/**
 * Structural validation for docs/architecture-designer/diagrams.json.
 * Usage: node scripts/validate-diagrams.mjs
 *
 * Checks each diagram entry for:
 *   - Required fields (id, title, code)
 *   - Recognized Mermaid diagram type on first/second line
 *   - architecture-beta: icon names misused as node types
 *   - C4Context / C4Container: missing UpdateLayoutConfig
 *   - flowchart / graph: basic bracket-balance heuristic
 *
 * Exit 0 → all pass.  Exit 1 → one or more failures.
 */

import fs from 'fs';
import path from 'path';

const DIAGRAMS_PATH = path.resolve(
  process.cwd(),
  'docs', 'architecture-designer', 'diagrams.json'
);

const KNOWN_TYPES = [
  'flowchart', 'graph', 'sequenceDiagram', 'classDiagram',
  'stateDiagram-v2', 'stateDiagram', 'erDiagram',
  'C4Context', 'C4Container', 'C4Component',
  'architecture-beta', 'gantt', 'pie', 'gitGraph',
  'mindmap', 'timeline',
];

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

  if (!KNOWN_TYPES.some(t => typeLine.startsWith(t))) {
    errors.push(
      `Unrecognized diagram type on line ${typeLineIdx + 1}: "${typeLine.slice(0, 70)}"`
    );
  }

  // architecture-beta: icon names used as standalone node types
  if (typeLine === 'architecture-beta') {
    const iconNames = ['database', 'cloud', 'server', 'internet', 'disk'];
    for (const icon of iconNames) {
      // Match an indented line that starts with the icon name followed by an identifier
      // This pattern matches node declarations like "  database foo[..." but NOT
      // valid icon slot usage like "service db(database)[Label]"
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
