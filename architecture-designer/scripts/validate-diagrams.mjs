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
  'C4Context', 'C4Container', 'C4Component',
  'gantt', 'pie', 'gitGraph', 'mindmap', 'timeline',
  'quadrantChart', 'xychart-beta',
]);

// Types handled by @mermaid-js/parser: keyword → parser type argument
const NEW_PARSER_MAP = { 'architecture-beta': 'architecture' };

const ALL_KNOWN_TYPES = [...LEGACY_TYPES, ...Object.keys(NEW_PARSER_MAP)];

// ── Parser initialization (dynamic imports — graceful on missing node_modules) ─

let legacyAvail = false;
let newAvail    = false;
let legacyParse = null;  // async (code: string) => void — throws on syntax error
let newParse    = null;  // (type: string, code: string) => void — throws on syntax error

async function initParsers() {
  // ── 1. mermaid + jsdom (legacy types) ────────────────────────────────────
  // jsdom provides the DOM globals mermaid reads at import time; the Jison
  // parsers themselves are pure JS and don't use the DOM during parse.
  try {
    const { JSDOM } = await import('jsdom');
    const { window: w } = new JSDOM('<!DOCTYPE html><html><body></body></html>');
    globalThis.window    = w;
    globalThis.document  = w.document;
    // Node 21+ defines navigator as a getter-only property on globalThis; a plain
    // assignment throws TypeError.  Object.defineProperty bypasses the restriction.
    Object.defineProperty(globalThis, 'navigator', { get: () => w.navigator, configurable: true });
    globalThis.location  = w.location;
    globalThis.SVGElement  = w.SVGElement;
    globalThis.HTMLElement = w.HTMLElement;
    globalThis.Element     = w.Element;
    globalThis.DOMParser   = w.DOMParser;

    const mermaidMod = await import('mermaid');
    const mermaid = mermaidMod.default ?? mermaidMod;
    mermaid.initialize({ startOnLoad: false, securityLevel: 'loose' });

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
    const { parse } = await import('@mermaid-js/parser');
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

/** Returns { errors: string[], notes: string[], quality: 'parsed' | 'heuristics' } */
async function validateCode(id, code) {
  const errors  = [];
  const notes   = [];
  const trimmed = code.trim();

  if (!trimmed) {
    return { errors: ['code field is empty'], notes, quality: 'parsed' };
  }

  const lines = trimmed.split('\n');
  // Skip all leading %% comment / init-directive lines to find the diagram type keyword.
  let typeIdx = 0;
  while (typeIdx < lines.length && lines[typeIdx].trim().startsWith('%%')) typeIdx++;
  const typeLine = (lines[typeIdx] ?? '').trim();
  const keyword   = ALL_KNOWN_TYPES.find(t => typeLine.startsWith(t));

  if (!keyword) {
    errors.push(`Unrecognized diagram type on line ${typeIdx + 1}: "${typeLine.slice(0, 70)}"`);
    return { errors, notes, quality: 'parsed' };
  }

  let parserRan = false;

  // ── Real parse ───────────────────────────────────────────────────────────

  if (LEGACY_TYPES.has(keyword) && legacyAvail) {
    try {
      await legacyParse(trimmed);
      parserRan = true;
    } catch (e) {
      const msg = String(e?.message ?? e).replace(/\n/g, ' ').slice(0, 300);
      errors.push(`Parse error: ${msg}`);
      return { errors, notes, quality: 'parsed' };
    }
  } else if (keyword in NEW_PARSER_MAP && newAvail) {
    try {
      newParse(NEW_PARSER_MAP[keyword], trimmed);
      parserRan = true;
    } catch (e) {
      const msg = String(e?.message ?? e).replace(/\n/g, ' ').slice(0, 300);
      if (/unsupported|not (yet )?supported|unknown diagram|no parser/i.test(msg)) {
        // This type isn't covered yet — fall through to heuristics
      } else {
        errors.push(`Parse error: ${msg}`);
        return { errors, notes, quality: 'parsed' };
      }
    }
  }

  // ── Heuristics ────────────────────────────────────────────────────────────
  // Run as fallback when no parser is available for this type, or for semantic
  // checks that aren't syntax rules (e.g. UpdateLayoutConfig is a layout
  // requirement, not enforced by the grammar — check it even when parser passes).

  // architecture-beta: icon names misused as standalone node types
  if (!parserRan && keyword === 'architecture-beta') {
    for (const icon of ['database', 'cloud', 'server', 'internet', 'disk']) {
      if (new RegExp(`^[ \\t]+${icon}[ \\t]+\\w`, 'm').test(trimmed)) {
        errors.push(
          `"${icon}" is a Mermaid icon name, not a node type — use service, group, or junction instead`
        );
      }
    }
  }

  // C4: UpdateLayoutConfig is a layout requirement, not enforced by syntax
  if (keyword === 'C4Context' || keyword === 'C4Container') {
    if (!trimmed.includes('UpdateLayoutConfig')) {
      errors.push(
        'Missing UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1") — required to prevent node overlap'
      );
    }
  }

  // flowchart / graph: node-overlap rules from diagrams-guide.md "Preventing Node
  // Overlap" — none of these are syntax rules, so they're checked regardless of
  // whether the real parser ran (same rationale as the C4 check above).
  if (keyword === 'flowchart' || keyword === 'graph') {
    const hasElkInit = /%%\{\s*init:\s*\{\s*['"]?layout['"]?\s*:\s*['"]elk['"]/i.test(trimmed);

    // Rule 1 / Rule 5 — subgraph nesting depth and node count drive the ELK requirement.
    let depth = 0, maxDepth = 0;
    for (const line of lines) {
      const t = line.trim();
      if (/^subgraph\b/.test(t)) { depth++; maxDepth = Math.max(maxDepth, depth); }
      else if (/^end$/.test(t)) { depth = Math.max(0, depth - 1); }
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
      if (nodeIds.size >= 12) {
        errors.push(
          `Rule 1: ${nodeIds.size} nodes detected with no ELK init directive — add %%{init: {'layout': 'elk'}}%% as the first line for diagrams with 12+ nodes`
        );
      } else if (nodeIds.size >= 8) {
        notes.push(
          `Rule 2: ${nodeIds.size} nodes with default Dagre spacing — consider %%{init: {'flowchart': {'nodeSpacing': 80, 'rankSpacing': 100}}}%% if nodes overlap visually`
        );
      }
    }

    // Rule 3 — node label length (28 chars per line; <br/> splits count as separate lines).
    const labelRe = /\[["']?([^\]"']{1,400})["']?\]/g;
    let lm;
    while ((lm = labelRe.exec(trimmed)) !== null) {
      for (const ll of lm[1].split(/<br\s*\/?>/i)) {
        if (ll.length > 28) {
          errors.push(
            `Rule 3: node label line exceeds 28 characters (${ll.length}): "${ll.slice(0, 40)}${ll.length > 40 ? '…' : ''}" — use <br/> to break across lines`
          );
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
  }

  // architecture-beta: Rule 4 — align directives must precede edge statements.
  if (keyword === 'architecture-beta') {
    const alignIdx = [];
    const edgeIdx = [];
    lines.forEach((line, i) => {
      const t = line.trim();
      if (/^align\s/.test(t)) alignIdx.push(i);
      else if (/--/.test(t) && !t.startsWith('%%')) edgeIdx.push(i);
    });
    if (alignIdx.length > 0 && edgeIdx.length > 0) {
      const firstEdge = Math.min(...edgeIdx);
      if (alignIdx.some(i => i > firstEdge)) {
        errors.push(
          `Rule 4: align directive(s) appear after an edge statement (line ${firstEdge + 1} is the first edge) — define all align statements before any edge statements`
        );
      }
    }
  }

  // flowchart / graph: bracket-balance heuristic (only when real parser unavailable)
  if (!parserRan && (keyword === 'flowchart' || keyword === 'graph')) {
    const open  = (trimmed.match(/[\[({]/g) ?? []).length;
    const close = (trimmed.match(/[\])}]/g) ?? []).length;
    if (Math.abs(open - close) > 4) {
      errors.push(
        `Possible unclosed bracket — ${open} opening vs ${close} closing bracket characters (difference > 4)`
      );
    }
  }

  return { errors, notes, quality: parserRan ? 'parsed' : 'heuristics' };
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
  const id          = String(d.id ?? '(no id)');
  const fieldErrors = [];
  const notes       = [];
  if (!d.id)    fieldErrors.push('missing required field: id');
  if (!d.title) fieldErrors.push('missing required field: title');
  if (!d.code)  fieldErrors.push('missing required field: code');

  if (d.indexPlan !== undefined || d.companionTable !== undefined) {
    if (d.indexPlan === undefined) {
      notes.push('using deprecated key "companionTable" — rename to "indexPlan"');
    }
    fieldErrors.push(...validateIndexPlan(d.indexPlan ?? d.companionTable));
  }

  const { errors: codeErrors, notes: codeNotes, quality } = d.code
    ? await validateCode(id, d.code)
    : { errors: [], notes: [], quality: 'parsed' };
  notes.push(...codeNotes);

  const errors = [...fieldErrors, ...codeErrors];
  if (errors.length > 0) anyFailed = true;
  results.push({ id, errors, notes, quality });
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
