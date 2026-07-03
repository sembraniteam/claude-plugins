#!/usr/bin/env python3
"""
vuln-lookup MCP server — stdlib only, no external dependencies.
Implements the MCP stdio transport with JSON-RPC 2.0.
"""
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# --- Configuration ---
NVD_API_KEY = os.getenv("NVD_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

NVD_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
OSV_BASE = "https://api.osv.dev/v1"
CWE_API_BASE = "https://cwe-api.mitre.org/api/v1/cwe/weakness"
GITHUB_GRAPHQL = "https://api.github.com/graphql"
EPSS_BASE = "https://api.first.org/data/v1/epss"
KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
KEV_CATALOG_TTL = 21600  # 6 hours — CISA updates the catalog roughly once a day

# --- In-memory cache ---
_cache: Dict[str, tuple] = {}
CACHE_TTL = 600


def _cache_get(key: str) -> Optional[Any]:
    if key in _cache:
        data, ts = _cache[key]
        if time.monotonic() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _cache_set(key: str, data: Any) -> None:
    _cache[key] = (data, time.monotonic())


def _cache_get_ex(key: str, ttl: float) -> Optional[Any]:
    """Cache lookup with a custom TTL (in seconds), for entries that should outlive CACHE_TTL."""
    if key in _cache:
        data, ts = _cache[key]
        if time.monotonic() - ts < ttl:
            return data
        del _cache[key]
    return None


# --- NVD rate limiter ---
_nvd_lock = threading.Lock()
_nvd_capacity = 50 if NVD_API_KEY else 5
_nvd_tokens = _nvd_capacity
_nvd_last_refill = time.monotonic()


def _nvd_acquire() -> None:
    global _nvd_tokens, _nvd_last_refill
    with _nvd_lock:
        now = time.monotonic()
        elapsed = now - _nvd_last_refill
        if elapsed >= 30.0:
            _nvd_tokens = _nvd_capacity
            _nvd_last_refill = now
        if _nvd_tokens <= 0:
            wait = 30.0 - elapsed
            if wait > 0:
                time.sleep(wait)
            _nvd_tokens = _nvd_capacity
            _nvd_last_refill = time.monotonic()
        _nvd_tokens -= 1


# --- HTTP helpers ---
def _http_get(url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}")


def _http_post(url: str, data: Any, headers: Optional[Dict] = None) -> Any:
    body = json.dumps(data).encode()
    all_headers = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=body, headers=all_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}")


# --- NVD parse helpers ---
def _nvd_headers() -> Dict:
    return {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}


def _parse_nvd_item(item: Dict) -> Dict:
    cve = item.get("cve", {})
    cve_id = cve.get("id", "unknown")
    metrics = cve.get("metrics", {})
    cvss_score = None
    severity = None
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        entries = metrics.get(key)
        if entries:
            m = entries[0]
            cvss_data = m.get("cvssData", {})
            cvss_score = cvss_data.get("baseScore")
            severity = m.get("baseSeverity") or cvss_data.get("baseSeverity")
            break
    descs = cve.get("descriptions", [])
    description = next((d["value"] for d in descs if d.get("lang") == "en"), "")
    weaknesses = cve.get("weaknesses", [])
    cwes = []
    for w in weaknesses:
        for desc in w.get("description", []):
            val = desc.get("value", "")
            if val.startswith("CWE-"):
                cwes.append(val)
    return {
        "cve_id": cve_id,
        "description": description[:600],
        "cvss_score": cvss_score,
        "severity": severity,
        "cwes": cwes,
        "published": cve.get("published", ""),
        "modified": cve.get("lastModified", ""),
        "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
    }


def _parse_osv_vuln(v: Dict) -> Dict:
    aliases = v.get("aliases", [])
    cve_ids = [a for a in aliases if a.startswith("CVE-")]
    severity = v.get("severity", [])
    cvss_score = None
    for preferred_type in ("CVSS_V4", "CVSS_V3", "CVSS_V2"):
        for s in severity:
            if s.get("type") == preferred_type:
                cvss_score = s.get("score")
                break
        if cvss_score is not None:
            break
    affected = v.get("affected", [])
    ranges = []
    for pkg in affected:
        for r in pkg.get("ranges", []):
            for evt in r.get("events", []):
                if "fixed" in evt:
                    ranges.append(evt["fixed"])
    return {
        "osv_id": v.get("id", ""),
        "cve_ids": cve_ids,
        "summary": v.get("summary", ""),
        "cvss_score": cvss_score,
        "fixed_versions": list(set(ranges)),
        "published": v.get("published", ""),
    }


# --- MCP tool implementations ---

def get_cve(cve_id: str) -> Dict:
    """Look up a specific CVE by ID from NVD. Returns CVSS score, severity, description, and CWEs."""
    cve_id = cve_id.upper().strip()
    key = f"cve:{cve_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    _nvd_acquire()
    try:
        data = _http_get(NVD_BASE, headers=_nvd_headers(), params={"cveId": cve_id})
    except Exception as e:
        return {"found": False, "cve_id": cve_id, "error": str(e)}
    vulns = data.get("vulnerabilities", [])
    result = (
        {"found": False, "cve_id": cve_id, "error": "CVE not found in NVD"}
        if not vulns
        else {"found": True, **_parse_nvd_item(vulns[0])}
    )
    _cache_set(key, result)
    return result


def search_cve(keyword: str, limit: int = 10) -> Dict:
    """Search CVEs by keyword from NVD. Returns a list of matching CVEs with CVSS scores."""
    limit = min(max(1, limit), 20)
    key = f"search:{keyword}:{limit}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    _nvd_acquire()
    try:
        data = _http_get(NVD_BASE, headers=_nvd_headers(), params={"keywordSearch": keyword, "resultsPerPage": limit})
    except Exception as e:
        return {"keyword": keyword, "error": str(e), "vulnerabilities": []}
    results = [_parse_nvd_item(v) for v in data.get("vulnerabilities", [])]
    result = {
        "keyword": keyword,
        "total_results": data.get("totalResults", 0),
        "returned": len(results),
        "vulnerabilities": results,
    }
    _cache_set(key, result)
    return result


def query_osv(ecosystem: str, package: str, version: str) -> Dict:
    """Query OSV.dev for vulnerabilities affecting a specific package version.

    Ecosystem values: npm, PyPI, Go, Maven, crates.io, Packagist, RubyGems, NuGet, Hex
    For Maven, use groupId:artifactId format for package name.
    """
    key = f"osv:{ecosystem}:{package}:{version}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    payload = {"version": version, "package": {"name": package, "ecosystem": ecosystem}}
    try:
        data = _http_post(f"{OSV_BASE}/query", data=payload)
    except Exception as e:
        return {"package": package, "version": version, "ecosystem": ecosystem, "error": str(e), "vulnerabilities": []}
    vulns = data.get("vulns", [])
    parsed = [_parse_osv_vuln(v) for v in vulns]
    result = {
        "package": package,
        "version": version,
        "ecosystem": ecosystem,
        "vulnerability_count": len(parsed),
        "vulnerabilities": parsed,
        "source": "OSV.dev",
    }
    _cache_set(key, result)
    return result


def get_cwe(cwe_id: str) -> Dict:
    """Look up CWE details from MITRE CWE API, with fallback to a local dictionary."""
    clean_id = cwe_id.upper().replace("CWE-", "").strip()
    key = f"cwe:{clean_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    try:
        data = _http_get(f"{CWE_API_BASE}/{clean_id}")
        weaknesses = data.get("Weaknesses", data if isinstance(data, list) else [data])
        item = weaknesses[0]
        result = {
            "id": f"CWE-{clean_id}",
            "name": item.get("Name", item.get("name", "")),
            "description": item.get("Description", item.get("description", ""))[:500],
            "url": f"https://cwe.mitre.org/data/definitions/{clean_id}.html",
            "source": "MITRE CWE API",
        }
        _cache_set(key, result)
        return result
    except Exception:
        pass
    fallback = _CWE_FALLBACK.get(clean_id)
    if fallback:
        result = {**fallback, "source": "local-fallback"}
        _cache_set(key, result)
        return result
    return {
        "id": f"CWE-{clean_id}",
        "name": "Unknown",
        "description": "CWE details not available. See MITRE website.",
        "url": f"https://cwe.mitre.org/data/definitions/{clean_id}.html",
        "source": "not-found",
    }


def get_advisory(package: str, ecosystem: str) -> Dict:
    """Query GitHub Advisory Database for package vulnerabilities (requires GITHUB_TOKEN env var)."""
    if not GITHUB_TOKEN:
        return {
            "error": "GITHUB_TOKEN environment variable not set",
            "hint": "Set GITHUB_TOKEN to enable GitHub Advisory Database queries",
            "advisories": [],
        }
    key = f"ghsa:{ecosystem}:{package}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    gh_ecosystem_map = {
        "npm": "NPM", "pypi": "PIP", "pip": "PIP", "maven": "MAVEN", "go": "GO",
        "cargo": "RUST", "crates.io": "RUST", "rubygems": "RUBYGEMS", "nuget": "NUGET",
        "composer": "COMPOSER", "packagist": "COMPOSER", "hex": "ERLANG",
    }
    gh_ecosystem = gh_ecosystem_map.get(ecosystem.lower(), ecosystem.upper())
    query = """
    query($package: String!, $ecosystem: SecurityAdvisoryEcosystem!) {
      securityVulnerabilities(first: 10, ecosystem: $ecosystem, package: $package,
                               orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          advisory {
            ghsaId summary severity cvss { score vectorString } publishedAt updatedAt
          }
          vulnerableVersionRange
          firstPatchedVersion { identifier }
        }
      }
    }
    """
    try:
        data = _http_post(
            GITHUB_GRAPHQL,
            data={"query": query, "variables": {"package": package, "ecosystem": gh_ecosystem}},
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        )
    except Exception as e:
        return {"package": package, "ecosystem": ecosystem, "error": str(e), "advisories": []}
    nodes = data.get("data", {}).get("securityVulnerabilities", {}).get("nodes", [])
    advisories = []
    for n in nodes:
        adv = n.get("advisory", {})
        advisories.append({
            "ghsa_id": adv.get("ghsaId", ""),
            "summary": adv.get("summary", ""),
            "severity": adv.get("severity", ""),
            "cvss_score": adv.get("cvss", {}).get("score"),
            "cvss_vector": adv.get("cvss", {}).get("vectorString"),
            "vulnerable_range": n.get("vulnerableVersionRange", ""),
            "fixed_version": (n.get("firstPatchedVersion") or {}).get("identifier", "no fix available"),
            "published": adv.get("publishedAt", ""),
        })
    result = {
        "package": package,
        "ecosystem": ecosystem,
        "advisory_count": len(advisories),
        "advisories": advisories,
        "source": "GitHub Advisory Database",
    }
    _cache_set(key, result)
    return result


# --- EPSS / KEV ---

_kev_lock = threading.Lock()


def _load_kev_catalog() -> Dict[str, Dict]:
    """Download and index the CISA KEV catalog, cached for KEV_CATALOG_TTL seconds."""
    catalog_key = "kev:__catalog__"
    cached = _cache_get_ex(catalog_key, KEV_CATALOG_TTL)
    if cached is not None:
        return cached
    with _kev_lock:
        cached = _cache_get_ex(catalog_key, KEV_CATALOG_TTL)
        if cached is not None:
            return cached
        data = _http_get(KEV_URL)
        vulns = data.get("vulnerabilities", [])
        index = {v["cveID"]: v for v in vulns if "cveID" in v}
        _cache[catalog_key] = (index, time.monotonic())
        return index


def get_epss(cve_id: str) -> Dict:
    """Get EPSS (Exploit Prediction Scoring System) probability for a CVE from FIRST.org.

    EPSS estimates the probability (0–1) that a CVE will be exploited in the next 30 days.
    Scores update daily; values above ~0.10 warrant elevated remediation priority.
    """
    cve_id = cve_id.upper().strip()
    key = f"epss:{cve_id}"
    cached = _cache_get_ex(key, 86400)  # 24h — matches EPSS daily update cadence
    if cached is not None:
        return cached
    try:
        data = _http_get(EPSS_BASE, params={"cve": cve_id})
        entries = data.get("data", [])
        if entries:
            e = entries[0]
            score = float(e.get("epss", 0))
            result = {
                "cve_id": cve_id,
                "found": True,
                "epss_score": score,
                "percentile": float(e.get("percentile", 0)),
                "date": e.get("date", ""),
                "interpretation": f"{score * 100:.1f}% probability of exploitation in the next 30 days",
                "source": "FIRST.org EPSS",
            }
        else:
            result = {
                "cve_id": cve_id,
                "found": False,
                "epss_score": None,
                "source": "FIRST.org EPSS",
            }
    except Exception as exc:
        result = {"cve_id": cve_id, "error": str(exc), "epss_score": None}
    _cache_set(key, result)
    return result


def get_kev(cve_id: str) -> Dict:
    """Check if a CVE appears in the CISA Known Exploited Vulnerabilities (KEV) catalog.

    KEV entries represent vulnerabilities with confirmed active exploitation.
    Presence in KEV is the strongest available signal that a CVE needs immediate remediation.
    """
    cve_id = cve_id.upper().strip()
    key = f"kev:{cve_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    try:
        catalog = _load_kev_catalog()
        entry = catalog.get(cve_id)
        if entry:
            result = {
                "cve_id": cve_id,
                "in_kev": True,
                "vendor": entry.get("vendorProject", ""),
                "product": entry.get("product", ""),
                "vulnerability_name": entry.get("vulnerabilityName", ""),
                "date_added": entry.get("dateAdded", ""),
                "due_date": entry.get("dueDate", ""),
                "required_action": entry.get("requiredAction", ""),
                "known_ransomware": entry.get("knownRansomwareCampaignUse", "") == "Known",
                "source": "CISA KEV",
            }
        else:
            result = {
                "cve_id": cve_id,
                "in_kev": False,
                "catalog_size": len(catalog),
                "source": "CISA KEV",
            }
    except Exception as exc:
        result = {"cve_id": cve_id, "error": str(exc), "in_kev": None}
    _cache_set(key, result)
    return result


# --- MCP protocol ---

_TOOLS = [
    {
        "name": "get_cve",
        "description": "Look up a specific CVE by ID from NVD. Returns CVSS score, severity, description, and CWEs.",
        "inputSchema": {
            "type": "object",
            "properties": {"cve_id": {"type": "string", "description": "CVE ID, e.g. CVE-2021-44906"}},
            "required": ["cve_id"],
        },
    },
    {
        "name": "search_cve",
        "description": "Search CVEs by keyword from NVD. Returns a list of matching CVEs with CVSS scores.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "query_osv",
        "description": (
            "Query OSV.dev for vulnerabilities affecting a specific package version. "
            "Ecosystem values: npm, PyPI, Go, Maven, crates.io, Packagist, RubyGems, NuGet, Hex. "
            "For Maven, use groupId:artifactId format for package name."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ecosystem": {"type": "string"},
                "package": {"type": "string"},
                "version": {"type": "string"},
            },
            "required": ["ecosystem", "package", "version"],
        },
    },
    {
        "name": "get_cwe",
        "description": "Look up CWE details from MITRE CWE API, with fallback to a local dictionary.",
        "inputSchema": {
            "type": "object",
            "properties": {"cwe_id": {"type": "string", "description": "CWE ID, e.g. CWE-89 or 89"}},
            "required": ["cwe_id"],
        },
    },
    {
        "name": "get_advisory",
        "description": "Query GitHub Advisory Database for package vulnerabilities (requires GITHUB_TOKEN env var).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package": {"type": "string"},
                "ecosystem": {"type": "string"},
            },
            "required": ["package", "ecosystem"],
        },
    },
    {
        "name": "get_epss",
        "description": (
            "Get EPSS (Exploit Prediction Scoring System) score for a CVE from FIRST.org. "
            "Returns the probability (0–1) of exploitation in the next 30 days and the percentile rank. "
            "Use after get_cve to enrich findings with real-world exploitability data."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"cve_id": {"type": "string", "description": "CVE ID, e.g. CVE-2021-44906"}},
            "required": ["cve_id"],
        },
    },
    {
        "name": "get_kev",
        "description": (
            "Check if a CVE is listed in the CISA Known Exploited Vulnerabilities (KEV) catalog. "
            "KEV membership means active exploitation has been confirmed in the wild — "
            "use this to escalate remediation priority for any CVE found in a dependency scan."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"cve_id": {"type": "string", "description": "CVE ID, e.g. CVE-2021-44906"}},
            "required": ["cve_id"],
        },
    },
]

_TOOL_FNS = {
    "get_cve": get_cve,
    "search_cve": search_cve,
    "query_osv": query_osv,
    "get_cwe": get_cwe,
    "get_advisory": get_advisory,
    "get_epss": get_epss,
    "get_kev": get_kev,
}


def _send(obj: Dict) -> None:
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _handle(msg: Dict) -> None:
    method = msg.get("method", "")
    params = msg.get("params") or {}
    id_ = msg.get("id")

    if method == "initialize":
        _send({"jsonrpc": "2.0", "id": id_, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "vuln-lookup", "version": "1.0.0"},
        }})
    elif method == "tools/list":
        _send({"jsonrpc": "2.0", "id": id_, "result": {"tools": _TOOLS}})
    elif method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments") or {}
        fn = _TOOL_FNS.get(name)
        if fn is None:
            _send({"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": f"Unknown tool: {name}"}})
            return
        try:
            result = fn(**args)
            _send({"jsonrpc": "2.0", "id": id_, "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
            }})
        except Exception as e:
            _send({"jsonrpc": "2.0", "id": id_, "error": {"code": -32603, "message": str(e)}})
    elif id_ is not None:
        _send({"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": f"Method not found: {method}"}})
    # Notifications (no id) need no response


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        _handle(msg)


# --- CWE fallback dictionary ---
_CWE_FALLBACK: Dict[str, Dict] = {
    "20":   {"id": "CWE-20",   "name": "Improper Input Validation",                    "url": "https://cwe.mitre.org/data/definitions/20.html",   "description": "The product receives input or data, but it does not validate that the input has the properties that are required to process the data safely."},
    "22":   {"id": "CWE-22",   "name": "Path Traversal",                               "url": "https://cwe.mitre.org/data/definitions/22.html",   "description": "The software uses external input to construct a pathname but does not properly neutralize special elements that can cause the path to resolve outside the restricted directory."},
    "78":   {"id": "CWE-78",   "name": "OS Command Injection",                         "url": "https://cwe.mitre.org/data/definitions/78.html",   "description": "The software constructs all or part of an OS command using externally-influenced input."},
    "79":   {"id": "CWE-79",   "name": "Cross-Site Scripting (XSS)",                   "url": "https://cwe.mitre.org/data/definitions/79.html",   "description": "The software does not neutralize user-controllable input before it is placed in output used as a web page."},
    "89":   {"id": "CWE-89",   "name": "SQL Injection",                                "url": "https://cwe.mitre.org/data/definitions/89.html",   "description": "The software constructs all or part of an SQL command using externally-influenced input."},
    "94":   {"id": "CWE-94",   "name": "Code Injection",                               "url": "https://cwe.mitre.org/data/definitions/94.html",   "description": "The software constructs all or part of a code segment using externally-influenced input."},
    "98":   {"id": "CWE-98",   "name": "PHP Remote File Inclusion",                    "url": "https://cwe.mitre.org/data/definitions/98.html",   "description": "The PHP application does not restrict input before using it in require/include functions."},
    "117":  {"id": "CWE-117",  "name": "Log Injection",                                "url": "https://cwe.mitre.org/data/definitions/117.html",  "description": "Failure to sanitize log entries allows attackers to forge log entries or inject malicious content."},
    "190":  {"id": "CWE-190",  "name": "Integer Overflow",                             "url": "https://cwe.mitre.org/data/definitions/190.html",  "description": "The software performs a calculation that can produce an integer overflow."},
    "200":  {"id": "CWE-200",  "name": "Exposure of Sensitive Information",            "url": "https://cwe.mitre.org/data/definitions/200.html",  "description": "The product exposes sensitive information to an actor not explicitly authorized to have access."},
    "209":  {"id": "CWE-209",  "name": "Information Exposure via Error Messages",      "url": "https://cwe.mitre.org/data/definitions/209.html",  "description": "The software generates an error message that includes sensitive information about its environment."},
    "287":  {"id": "CWE-287",  "name": "Improper Authentication",                      "url": "https://cwe.mitre.org/data/definitions/287.html",  "description": "When an actor claims a given identity, the software does not sufficiently prove the claim is correct."},
    "306":  {"id": "CWE-306",  "name": "Missing Authentication for Critical Function", "url": "https://cwe.mitre.org/data/definitions/306.html",  "description": "The software does not perform authentication for functionality that requires a provable user identity."},
    "311":  {"id": "CWE-311",  "name": "Missing Encryption of Sensitive Data",         "url": "https://cwe.mitre.org/data/definitions/311.html",  "description": "The software does not encrypt sensitive or critical information before storage or transmission."},
    "312":  {"id": "CWE-312",  "name": "Cleartext Storage of Sensitive Information",   "url": "https://cwe.mitre.org/data/definitions/312.html",  "description": "The application stores sensitive information in cleartext within a resource that might be accessible to another control sphere."},
    "321":  {"id": "CWE-321",  "name": "Use of Hard-coded Cryptographic Key",          "url": "https://cwe.mitre.org/data/definitions/321.html",  "description": "The use of a hard-coded cryptographic key significantly increases the possibility of compromised data."},
    "327":  {"id": "CWE-327",  "name": "Use of Broken or Risky Cryptographic Algorithm","url": "https://cwe.mitre.org/data/definitions/327.html", "description": "The use of a broken or risky cryptographic algorithm is an unnecessary risk that may result in the exposure of sensitive information."},
    "328":  {"id": "CWE-328",  "name": "Use of Weak Hash",                             "url": "https://cwe.mitre.org/data/definitions/328.html",  "description": "The product uses an algorithm that produces a digest that does not meet security expectations for a hash function."},
    "330":  {"id": "CWE-330",  "name": "Use of Insufficiently Random Values",          "url": "https://cwe.mitre.org/data/definitions/330.html",  "description": "The software may use insufficiently random numbers in a security context that depends on unpredictable numbers."},
    "352":  {"id": "CWE-352",  "name": "Cross-Site Request Forgery (CSRF)",            "url": "https://cwe.mitre.org/data/definitions/352.html",  "description": "The web application does not sufficiently verify whether a well-formed request was intentionally provided by the user."},
    "367":  {"id": "CWE-367",  "name": "TOCTOU Race Condition",                        "url": "https://cwe.mitre.org/data/definitions/367.html",  "description": "The software checks the state of a resource before using that resource, but the resource's state can change between the check and the use."},
    "400":  {"id": "CWE-400",  "name": "Uncontrolled Resource Consumption",            "url": "https://cwe.mitre.org/data/definitions/400.html",  "description": "The software does not properly restrict the size or amount of resources requested or influenced by an actor."},
    "434":  {"id": "CWE-434",  "name": "Unrestricted Upload of File with Dangerous Type","url": "https://cwe.mitre.org/data/definitions/434.html","description": "The software allows the attacker to upload files of dangerous types that can be automatically processed within the product's environment."},
    "476":  {"id": "CWE-476",  "name": "NULL Pointer Dereference",                     "url": "https://cwe.mitre.org/data/definitions/476.html",  "description": "A NULL pointer dereference occurs when the application dereferences a pointer that it expects to be valid, but is NULL."},
    "502":  {"id": "CWE-502",  "name": "Deserialization of Untrusted Data",            "url": "https://cwe.mitre.org/data/definitions/502.html",  "description": "The application deserializes untrusted data without sufficiently verifying that the resulting data will be valid."},
    "521":  {"id": "CWE-521",  "name": "Weak Password Requirements",                   "url": "https://cwe.mitre.org/data/definitions/521.html",  "description": "The software does not require that users should have strong passwords."},
    "601":  {"id": "CWE-601",  "name": "Open Redirect",                                "url": "https://cwe.mitre.org/data/definitions/601.html",  "description": "A web application accepts a user-controlled input that specifies a link to an external site and uses that link in a redirect."},
    "611":  {"id": "CWE-611",  "name": "XXE — XML External Entity Reference",          "url": "https://cwe.mitre.org/data/definitions/611.html",  "description": "The software processes an XML document that can contain XML entities with URIs that resolve to documents outside the intended sphere of control."},
    "639":  {"id": "CWE-639",  "name": "IDOR — Authorization Bypass via User-Controlled Key","url": "https://cwe.mitre.org/data/definitions/639.html","description": "The system's authorization functionality does not prevent one user from gaining access to another user's data."},
    "732":  {"id": "CWE-732",  "name": "Incorrect Permission Assignment for Critical Resource","url": "https://cwe.mitre.org/data/definitions/732.html","description": "The product specifies permissions for a security-critical resource in a way that allows unintended actors to read or modify it."},
    "798":  {"id": "CWE-798",  "name": "Use of Hard-coded Credentials",                "url": "https://cwe.mitre.org/data/definitions/798.html",  "description": "The software contains hard-coded credentials such as a password or cryptographic key."},
    "862":  {"id": "CWE-862",  "name": "Missing Authorization",                        "url": "https://cwe.mitre.org/data/definitions/862.html",  "description": "The software does not perform an authorization check when an actor attempts to access a resource or perform an action."},
    "863":  {"id": "CWE-863",  "name": "Incorrect Authorization",                      "url": "https://cwe.mitre.org/data/definitions/863.html",  "description": "The software performs an authorization check, but it does not correctly perform the check."},
    "915":  {"id": "CWE-915",  "name": "Mass Assignment",                              "url": "https://cwe.mitre.org/data/definitions/915.html",  "description": "The software receives input from an upstream component that specifies multiple attributes of an object, but it does not properly control which attributes are modified."},
    "918":  {"id": "CWE-918",  "name": "Server-Side Request Forgery (SSRF)",           "url": "https://cwe.mitre.org/data/definitions/918.html",  "description": "The web server receives a URL from an upstream component and retrieves the contents of this URL, but does not sufficiently ensure the request is sent to the expected destination."},
    "1021": {"id": "CWE-1021", "name": "Clickjacking — Improper Restriction of Rendered UI Layers","url": "https://cwe.mitre.org/data/definitions/1021.html","description": "The web application does not restrict or incorrectly restricts frame objects or UI layers that belong to another application or domain."},
}


if __name__ == "__main__":
    main()
