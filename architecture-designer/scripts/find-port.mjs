/**
 * Finds the first available TCP port in the range 3000–9000.
 * Uses only the built-in `net` module — no shell commands, no external deps.
 * Prints the port number to stdout, then exits 0.
 * Exits 1 with an error message if the entire range is occupied.
 */

import net from 'net';

const START_PORT = 3000;
const END_PORT = 9000;

function tryBind(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(false));
    server.once('listening', () => server.close(() => resolve(true)));
    server.listen(port, '127.0.0.1');
  });
}

async function main() {
  for (let port = START_PORT; port <= END_PORT; port++) {
    if (await tryBind(port)) {
      process.stdout.write(`${port}\n`);
      process.exit(0);
    }
  }
  process.stderr.write(
    `Error: No free port found in range ${START_PORT}–${END_PORT}.\n` +
    'Please close some applications and try again.\n'
  );
  process.exit(1);
}

main();
