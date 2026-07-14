/**
 * Pre-flight completeness check for docs/architecture-designer/session.json.
 * Verifies that schemaVersion, project, description, and stages 1-5 have been
 * confirmed and written before Stage 6 begins.
 * Usage: node scripts/validate-session.mjs
 *
 * Exit 0 → all required fields and stages present and non-empty.
 * Exit 1 → one or more required fields or stages missing or empty.
 */

import fs from 'fs';
import path from 'path';

const SESSION_PATH = path.resolve(
  process.cwd(),
  'docs', 'architecture-designer', 'session.json'
);

const REQUIRED_STAGES = ['stage1', 'stage2', 'stage3', 'stage4', 'stage5'];
const REQUIRED_TOP_LEVEL = ['schemaVersion', 'project', 'description'];

let raw;
try {
  raw = fs.readFileSync(SESSION_PATH, 'utf8');
} catch (err) {
  process.stderr.write(`\nERROR: Cannot read ${SESSION_PATH}\n  ${err.message}\n`);
  process.stderr.write('Complete stages 1–5 of the design workflow first.\n\n');
  process.exit(1);
}

let session;
try {
  session = JSON.parse(raw);
} catch (err) {
  process.stderr.write(`\nERROR: session.json is not valid JSON\n  ${err.message}\n\n`);
  process.exit(1);
}

function isEmpty(val) {
  if (val === null || val === undefined) return true;
  if (typeof val === 'string') return val.trim() === '';
  if (typeof val === 'object') return Object.keys(val).length === 0;
  return false;
}

const LINE = '─'.repeat(60);
process.stdout.write(`\nSession Completeness Check\n${LINE}\n`);
process.stdout.write(`Source: ${SESSION_PATH}\n${LINE}\n`);

let anyFailed = false;

for (const field of REQUIRED_TOP_LEVEL) {
  if (!(field in session)) {
    process.stdout.write(`  ✗  ${field} — missing\n`);
    anyFailed = true;
  } else if (isEmpty(session[field])) {
    process.stdout.write(`  ✗  ${field} — empty\n`);
    anyFailed = true;
  } else {
    process.stdout.write(`  ✓  ${field}\n`);
  }
}

for (const stage of REQUIRED_STAGES) {
  if (!(stage in session)) {
    process.stdout.write(`  ✗  ${stage} — missing\n`);
    anyFailed = true;
  } else if (isEmpty(session[stage])) {
    process.stdout.write(`  ✗  ${stage} — empty\n`);
    anyFailed = true;
  } else {
    process.stdout.write(`  ✓  ${stage}\n`);
  }
}

process.stdout.write(`${LINE}\n`);
if (anyFailed) {
  process.stdout.write(
    'SESSION CHECK FAILED — complete the missing fields/stages before starting Stage 6.\n\n'
  );
  process.exit(1);
} else {
  process.stdout.write(
    'SESSION CHECK PASSED — all required fields and stages are present.\n\n'
  );
  process.exit(0);
}
