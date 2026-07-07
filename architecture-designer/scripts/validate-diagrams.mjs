/**
 * Structural + syntactic validation for docs/architecture-designer/diagrams.json.
 * Usage: node scripts/validate-diagrams.mjs
 *
 * Validates each diagram with the real @mermaid-js/parser, catching actual syntax
 * errors before they reach the browser. Heuristic checks supplement the parser for
 * diagram types it does not yet cover (e.g. architecture-beta node-type misuse).
 *
 * Requires: run `npm install` in the scripts/ directory once before first use.
 *
 * Exit 0 → all pass.  Exit 1 → one or more failures.
 */

import fs from 'fs';
import path from 'path';
import { parse } from '@mermaid-js/parser';

// First-line Mermaid keyword → @mermaid-js/parser type argument
const PARSER_TYPES = {
  flowchart:           'flowchart',
  graph:               'flowchart',
  sequenceDiagram:     'sequenceDiagram',
  classDiagram:        'classDiagram',
  erDiagram:           'erDiagram',
  'stateDiagram-v2':   'stateDiagram',
  stateDiagram:        'stateDiagram',
  C4Context:           'c4',
  C4Container:         'c4',
  C4Component:         'c4',
  'architecture-beta': 'architecture',
  gantt:               'gantt',
  pie:                 'pie',
  gitGraph:            'gitGraph',
  mindmap:             'mindmap',
  timeline:            'timeline',
};

const DIAGRAMS_PATH = path.resolve(
  process.cwd(),
  'docs', 'architecture-designer', 'diagrams.json'
);

const KNOWN_TYPES = Object.keys(PARSER_TYPES);

function validateCode(id, code) {
  const errors = [];
  const trimmed = code.trim();

  if (!trimmed) {
    errors.push('code field is empty');
    return errors;
  }

  const lines = trimmed.split('\n');
  const firstLine = lines[0].trim();

  // Allow %%{init ...}%% as first line — type keyword is then on line 2
  const typeLineIdx = firstLine.startsWith('%%') ? 1 : 0;
  const typeLine = (lines[typeLineIdx] ?? '').trim();

  const detectedKeyword = KNOWN_TYPES.find(t => typeLine.startsWith(t));

  if (!detectedKeyword) {
    errors.push(
      `Unrecognized diagram type on line ${typeLineIdx + 1}: "${typeLine.slice(0, 70)}"`
    );
    return errors; // nothing further to check without a type
  }

  // ── Real Mermaid parse ───────────────────────────────────────────────────

  const parserType = PARSER_TYPES[detectedKeyword];
  try {
    parse(parserType, trimmed);
    // Parse succeeded — heuristics below are redundant; return clean
    return errors;
  } catch (parseErr) {
    const msg = String(parseErr?.message ?? parseErr)
      .replace(/\n/g, ' ')
      .slice(0, 300);
    // "Type not yet supported by parser" → fall through to heuristics
    const isUnsupported =
      /unsupported|not (yet )?supported|unknown diagram|no parser/i.test(msg);
    if (!isUnsupported) {
      errors.push(`Parse error: ${msg}`);
      return errors; // real error supersedes heuristics
    }
  }

  // ── Heuristic checks (complement real parse for unsupported diagram types) ──

  // architecture-beta: icon names used as standalone node types
  if (typeLine === 'architecture-beta') {
    const iconNames = ['database', 'cloud', 'server', 'internet', 'disk'];
    for (const icon of iconNames) {
      const re = new RegExp(`^[ \\t]+${icon}[ \\t]+\\w`, 'm');
      if (re.test(trimmed)) {
        errors.push(
          `"${icon}" is a Mermaid icon name, not a node type — use service, group, or junction instead`
        );
      }
    }
  }

  // C4: missing UpdateLayoutConfig (required to prevent node overlap)
  if (typeLine.startsWith('C4Context') || typeLine.startsWith('C4Container')) {
    if (!trimmed.includes('UpdateLayoutConfig')) {
      errors.push(
        'Missing UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1") — required to prevent node overlap'
      );
    }
  }

  // flowchart / graph: basic bracket-balance heuristic (tolerance = 4)
  if (typeLine.startsWith('flowchart') || typeLine.startsWith('graph')) {
    const open  = (trimmed.match(/[\[({]/g) ?? []).length;
    const close = (trimmed.match(/[\])}]/g) ?? []).length;
    if (Math.abs(open - close) > 4) {
      errors.push(
        `Possible unclosed bracket — ${open} opening vs ${close} closing bracket characters (difference > 4)`
      );
    }
  }

  return errors;
}

// ── Load diagrams.json ────────────────────────────────────────────────────────

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

// ── Validate each entry ───────────────────────────────────────────────────────

const results = [];
let anyFailed = false;

for (const d of diagrams) {
  const id = String(d.id ?? '(no id)');
  const fieldErrors = [];
  if (!d.id)    fieldErrors.push('missing required field: id');
  if (!d.title) fieldErrors.push('missing required field: title');
  if (!d.code)  fieldErrors.push('missing required field: code');

  const codeErrors = d.code ? validateCode(id, d.code) : [];
  const errors = [...fieldErrors, ...codeErrors];
  if (errors.length > 0) anyFailed = true;
  results.push({ id, errors });
}

// ── Report ────────────────────────────────────────────────────────────────────

const LINE = '─'.repeat(60);
process.stdout.write(`\nMermaid Diagram Validation\n${LINE}\n`);
process.stdout.write(`Source: ${DIAGRAMS_PATH}\n${LINE}\n`);

for (const r of results) {
  if (r.errors.length === 0) {
    process.stdout.write(`  ✓  ${r.id}\n`);
  } else {
    process.stdout.write(`  ✗  ${r.id}\n`);
    for (const e of r.errors) {
      process.stdout.write(`       → ${e}\n`);
    }
  }
}

process.stdout.write(`${LINE}\n`);
if (anyFailed) {
  process.stdout.write(
    `VALIDATION FAILED — fix the errors above before opening the preview.\n\n`
  );
  process.exit(1);
} else {
  process.stdout.write(
    `VALIDATION PASSED — all ${results.length} diagram(s) look structurally sound.\n\n`
  );
  process.exit(0);
}
