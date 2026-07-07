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
    globalThis.navigator = w.navigator;
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
  } catch {
    process.stderr.write(
      'WARNING: mermaid+jsdom unavailable — run `npm install` in scripts/ to enable real\n' +
      '         syntax validation for flowchart, ERD, sequence, C4, class, and state.\n' +
      '         These types will fall back to heuristic checks (shown as "heuristics only").\n\n'
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

/** Returns { errors: string[], quality: 'parsed' | 'heuristics' } */
async function validateCode(id, code) {
  const errors  = [];
  const trimmed = code.trim();

  if (!trimmed) {
    return { errors: ['code field is empty'], quality: 'parsed' };
  }

  const lines     = trimmed.split('\n');
  const firstLine = lines[0].trim();
  const typeIdx   = firstLine.startsWith('%%') ? 1 : 0;
  const typeLine  = (lines[typeIdx] ?? '').trim();
  const keyword   = ALL_KNOWN_TYPES.find(t => typeLine.startsWith(t));

  if (!keyword) {
    errors.push(`Unrecognized diagram type on line ${typeIdx + 1}: "${typeLine.slice(0, 70)}"`);
    return { errors, quality: 'parsed' };
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
      return { errors, quality: 'parsed' };
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
        return { errors, quality: 'parsed' };
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

  return { errors, quality: parserRan ? 'parsed' : 'heuristics' };
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
  if (!d.id)    fieldErrors.push('missing required field: id');
  if (!d.title) fieldErrors.push('missing required field: title');
  if (!d.code)  fieldErrors.push('missing required field: code');

  const { errors: codeErrors, quality } = d.code
    ? await validateCode(id, d.code)
    : { errors: [], quality: 'parsed' };

  const errors = [...fieldErrors, ...codeErrors];
  if (errors.length > 0) anyFailed = true;
  results.push({ id, errors, quality });
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
}

process.stdout.write(`${LINE}\n`);
if (anyFailed) {
  process.stdout.write('VALIDATION FAILED — fix the errors above before opening the preview.\n\n');
  process.exit(1);
} else {
  process.stdout.write(
    `VALIDATION PASSED — all ${results.length} diagram(s) look structurally sound.\n\n`
  );
  process.exit(0);
}
