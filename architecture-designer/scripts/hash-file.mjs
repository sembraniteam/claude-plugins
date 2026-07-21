/**
 * Prints the sha256 hex digest of the file passed as the first CLI argument.
 * Uses only the built-in `crypto`/`fs` modules — no shell commands (e.g. `shasum`,
 * which isn't guaranteed on Windows), no external deps.
 * Prints the digest to stdout, then exits 0.
 * Exits 1 with an error message if no path was given or the file can't be read.
 */

import { createHash } from 'crypto';
import { readFileSync } from 'fs';

function main() {
  const path = process.argv[2];
  if (!path) {
    process.stderr.write('Error: pass a file path, e.g. node hash-file.mjs docs/architecture-designer/diagrams.json\n');
    process.exit(1);
  }

  let contents;
  try {
    contents = readFileSync(path);
  } catch (err) {
    process.stderr.write(`Error: could not read "${path}": ${err.message}\n`);
    process.exit(1);
  }

  const digest = createHash('sha256').update(contents).digest('hex');
  process.stdout.write(`${digest}\n`);
  process.exit(0);
}

main();
