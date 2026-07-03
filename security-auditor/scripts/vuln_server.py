# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastmcp>=2.0",
#   "httpx>=0.27",
# ]
# ///

import asyncio
import os
import time
from typing import Any, Optional

import httpx
from fastmcp import FastMCP

mcp = FastMCP("vuln-lookup")

# --- Configuration ---
NVD_API_KEY = os.getenv("NVD_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

NVD_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
OSV_BASE = "https://api.osv.dev/v1"
CWE_API_BASE = "https://cwe-api.mitre.org/api/v1/cwe"
GITHUB_GRAPHQL = "https://api.github.com/graphql"

# --- In-memory cache ---
_cache: dict[str, tuple[Any, float]] = {}
CACHE_TTL = 600  # 10 minutes


def _cache_get(key: str) -> Optional[Any]:
    if key in _cache:
        data, ts = _cache[key]
        if time.monotonic() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None


def _cache_set(key: str, data: Any) -> None:
    _cache[key] = (data, time.monotonic())


# --- NVD rate limiter ---
# Without API key: 5 requests / 30 seconds
# With API key:   50 requests / 30 seconds
class _TokenBucket:
    def __init__(self, capacity: int, refill_period: float):
        self.capacity = capacity
        self.refill_period = refill_period
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock: asyncio.Lock | None = None  # lazy: created on first use inside event loop

    async def acquire(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            if elapsed >= self.refill_period:
                self._tokens = self.capacity
                self._last_refill = now
            if self._tokens <= 0:
                wait = self.refill_period - elapsed
                await asyncio.sleep(max(wait, 0))
                self._tokens = self.capacity
                self._last_refill = time.monotonic()
            self._tokens -= 1


_nvd_limiter = _TokenBucket(
    capacity=50 if NVD_API_KEY else 5,
    refill_period=30.0,
)


# --- NVD helpers ---
def _nvd_headers() -> dict:
    return {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}


def _parse_nvd_item(item: dict) -> dict:
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


def _parse_osv_vuln(v: dict) -> dict:
    aliases = v.get("aliases", [])
    cve_ids = [a for a in aliases if a.startswith("CVE-")]
    severity = v.get("severity", [])
    cvss_score = None
    if severity:
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


# --- MCP Tools ---

@mcp.tool()
async def get_cve(cve_id: str) -> dict:
    """Look up a specific CVE by ID from NVD. Returns CVSS score, severity, description, and CWEs."""
    cve_id = cve_id.upper().strip()
    key = f"cve:{cve_id}"
    if (cached := _cache_get(key)) is not None:
        return cached

    await _nvd_limiter.acquire()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(NVD_BASE, headers=_nvd_headers(), params={"cveId": cve_id})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return {"found": False, "cve_id": cve_id, "error": f"NVD HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except httpx.RequestError as e:
        return {"found": False, "cve_id": cve_id, "error": f"NVD request failed: {e}"}

    vulns = data.get("vulnerabilities", [])
    if not vulns:
        result = {"found": False, "cve_id": cve_id, "error": "CVE not found in NVD"}
    else:
        result = {"found": True, **_parse_nvd_item(vulns[0])}

    _cache_set(key, result)
    return result


@mcp.tool()
async def search_cve(keyword: str, limit: int = 10) -> dict:
    """Search CVEs by keyword from NVD. Returns a list of matching CVEs with CVSS scores."""
    limit = min(max(1, limit), 20)
    key = f"search:{keyword}:{limit}"
    if (cached := _cache_get(key)) is not None:
        return cached

    await _nvd_limiter.acquire()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                NVD_BASE,
                headers=_nvd_headers(),
                params={"keywordSearch": keyword, "resultsPerPage": limit},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return {"keyword": keyword, "error": f"NVD HTTP {e.response.status_code}: {e.response.text[:200]}", "vulnerabilities": []}
    except httpx.RequestError as e:
        return {"keyword": keyword, "error": f"NVD request failed: {e}", "vulnerabilities": []}

    results = [_parse_nvd_item(v) for v in data.get("vulnerabilities", [])]
    result = {
        "keyword": keyword,
        "total_results": data.get("totalResults", 0),
        "returned": len(results),
        "vulnerabilities": results,
    }
    _cache_set(key, result)
    return result


@mcp.tool()
async def query_osv(ecosystem: str, package: str, version: str) -> dict:
    """Query OSV.dev for vulnerabilities affecting a specific package version.

    Ecosystem values: npm, PyPI, Go, Maven, crates.io, Packagist, RubyGems, NuGet, Hex
    For Maven, use groupId:artifactId format for package name.
    """
    key = f"osv:{ecosystem}:{package}:{version}"
    if (cached := _cache_get(key)) is not None:
        return cached

    payload = {
        "version": version,
        "package": {"name": package, "ecosystem": ecosystem},
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(f"{OSV_BASE}/query", json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return {"package": package, "version": version, "ecosystem": ecosystem,
                "error": f"OSV HTTP {e.response.status_code}: {e.response.text[:200]}", "vulnerabilities": []}
    except httpx.RequestError as e:
        return {"package": package, "version": version, "ecosystem": ecosystem,
                "error": f"OSV request failed: {e}", "vulnerabilities": []}

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


@mcp.tool()
async def get_cwe(cwe_id: str) -> dict:
    """Look up CWE details from MITRE CWE API, with fallback to a local dictionary."""
    clean_id = cwe_id.upper().replace("CWE-", "").strip()
    key = f"cwe:{clean_id}"
    if (cached := _cache_get(key)) is not None:
        return cached

    # Try MITRE API first
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{CWE_API_BASE}/{clean_id}")
            if resp.status_code == 200:
                data = resp.json()
                # MITRE API may return a list or dict depending on version
                item = data[0] if isinstance(data, list) else data
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

    # Fallback: local dictionary of 35 most common CWEs
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


@mcp.tool()
async def get_advisory(package: str, ecosystem: str) -> dict:
    """Query GitHub Advisory Database for package vulnerabilities (requires GITHUB_TOKEN env var)."""
    if not GITHUB_TOKEN:
        return {
            "error": "GITHUB_TOKEN environment variable not set",
            "hint": "Set GITHUB_TOKEN to enable GitHub Advisory Database queries",
            "advisories": [],
        }

    key = f"ghsa:{ecosystem}:{package}"
    if (cached := _cache_get(key)) is not None:
        return cached

    gh_ecosystem_map = {
        "npm": "NPM",
        "pypi": "PIP",
        "pip": "PIP",
        "maven": "MAVEN",
        "go": "GO",
        "cargo": "RUST",
        "crates.io": "RUST",
        "rubygems": "RUBYGEMS",
        "nuget": "NUGET",
        "composer": "COMPOSER",
        "packagist": "COMPOSER",
        "hex": "ERLANG",
    }
    gh_ecosystem = gh_ecosystem_map.get(ecosystem.lower(), ecosystem.upper())

    query = """
    query($package: String!, $ecosystem: SecurityAdvisoryEcosystem!) {
      securityVulnerabilities(first: 10, ecosystem: $ecosystem, package: $package,
                               orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          advisory {
            ghsaId
            summary
            severity
            cvss { score vectorString }
            publishedAt
            updatedAt
          }
          vulnerableVersionRange
          firstPatchedVersion { identifier }
        }
      }
    }
    """

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                GITHUB_GRAPHQL,
                json={"query": query, "variables": {"package": package, "ecosystem": gh_ecosystem}},
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return {"package": package, "ecosystem": ecosystem,
                "error": f"GitHub API HTTP {e.response.status_code}: {e.response.text[:200]}", "advisories": []}
    except httpx.RequestError as e:
        return {"package": package, "ecosystem": ecosystem,
                "error": f"GitHub API request failed: {e}", "advisories": []}

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


# --- CWE Fallback Dictionary ---
_CWE_FALLBACK: dict[str, dict] = {
    "20":   {"id": "CWE-20",   "name": "Improper Input Validation",                    "url": "https://cwe.mitre.org/data/definitions/20.html",   "description": "The product receives input or data, but it does not validate that the input has the properties that are required to process the data safely."},
    "22":   {"id": "CWE-22",   "name": "Path Traversal",                               "url": "https://cwe.mitre.org/data/definitions/22.html",   "description": "The software uses external input to construct a pathname but does not properly neutralize special elements that can cause the path to resolve outside the restricted directory."},
    "78":   {"id": "CWE-78",   "name": "OS Command Injection",                         "url": "https://cwe.mitre.org/data/definitions/78.html",   "description": "The software constructs all or part of an OS command using externally-influenced input."},
    "79":   {"id": "CWE-79",   "name": "Cross-Site Scripting (XSS)",                   "url": "https://cwe.mitre.org/data/definitions/79.html",   "description": "The software does not neutralize user-controllable input before it is placed in output used as a web page."},
    "89":   {"id": "CWE-89",   "name": "SQL Injection",                                "url": "https://cwe.mitre.org/data/definitions/89.html",   "description": "The software constructs all or part of an SQL command using externally-influenced input."},
    "94":   {"id": "CWE-94",   "name": "Code Injection",                               "url": "https://cwe.mitre.org/data/definitions/94.html",   "description": "The software constructs all or part of a code segment using externally-influenced input."},
    "98":   {"id": "CWE-98",   "name": "PHP Remote File Inclusion",                    "url": "https://cwe.mitre.org/data/definitions/98.html",   "description": "The PHP application does not restrict input before using it in require/include functions."},
    "117":  {"id": "CWE-117",  "name": "Log Injection",                                "url": "https://cwe.mitre.org/data/definitions/117.html",  "description": "Failure to sanitize log entries allows attackers to forge log entries or inject malicious content."},
    "190":  {"id": "CWE-190",  "name": "Integer Overflow",                             "url": "https://cwe.mitre.org/data/definitions/190.html",  "description": "The software performs a calculation that can produce an integer overflow when the logic assumes the result will always be larger than the initial value."},
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
    mcp.run()
