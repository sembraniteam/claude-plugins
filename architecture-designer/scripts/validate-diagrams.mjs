/**
 * Structural + syntactic validation for docs/architecture-designer/diagrams.json.
 * Usage: node scripts/validate-diagrams.mjs
 *
 * Two-tier parsing strategy:
 *   - Legacy types (flowchart, ERD, sequence, C4, class, state, gantt, etc.)
 *     → mermaid package (Jison-based parsers) via jsdom DOM shim in Node.js
 *   - New types (architecture-beta)
 *     → @mermaid-js/parser (Langium-based)
 *   - When parsers are unavailable (node_modules missing): heuristic checks;
 *     passing diagrams are marked "✓ (heuristics only)" to be honest about coverage
 *
 * Each diagram's `code` field is normalized before parsing (BOM stripped, CRLF/CR
 * unified to LF, trailing per-line whitespace removed) — see normalizeCode().
 *
 * Also checks the `indexPlan` contract on ERD entries: every row must carry all five
 * keys (name, table, columns, type, reason). This catches the field being filled with
 * entity descriptions or other ERD notes instead of actual index rows.
 *
 * Requires: run `npm install` in the scripts/ directory once before first use.
 * The script degrades gracefully if dependencies are missing — it will not crash.
 *
 * Exit 0 → all pass.  Exit 1 → one or more failures.
 */

import fs from 'fs';
import path from 'path';

// ── Parser routing tables ─────────────────────────────────────────────────────

// @mermaid-js/parser (Langium) supports new types; its "Unknown diagram type"
// error for legacy types is NOT a real validation signal — use mermaid core instead.
const LEGACY_TYPES = new Set([
    'flowchart', 'graph', 'sequenceDiagram', 'classDiagram', 'erDiagram',
    'stateDiagram-v2', 'stateDiagram',
    'C4Context', 'C4Container',
    'gantt', 'pie', 'gitGraph', 'mindmap', 'timeline',
    'quadrantChart', 'xychart-beta',
]);

// Types handled by @mermaid-js/parser: keyword → parser type argument
const NEW_PARSER_MAP = {'architecture-beta': 'architecture'};

const ALL_KNOWN_TYPES = [...LEGACY_TYPES, ...Object.keys(NEW_PARSER_MAP)];

// ── Parser initialization (dynamic imports — graceful on missing node_modules) ─

let legacyAvail = false;
let newAvail = false;
let legacyParse = null;  // async (code: string) => void — throws on syntax error
let newParse = null;  // (type: string, code: string) => void — throws on syntax error

async function initParsers() {
    // ── 1. mermaid + jsdom (legacy types) ────────────────────────────────────
    // jsdom provides the DOM globals mermaid reads at import time; the Jison
    // parsers themselves are pure JS and don't use the DOM during parse.
    try {
        const {JSDOM} = await import('jsdom');
        const {window: w} = new JSDOM('<!DOCTYPE html><html><body></body></html>');
        globalThis.window = w;
        globalThis.document = w.document;
        // Node 21+ defines navigator as a getter-only property on globalThis; a plain
        // assignment throws TypeError.  Object.defineProperty bypasses the restriction.
        Object.defineProperty(globalThis, 'navigator', {get: () => w.navigator, configurable: true});
        globalThis.location = w.location;
        globalThis.SVGElement = w.SVGElement;
        globalThis.HTMLElement = w.HTMLElement;
        globalThis.Element = w.Element;
        globalThis.DOMParser = w.DOMParser;

        const mermaidMod = await import('mermaid');
        const mermaid = mermaidMod.default ?? mermaidMod;
        mermaid.initialize({startOnLoad: false, securityLevel: 'loose'});

        legacyParse = async (code) => {
            const result = await mermaid.parse(code);
            if (result === false) throw new Error('syntax check failed (no detail available)');
        };
        legacyAvail = true;
    } catch (e) {
        process.stderr.write(
            'WARNING: mermaid+jsdom unavailable — run `npm install` in scripts/ to enable real\n' +
            '         syntax validation for flowchart, ERD, sequence, C4, class, and state.\n' +
            '         These types will fall back to heuristic checks (shown as "heuristics only").\n' +
            `         Reason: ${e?.message ?? e}\n\n`
        );
    }

    // ── 2. @mermaid-js/parser (new types like architecture-beta) ─────────────
    try {
        const {parse} = await import('@mermaid-js/parser');
        newParse = parse;
        newAvail = true;
    } catch {
        if (legacyAvail) {
            process.stderr.write(
                'NOTE: @mermaid-js/parser unavailable — architecture-beta will use heuristics.\n' +
                '      Run `npm install` in scripts/ to enable.\n\n'
            );
        }
        // If legacyAvail is also false, the first warning already covers this.
    }
}

// ── Per-diagram validation ────────────────────────────────────────────────────

const DIAGRAMS_PATH = path.resolve(
    process.cwd(), 'docs', 'architecture-designer', 'diagrams.json'
);

// ── validateCode() helpers ─────────────────────────────────────────────────────
// Each helper below owns one concern of the old monolithic validateCode(): type
// detection, dispatch to the real parser, and each independent heuristic check.
// validateCode() itself just orchestrates them in the same order/short-circuit
// behavior as before — no behavior changed by this split, only its shape.

/**
 * Normalizes a raw `code` field before parsing: strips a leading BOM, unifies
 * CRLF/CR line endings to LF, and removes trailing whitespace per line — all
 * artifacts of how the text was authored/copy-pasted, not part of the diagram
 * itself. Leading indentation is left untouched: Mermaid is whitespace-sensitive
 * (subgraph/participant nesting depth is inferred from it), so only trailing
 * whitespace is safe to strip. This never writes back to diagrams.json — it
 * only normalizes the in-memory copy used for validation.
 */
function normalizeCode(code) {
    return code
        .replace(/^\uFEFF/, '')
        .replace(/\r\n?/g, '\n')
        .split('\n')
        .map(line => line.replace(/[ \t]+$/, ''))
        .join('\n')
        .trim();
}

/** Skips leading %% comment/init-directive lines to find the diagram type keyword. */
function findDiagramType(lines) {
    let typeIdx = 0;
    while (typeIdx < lines.length && lines[typeIdx].trim().startsWith('%%')) typeIdx++;
    const typeLine = (lines[typeIdx] ?? '').trim();
    const keyword = ALL_KNOWN_TYPES.find(t => typeLine.startsWith(t));
    return {keyword, typeIdx, typeLine};
}

/**
 * Dispatches to the real parser for `keyword`, if one is available.
 * Returns { ran, fatalError }: `fatalError` set means validateCode must stop and
 * report it immediately (a genuine syntax error) rather than run heuristics;
 * `ran: false, fatalError: null` means fall through to heuristics (no parser
 * available, or the new parser doesn't cover this type yet).
 */
async function runRealParser(keyword, trimmed) {
    if (LEGACY_TYPES.has(keyword) && legacyAvail) {
        try {
            await legacyParse(trimmed);
            return {ran: true, fatalError: null};
        } catch (e) {
            const msg = String(e?.message ?? e).replace(/\n/g, ' ').slice(0, 300);
            return {ran: false, fatalError: `Parse error: ${msg}`};
        }
    }
    if (keyword in NEW_PARSER_MAP && newAvail) {
        try {
            newParse(NEW_PARSER_MAP[keyword], trimmed);
            return {ran: true, fatalError: null};
        } catch (e) {
            const msg = String(e?.message ?? e).replace(/\n/g, ' ').slice(0, 300);
            if (/unsupported|not (yet )?supported|unknown diagram|no parser/i.test(msg)) {
                return {ran: false, fatalError: null}; // this type isn't covered yet
            }
            return {ran: false, fatalError: `Parse error: ${msg}`};
        }
    }
    return {ran: false, fatalError: null};
}

/** architecture-beta: icon names misused as standalone node types. */
function checkArchitectureBetaIcons(keyword, trimmed, parserRan) {
    const errors = [];
    if (!parserRan && keyword === 'architecture-beta') {
        for (const icon of ['database', 'cloud', 'server', 'internet', 'disk']) {
            if (new RegExp(`^[ \\t]+${icon}[ \\t]+\\w`, 'm').test(trimmed)) {
                errors.push(
                    `"${icon}" is a Mermaid icon name, not a node type — use service, group, or junction instead`
                );
            }
        }
    }
    return errors;
}

/**
 * C4: UpdateLayoutConfig is a layout requirement, not enforced by syntax — so
 * this runs regardless of whether the real parser ran. Also checks relationship
 * density: diagrams-guide.md Rule 6's `c4ShapeMargin` note — UpdateLayoutConfig only
 * prevents shape-box overlap; it does nothing for Rel() label collisions, which is a
 * verified, separate failure mode once enough relationships converge on one shape.
 * Returns {errors, notes} since the relationship-density check is advisory.
 */
function checkC4LayoutConfig(keyword, trimmed) {
    const errors = [];
    const notes = [];
    if (keyword === 'C4Context' || keyword === 'C4Container') {
        if (!trimmed.includes('UpdateLayoutConfig')) {
            errors.push(
                'Missing UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1") — required to prevent node overlap'
            );
        }
        const relCount = (trimmed.match(/^\s*Rel\w*\(/gm) ?? []).length;
        if (relCount >= 7 && !/c4ShapeMargin/.test(trimmed)) {
            notes.push(
                `Rule 6: ${relCount} Rel() relationships detected with no c4ShapeMargin override — relationship labels have no automatic collision avoidance in Mermaid's C4 renderer and can overlap each other once this many converge on a shape, even with UpdateLayoutConfig set correctly. Consider %%{init: {'c4': {'c4ShapeMargin': 90}}}%% and check the live preview for colliding labels; use UpdateRelStyle($from=..., $to=..., $offsetY=...) to nudge any that still overlap — see diagrams-guide.md Rule 6.`
            );
        }
    }
    return {errors, notes};
}

/**
 * Rule 7 (diagrams-guide.md "Preventing Node Overlap"): sibling (non-nested) subgraphs
 * connected by inter-subgraph edges — the "sequential stages/pipeline" shape (e.g. the
 * CI/CD Pipeline Diagram template's CI -> dev -> staging -> prod stages). This has a
 * *verified* ELK failure mode (empirically reproduced via rendered-DOM inspection, not a
 * theoretical concern): an edge from a node inside one sibling subgraph to a node inside
 * another can get routed through many unrelated nodes far outside the direct path, worse
 * than the node overlap ELK exists to prevent. Detected regardless of whether ELK is
 * present, so both directions can be advised: don't require ELK here on node-count
 * grounds alone (Rule 1), and warn if ELK is already active for this exact risky shape.
 *
 * Heuristic approach: track which top-level (depth-1) subgraph "owns" each identifier
 * token seen while inside it (covers both bracket-declared nodes and bare-id edge
 * endpoints declared inline, e.g. `Lint --> UnitTest["cargo test"]`), then scan
 * depth-0 edge lines for a source/target pair whose owners differ.
 */
function checkSiblingSubgraphEdges(keyword, lines) {
    if (keyword !== 'flowchart' && keyword !== 'graph') {
        return {riskyShape: false, topLevelCount: 0, interSubgraphEdges: 0};
    }

    const idTokenRe = /[A-Za-z][A-Za-z0-9_]*/g;
    const arrowRe = /--[.ox]*>|==[.ox]*>|-\.-*>/;

    let depth = 0;
    let topLevelIndex = -1;
    let topLevelCount = 0;
    const nodeOwner = new Map();
    for (const line of lines) {
        const t = line.trim();
        if (/^subgraph\b/.test(t)) {
            depth++;
            if (depth === 1) {
                topLevelIndex = topLevelCount;
                topLevelCount++;
            }
            continue;
        }
        if (/^end$/.test(t)) {
            depth = Math.max(0, depth - 1);
            if (depth === 0) topLevelIndex = -1;
            continue;
        }
        if (depth >= 1 && topLevelIndex >= 0) {
            let m;
            idTokenRe.lastIndex = 0;
            while ((m = idTokenRe.exec(t)) !== null) {
                if (!nodeOwner.has(m[0])) nodeOwner.set(m[0], topLevelIndex);
            }
        }
    }
    if (topLevelCount < 2) return {riskyShape: false, topLevelCount, interSubgraphEdges: 0};

    depth = 0;
    let interSubgraphEdges = 0;
    for (const line of lines) {
        const t = line.trim();
        if (/^subgraph\b/.test(t)) { depth++; continue; }
        if (/^end$/.test(t)) { depth = Math.max(0, depth - 1); continue; }
        if (depth !== 0 || !arrowRe.test(t)) continue;
        const parts = t.split(arrowRe);
        if (parts.length < 2) continue;
        const leftMatches = parts[0].match(idTokenRe);
        const leftId = leftMatches ? leftMatches[leftMatches.length - 1] : null;
        const rightRaw = parts[parts.length - 1].replace(/^\|[^|]*\|/, '');
        const rightMatches = rightRaw.match(idTokenRe);
        const rightId = rightMatches ? rightMatches[0] : null;
        if (!leftId || !rightId) continue;
        const a = nodeOwner.get(leftId), b = nodeOwner.get(rightId);
        if (a !== undefined && b !== undefined && a !== b) interSubgraphEdges++;
    }

    return {riskyShape: interSubgraphEdges > 0, topLevelCount, interSubgraphEdges};
}

/**
 * flowchart / graph: node-overlap rules from diagrams-guide.md "Preventing Node
 * Overlap" — none of these are syntax rules, so they're checked regardless of
 * whether the real parser ran (same rationale as the C4 check above).
 * Returns { errors, notes } since Rule 2 is advisory (a note), not a failure.
 */
function checkFlowchartNodeOverlap(keyword, trimmed, lines, siblingSubgraphInfo) {
    const errors = [];
    const notes = [];
    if (keyword !== 'flowchart' && keyword !== 'graph') return {errors, notes};

    const hasElkInit = /%%\{\s*init:\s*\{\s*['"]?layout['"]?\s*:\s*['"]elk['"]/i.test(trimmed);
    const {riskyShape, topLevelCount, interSubgraphEdges} = siblingSubgraphInfo;

    if (hasElkInit && riskyShape) {
        notes.push(
            `Rule 7: ${topLevelCount} sibling subgraphs connected by ${interSubgraphEdges} inter-subgraph edge(s), with ELK layout active — ELK has a verified failure mode for exactly this shape (a cross-subgraph edge can route through many unrelated nodes far outside the direct path, worse than the overlap it's meant to prevent — this is exactly what the CI/CD Pipeline Diagram template's stage-to-stage edges hit). Open the live preview and confirm these edges render as short, direct paths; if any detour through unrelated nodes, remove the ELK init directive and use default Dagre layout instead — see diagrams-guide.md Rule 7.`
        );
    }

    // Rule 1 / Rule 5 — subgraph nesting depth and node count drive the ELK requirement.
    let depth = 0, maxDepth = 0;
    for (const line of lines) {
        const t = line.trim();
        if (/^subgraph\b/.test(t)) {
            depth++;
            maxDepth = Math.max(maxDepth, depth);
        } else if (/^end$/.test(t)) {
            depth = Math.max(0, depth - 1);
        }
    }
    const nodeIds = new Set();
    const nodeDeclRe = /^\s*([A-Za-z0-9_]+)(\[\[|\(\(|\[\(|[[({])/;
    for (const line of lines) {
        const m = line.match(nodeDeclRe);
        if (m) nodeIds.add(m[1]);
    }
    if (!hasElkInit) {
        if (maxDepth >= 3) {
            errors.push(
                `Rule 1/5: subgraph nesting depth is ${maxDepth} (3+) with no ELK init directive — add %%{init: {'layout': 'elk'}}%% as the first line, or flatten to at most 2 levels`
            );
        }
        if (nodeIds.size >= 12 && !riskyShape) {
            errors.push(
                `Rule 1: ${nodeIds.size} nodes detected with no ELK init directive — add %%{init: {'layout': 'elk'}}%% as the first line for diagrams with 12+ nodes`
            );
        } else if (nodeIds.size >= 12 && riskyShape) {
            notes.push(
                `Rule 1/7: ${nodeIds.size} nodes across ${topLevelCount} sibling subgraphs connected by inter-subgraph edges — Rule 1's ELK recommendation is intentionally NOT applied here, since Rule 7's verified failure mode makes ELK actively worse for this shape. Default Dagre is correct; only add spacing overrides (Rule 2) if nodes overlap within one subgraph.`
            );
        } else if (nodeIds.size >= 8) {
            notes.push(
                `Rule 2: ${nodeIds.size} nodes with default Dagre spacing — consider %%{init: {'flowchart': {'nodeSpacing': 80, 'rankSpacing': 100}}}%% if nodes overlap visually`
            );
        }
    }

    // Rule 3 — node label length (28 chars per line; <br/> splits count as separate lines).
    // Scanned per-line, skipping subgraph-declaration lines: a subgraph's own bracketed title
    // (e.g. subgraph PublicSubnet["Public Subnet (AZ-a + AZ-b)"]) matches this same [...] shape
    // but is governed by the separate 35-char subgraph-title rule below — without this exclusion,
    // any subgraph title between 29 and 35 characters (valid under that rule) was also flagged
    // here as a false-positive 28-char node-label violation.
    const labelRe = /\[["']?([^\]"']{1,400})["']?\]/g;
    for (const line of lines) {
        if (/^\s*subgraph\b/.test(line)) continue;
        for (const lm of line.matchAll(labelRe)) {
            // Strip leading/trailing shape delimiters that the character class above can't
            // exclude (subroutine [[Label]], cylinder [(Label)], etc.) — otherwise a node's
            // own extra bracket/paren is counted as part of the label, inflating its length.
            const label = lm[1].replace(/^[[({]+/, '').replace(/[\])}]+$/, '');
            for (const ll of label.split(/<br\s*\/?>/i)) {
                if (ll.length > 28) {
                    errors.push(
                        `Rule 3: node label line exceeds 28 characters (${ll.length}): "${ll.slice(0, 40)}${ll.length > 40 ? '…' : ''}" — use <br/> to break across lines`
                    );
                }
            }
        }
    }
    // Rule 3 — subgraph titles (35 char max, Dagre does not resize to fit).
    const subgraphTitleRe = /^\s*subgraph\s+\S+\s*\[?["']?([^\]"'\n]{1,200})/gm;
    let sm;
    while ((sm = subgraphTitleRe.exec(trimmed)) !== null) {
        const title = sm[1].trim();
        if (title.length > 35) {
            errors.push(
                `Rule 3: subgraph title exceeds 35 characters (${title.length}): "${title.slice(0, 40)}…"`
            );
        }
    }

    return {errors, notes};
}

/** architecture-beta: Rule 4 — align directives must precede edge statements. */
function checkArchitectureBetaAlignOrder(keyword, lines) {
    const errors = [];
    if (keyword !== 'architecture-beta') return errors;

    const alignIdx = [];
    const edgeIdx = [];
    lines.forEach((line, i) => {
        const t = line.trim();
        if (/^align\s/.test(t)) alignIdx.push(i);
        // Architecture-beta's edge operator is "--" or "-->", always whitespace-delimited
        // on both sides (e.g. "serviceA:R -- L:serviceB"). Requiring that whitespace avoids
        // false-positiving on a title/label string that merely contains a double hyphen
        // (e.g. "read--write") or hyphenated words, which have no surrounding space.
        else if (/\s--(>)?\s/.test(t) && !t.startsWith('%%')) edgeIdx.push(i);
    });
    if (alignIdx.length > 0 && edgeIdx.length > 0) {
        const firstEdge = Math.min(...edgeIdx);
        if (alignIdx.some(i => i > firstEdge)) {
            errors.push(
                `Rule 4: align directive(s) appear after an edge statement (line ${firstEdge + 1} is the first edge) — define all align statements before any edge statements`
            );
        }
    }
    return errors;
}

/**
 * flowchart / graph: bracket-balance heuristic (only when real parser unavailable).
 * Tolerates a difference of up to 4 before flagging, to avoid false positives on
 * legitimate single stray brackets inside a node label. This means a genuine
 * unclosed-bracket bug with a diff of 1-3 silently passes undetected while in this
 * degraded (parser-unavailable) mode — the "(heuristics only)" quality marker this
 * function's errors are reported under already discloses reduced coverage, but this
 * specific blind spot (up to 3 unbalanced brackets can slip through) is not obvious
 * from that marker alone.
 */
function checkBracketBalance(keyword, trimmed, parserRan) {
    const errors = [];
    if (!parserRan && (keyword === 'flowchart' || keyword === 'graph')) {
        const open = (trimmed.match(/[\[({]/g) ?? []).length;
        const close = (trimmed.match(/[\])}]/g) ?? []).length;
        if (Math.abs(open - close) > 4) {
            errors.push(
                `Possible unclosed bracket — ${open} opening vs ${close} closing bracket characters (difference > 4)`
            );
        }
    }
    return errors;
}

/** Returns { errors: string[], notes: string[], quality: 'parsed' | 'heuristics' } */
async function validateCode(id, code) {
    const trimmed = normalizeCode(code);
    if (!trimmed) {
        return {errors: ['code field is empty'], notes: [], quality: 'parsed'};
    }

    const lines = trimmed.split('\n');
    const {keyword, typeIdx, typeLine} = findDiagramType(lines);
    if (!keyword) {
        return {
            errors: [`Unrecognized diagram type on line ${typeIdx + 1}: "${typeLine.slice(0, 70)}"`],
            notes: [],
            quality: 'parsed',
        };
    }

    const {ran: parserRan, fatalError} = await runRealParser(keyword, trimmed);
    if (fatalError) {
        return {errors: [fatalError], notes: [], quality: 'parsed'};
    }

    // Heuristics run as fallback when no parser is available for this type, or for
    // semantic checks that aren't syntax rules (e.g. UpdateLayoutConfig is a layout
    // requirement, not enforced by the grammar — check it even when parser passes).
    const siblingSubgraphInfo = checkSiblingSubgraphEdges(keyword, lines);
    const flowchartChecks = checkFlowchartNodeOverlap(keyword, trimmed, lines, siblingSubgraphInfo);
    const c4Checks = checkC4LayoutConfig(keyword, trimmed);
    const errors = [
        ...checkArchitectureBetaIcons(keyword, trimmed, parserRan),
        ...c4Checks.errors,
        ...flowchartChecks.errors,
        ...checkArchitectureBetaAlignOrder(keyword, lines),
        ...checkBracketBalance(keyword, trimmed, parserRan),
    ];

    return {
        errors,
        notes: [...flowchartChecks.notes, ...c4Checks.notes],
        quality: parserRan ? 'parsed' : 'heuristics',
    };
}

// ── indexPlan contract check ──────────────────────────────────────────────────
// A row missing one of the five keys — or carrying one as an empty/blank string —
// is not an index row — usually it means the field was filled with entity
// descriptions or other ERD notes instead of an index plan, or left as a
// placeholder. Catch that mechanically rather than relying on the writer to have
// followed the field guide.

const INDEX_PLAN_KEYS = ['name', 'table', 'columns', 'type', 'reason'];

function isBlankIndexPlanValue(value) {
    return value === undefined || value === null || String(value).trim() === '';
}

function validateIndexPlan(rows) {
    if (!Array.isArray(rows)) return ['indexPlan must be an array of index rows'];
    return rows.flatMap((row, i) => {
        if (!row || typeof row !== 'object') return [`indexPlan row ${i + 1} is not an object`];
        const missing = INDEX_PLAN_KEYS.filter(k => !(k in row) || isBlankIndexPlanValue(row[k]));
        return missing.length > 0
            ? [`indexPlan row ${i + 1} missing or empty key(s): ${missing.join(', ')} — looks like an entity description or note, not an index row`]
            : [];
    });
}

// ── Main ──────────────────────────────────────────────────────────────────────

await initParsers();

let raw;
try {
    raw = fs.readFileSync(DIAGRAMS_PATH, 'utf8');
} catch (err) {
    process.stderr.write(`\nERROR: Cannot read ${DIAGRAMS_PATH}\n  ${err.message}\n\n`);
    process.exit(1);
}

let data;
try {
    data = JSON.parse(raw);
} catch (err) {
    process.stderr.write(`\nERROR: diagrams.json is not valid JSON\n  ${err.message}\n\n`);
    process.exit(1);
}

const diagrams = Array.isArray(data.diagrams) ? data.diagrams : [];
if (diagrams.length === 0) {
    process.stdout.write('\nWARNING: diagrams array is empty — nothing to validate.\n\n');
    process.exit(0);
}

const results = [];
let anyFailed = false;

for (const d of diagrams) {
    const id = String(d.id ?? '(no id)');
    const fieldErrors = [];
    const notes = [];
    if (!d.id) fieldErrors.push('missing required field: id');
    if (!d.title) fieldErrors.push('missing required field: title');
    if (!d.code) fieldErrors.push('missing required field: code');

    if (d.indexPlan !== undefined || d.companionTable !== undefined) {
        if (d.indexPlan === undefined) {
            notes.push('using deprecated key "companionTable" — rename to "indexPlan"');
        }
        // diagrams-guide.md: "omit this field entirely for all non-ERD diagrams" — check the
        // diagram's own type keyword rather than trusting the id/title to say "erd".
        if (d.code) {
            const {keyword} = findDiagramType(normalizeCode(d.code).split('\n'));
            if (keyword && keyword !== 'erDiagram') {
                fieldErrors.push(
                    `indexPlan/companionTable present on a "${keyword}" diagram — this field is ERD-only per diagrams-guide.md; omit it for non-ERD diagrams`
                );
            }
        }
        fieldErrors.push(...validateIndexPlan(d.indexPlan ?? d.companionTable));
    }

    const {errors: codeErrors, notes: codeNotes, quality} = d.code
        ? await validateCode(id, d.code)
        : {errors: [], notes: [], quality: 'parsed'};
    notes.push(...codeNotes);

    const errors = [...fieldErrors, ...codeErrors];
    if (errors.length > 0) anyFailed = true;
    results.push({id, errors, notes, quality});
}

// ── Report ────────────────────────────────────────────────────────────────────

const LINE = '─'.repeat(60);
process.stdout.write(`\nMermaid Diagram Validation\n${LINE}\n`);
process.stdout.write(`Source: ${DIAGRAMS_PATH}\n${LINE}\n`);

for (const r of results) {
    if (r.errors.length === 0) {
        const mark = r.quality === 'heuristics' ? '✓ (heuristics only)' : '✓';
        process.stdout.write(`  ${mark.padEnd(22)} ${r.id}\n`);
    } else {
        process.stdout.write(`  ✗  ${r.id}\n`);
        for (const e of r.errors) {
            process.stdout.write(`       → ${e}\n`);
        }
    }
    for (const n of r.notes) {
        process.stdout.write(`       note: ${n}\n`);
    }
}

const heuristicCount = results.filter(r => r.quality === 'heuristics').length;
const degradedSuffix = heuristicCount > 0
    ? ` DEGRADED MODE — ${heuristicCount} of ${results.length} diagram(s) were checked via heuristics only (full syntax parser unavailable); run \`npm install\` in scripts/ for complete coverage.`
    : '';

process.stdout.write(`${LINE}\n`);
if (anyFailed) {
    process.stdout.write(`VALIDATION FAILED — fix the errors above before opening the preview.${degradedSuffix}\n\n`);
    process.exit(1);
} else {
    process.stdout.write(
        `VALIDATION PASSED — all ${results.length} diagram(s) look structurally sound.${degradedSuffix}\n\n`
    );
    process.exit(0);
}
