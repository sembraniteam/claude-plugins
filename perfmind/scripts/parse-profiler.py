#!/usr/bin/env python3
"""Parse a profiler artifact into a normalized top-N JSON structure.

Supported formats:
  cpuprofile  - Chrome DevTools / Node.js --cpu-prof (.cpuprofile) CPU profile
  pprof-top   - text output of `go tool pprof -top <profile>`
  pg-explain  - PostgreSQL `EXPLAIN (ANALYZE, FORMAT JSON)` output

Usage:
  parse-profiler.py <file|-> [--format cpuprofile|pprof-top|pg-explain] [--top N]

Output is always a single JSON object on stdout. Errors go to stderr with a
non-zero exit code; nothing is guessed silently on malformed input.
"""

import argparse
import json
import re
import sys


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        fail(f"Cannot read '{path}': {e}")


def fail(message: str):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def detect_format(text: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            fail(
                "Input looks like JSON but failed to parse. Pass --format explicitly "
                "if this is a truncated or non-standard file."
            )
        root = data[0] if isinstance(data, list) and data else data
        if isinstance(root, dict) and "nodes" in root and "samples" in root:
            return "cpuprofile"
        if isinstance(root, dict) and "Plan" in root:
            return "pg-explain"
        fail(
            "Input is valid JSON but does not match a known format (expected "
            "'nodes'+'samples' for cpuprofile, or 'Plan' for pg-explain). "
            "Pass --format explicitly."
        )
    for line in stripped.splitlines()[:30]:
        if re.search(r"\bflat\b.*\bcum\b", line) or "Showing nodes accounting for" in line:
            return "pprof-top"
    fail(
        "Could not auto-detect the profiler format from the input. "
        "Pass --format explicitly: cpuprofile, pprof-top, or pg-explain."
    )


# --- Chrome / Node.js .cpuprofile -------------------------------------------


def parse_cpuprofile(text: str, top_n: int) -> dict:
    data = json.loads(text)
    if isinstance(data, list):
        data = data[0]

    nodes = data.get("nodes", [])
    samples = data.get("samples", [])
    start_time = data.get("startTime")
    end_time = data.get("endTime")

    if not nodes:
        fail("cpuprofile has no 'nodes' array — nothing to parse.")

    by_id = {n["id"]: n for n in nodes}
    children_of = {n["id"]: n.get("children", []) for n in nodes}

    # Self/cumulative hits below are always computed from node hitCount, so the
    # denominator must come from the same accounting system — the top-level
    # `samples` array is not guaranteed to sum to the same total (it records
    # per-tick node ids for stack reconstruction, a different bookkeeping
    # scheme than hitCount's self-time aggregate) and mixing the two would
    # silently skew every percentage. Only fall back to len(samples) if no
    # node reports a hitCount at all, so there is still something to divide by.
    total_hit_count = sum(n.get("hitCount", 0) for n in nodes)
    total_samples = total_hit_count if total_hit_count else len(samples)
    if total_samples == 0:
        fail("Profile has zero samples — cannot compute time percentages.")

    duration_ms = None
    if start_time is not None and end_time is not None:
        duration_ms = (end_time - start_time) / 1000.0
    ms_per_sample = (duration_ms / total_samples) if duration_ms else None

    # The cumulative-time aggregation below relies on a genuine tree property:
    # a DFS preorder always places a node strictly before every one of its
    # descendants, which is what makes reversed(preorder) a valid post-order
    # (children processed before parents) without needing an explicit
    # post-order implementation. That property only holds if every node has
    # at most one parent — a node listed as a child of two different parents
    # would be visited (and marked "done") via whichever parent's turn comes
    # first, silently starving the other parent's cumulative sum of that
    # child's hits. Validate this up front rather than let it corrupt output.
    child_counts = {}
    for kids in children_of.values():
        for c in kids:
            child_counts[c] = child_counts.get(c, 0) + 1
    shared = [node_id for node_id, count in child_counts.items() if count > 1]
    if shared:
        fail(
            f"Call tree is malformed: node id(s) {shared[:5]} are listed as a child of more than one "
            "parent, which is not a valid call tree. Refusing to compute cumulative time against it."
        )

    # Post-order traversal (iterative, to avoid recursion-depth issues on deep
    # call stacks) to compute cumulative hitCount per node id.
    cum_hits = {}
    root_ids = [n["id"] for n in nodes if n["id"] not in child_counts]
    visited = set()
    stack = list(root_ids) or [nodes[0]["id"]]
    order = []
    while stack:
        node_id = stack.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        order.append(node_id)
        stack.extend(children_of.get(node_id, []))
    if len(order) != len(nodes):
        fail(
            f"Call tree is malformed: reached {len(order)} of {len(nodes)} nodes from the root(s) — "
            "the tree may be disconnected, or contain a cycle. Refusing to compute cumulative time against it."
        )
    for node_id in reversed(order):
        node = by_id[node_id]
        cum = node.get("hitCount", 0)
        for child_id in children_of.get(node_id, []):
            cum += cum_hits.get(child_id, 0)
        cum_hits[node_id] = cum

    # Aggregate by function identity — the same function can appear at
    # multiple call sites / recursion depths as distinct node ids.
    agg = {}
    for node in nodes:
        cf = node.get("callFrame", {})
        key = (cf.get("functionName") or "(anonymous)", cf.get("url", ""), cf.get("lineNumber", -1))
        entry = agg.setdefault(
            key,
            {"name": key[0], "location": f"{key[1]}:{key[2] + 1}" if key[1] else None, "self_hits": 0, "cum_hits": 0},
        )
        entry["self_hits"] += node.get("hitCount", 0)
        entry["cum_hits"] += cum_hits.get(node["id"], 0)

    ranked = sorted(agg.values(), key=lambda e: e["self_hits"], reverse=True)
    top = []
    for i, e in enumerate(ranked[:top_n], start=1):
        top.append(
            {
                "rank": i,
                "name": e["name"],
                "location": e["location"],
                "self_pct": round(100 * e["self_hits"] / total_samples, 2),
                "self_time_ms": round(e["self_hits"] * ms_per_sample, 3) if ms_per_sample else None,
                "total_pct": round(100 * e["cum_hits"] / total_samples, 2),
                "total_time_ms": round(e["cum_hits"] * ms_per_sample, 3) if ms_per_sample else None,
                "extra": {"self_hit_count": e["self_hits"], "cum_hit_count": e["cum_hits"]},
            }
        )

    return {
        "format": "cpuprofile",
        "summary": {
            "total_samples": total_samples,
            "duration_ms": round(duration_ms, 3) if duration_ms else None,
            "distinct_functions": len(agg),
        },
        "top": top,
    }


# --- `go tool pprof -top` text ----------------------------------------------

_PPROF_ROW = re.compile(
    r"^\s*(?P<flat>[\d.]+\w*)\s+(?P<flat_pct>[\d.]+)%\s+(?P<sum_pct>[\d.]+)%\s+"
    r"(?P<cum>[\d.]+\w*)\s+(?P<cum_pct>[\d.]+)%\s+(?P<name>.+?)\s*$"
)
_PPROF_HEADER = re.compile(r"^\s*flat\s+flat%\s+sum%\s+cum\s+cum%\s*$")
_PPROF_META = re.compile(r"^(File|Type|Time|Duration):\s*(.+)$")

# Both the micro sign (µ, U+00B5) and the Greek small letter mu (μ, U+03BC)
# render identically as "µs"/"μs" and both appear in the wild depending on
# which Go toolchain/locale produced the pprof output — accept either.
_TIME_UNIT_MS = {"ns": 1e-6, "us": 1e-3, "µs": 1e-3, "μs": 1e-3, "ms": 1.0, "s": 1000.0}


def _parse_value_unit(raw: str):
    m = re.match(r"^([\d.]+)([a-zµμ]*)$", raw)
    if not m:
        return None, None
    value, unit = float(m.group(1)), m.group(2)
    if unit in _TIME_UNIT_MS:
        return round(value * _TIME_UNIT_MS[unit], 3), "ms"
    return value, unit or None


def parse_pprof_top(text: str, top_n: int) -> dict:
    lines = text.splitlines()
    meta = {}
    showing_line = None
    rows = []
    header_seen = False

    for line in lines:
        m = _PPROF_META.match(line.strip())
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
            continue
        if "Showing nodes accounting for" in line:
            showing_line = line.strip()
            continue
        if _PPROF_HEADER.match(line):
            header_seen = True
            continue
        if not header_seen:
            continue
        m = _PPROF_ROW.match(line)
        if m:
            rows.append(m.groupdict())

    if not rows:
        fail(
            "No data rows found under the 'flat  flat%  sum%  cum  cum%' header. "
            "Make sure this is the output of `go tool pprof -top`, not an interactive session."
        )

    rows.sort(key=lambda r: float(r["flat_pct"]), reverse=True)
    top = []
    for i, r in enumerate(rows[:top_n], start=1):
        flat_ms, flat_unit = _parse_value_unit(r["flat"])
        cum_ms, cum_unit = _parse_value_unit(r["cum"])
        top.append(
            {
                "rank": i,
                "name": r["name"],
                "location": None,
                "self_pct": float(r["flat_pct"]),
                "self_time_ms": flat_ms if flat_unit == "ms" else None,
                "total_pct": float(r["cum_pct"]),
                "total_time_ms": cum_ms if cum_unit == "ms" else None,
                "extra": {
                    "flat_raw": r["flat"],
                    "cum_raw": r["cum"],
                    "sum_pct": float(r["sum_pct"]),
                },
            }
        )

    return {
        "format": "pprof-top",
        "summary": {**meta, "showing_line": showing_line, "rows_parsed": len(rows)},
        "top": top,
    }


# --- PostgreSQL EXPLAIN (ANALYZE, FORMAT JSON) ------------------------------


def parse_pg_explain(text: str, top_n: int) -> dict:
    data = json.loads(text)
    root = data[0] if isinstance(data, list) else data
    plan = root.get("Plan")
    if plan is None:
        fail("No 'Plan' key found — is this EXPLAIN (ANALYZE, FORMAT JSON) output?")
    if "Actual Total Time" not in plan:
        fail("Plan has no 'Actual Total Time' — EXPLAIN must be run with ANALYZE, not just EXPLAIN.")

    nodes = []

    # Plain recursion is fine here, unlike the cpuprofile call tree above: a
    # query plan's depth is bounded by join/CTE/subquery nesting in the SQL
    # itself, which stays well under Python's default recursion limit for any
    # realistic query. A CPU call tree has no such natural ceiling.
    def walk(node, depth):
        loops = node.get("Actual Loops", 1) or 1
        total_ms = node.get("Actual Total Time", 0.0) * loops
        children = node.get("Plans", [])
        children_total_ms = sum((c.get("Actual Total Time", 0.0) * (c.get("Actual Loops", 1) or 1)) for c in children)
        self_ms = max(total_ms - children_total_ms, 0.0)

        label = node.get("Relation Name") or node.get("Index Name") or node.get("CTE Name")
        nodes.append(
            {
                "node_type": node.get("Node Type"),
                "label": label,
                "depth": depth,
                "self_time_ms": round(self_ms, 3),
                "total_time_ms": round(total_ms, 3),
                "actual_rows": node.get("Actual Rows"),
                "plan_rows": node.get("Plan Rows"),
                "actual_loops": loops,
                "filter": node.get("Filter"),
                "rows_removed_by_filter": node.get("Rows Removed by Filter"),
                "index_condition": node.get("Index Cond"),
            }
        )
        for c in children:
            walk(c, depth + 1)

    walk(plan, 0)

    total_query_ms = root.get("Execution Time")
    ranked = sorted(nodes, key=lambda n: n["self_time_ms"], reverse=True)
    top = []
    for i, n in enumerate(ranked[:top_n], start=1):
        self_pct = round(100 * n["self_time_ms"] / total_query_ms, 2) if total_query_ms else None
        est_vs_actual = None
        if n["plan_rows"] not in (None, 0) and n["actual_rows"] is not None:
            est_vs_actual = round(n["actual_rows"] / n["plan_rows"], 2)
        top.append(
            {
                "rank": i,
                "name": n["node_type"],
                "location": n["label"],
                "self_pct": self_pct,
                "self_time_ms": n["self_time_ms"],
                "total_pct": round(100 * n["total_time_ms"] / total_query_ms, 2) if total_query_ms else None,
                "total_time_ms": n["total_time_ms"],
                "extra": {
                    "depth": n["depth"],
                    "actual_rows": n["actual_rows"],
                    "plan_rows": n["plan_rows"],
                    "actual_vs_estimated_rows_ratio": est_vs_actual,
                    "actual_loops": n["actual_loops"],
                    "filter": n["filter"],
                    "rows_removed_by_filter": n["rows_removed_by_filter"],
                    "index_condition": n["index_condition"],
                },
            }
        )

    return {
        "format": "pg-explain",
        "summary": {
            "planning_time_ms": root.get("Planning Time"),
            "execution_time_ms": root.get("Execution Time"),
            "total_plan_nodes": len(nodes),
        },
        "top": top,
    }


PARSERS = {
    "cpuprofile": parse_cpuprofile,
    "pprof-top": parse_pprof_top,
    "pg-explain": parse_pg_explain,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="Profiler artifact path, or '-' to read stdin")
    ap.add_argument("--format", choices=sorted(PARSERS), default=None, help="Skip auto-detection")
    ap.add_argument("--top", type=int, default=15, help="Number of entries to return (default: 15)")
    args = ap.parse_args()

    if args.top < 1:
        fail("--top must be a positive integer.")

    text = read_input(args.path)
    if not text.strip():
        fail("Input is empty.")

    fmt = args.format or detect_format(text)

    try:
        result = PARSERS[fmt](text, args.top)
    except json.JSONDecodeError as e:
        fail(f"Malformed JSON for format '{fmt}': {e}")

    result["source"] = args.path
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
