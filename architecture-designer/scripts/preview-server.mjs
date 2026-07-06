/**
 * Architecture preview server.
 * Usage: node preview-server.mjs <port>
 *
 * Reads docs/architecture-designer/diagrams.json (relative to CWD) on every
 * request, builds an HTML page with all Mermaid diagrams, and opens the
 * browser automatically. No external deps — built-ins only.
 *
 * diagrams.json schema:
 * {
 *   "title": "Project Title",
 *   "topic": "project-topic-kebab",
 *   "generatedAt": "ISO 8601 string",
 *   "diagrams": [
 *     {
 *       "id": "use-case",
 *       "title": "Use Case Diagram",
 *       "description": "One-sentence summary shown above the diagram.",
 *       "details": "Multi-paragraph explanation (paragraphs separated by \\n\\n). Rendered as collapsible block.",
 *       "rationale": "Why this diagram type was chosen and what decisions it encodes. Rendered as collapsible block.",
 *       "companionTable": [
 *         { "name": "idx_name", "table": "tbl", "columns": "col", "type": "B-TREE", "reason": "..." }
 *       ],
 *       "code": "flowchart LR\n..."
 *     }
 *   ]
 * }
 * companionTable is optional; only include it for erDiagram entries (rendered as an index plan table below the diagram).
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const port = parseInt(process.argv[2], 10);
if (!port || isNaN(port) || port < 1 || port > 65535) {
  process.stderr.write('Usage: node preview-server.mjs <port>\n');
  process.exit(1);
}

const DIAGRAMS_PATH = path.resolve(process.cwd(), 'docs', 'architecture-designer', 'diagrams.json');

function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildTocItem(d) {
  return `<li><a href="#diagram-${esc(d.id)}">${esc(d.title)}</a></li>`;
}

function renderParagraphs(text) {
  return String(text ?? '').split(/\n\n+/)
    .filter(p => p.trim())
    .map(p => `<p>${esc(p.trim())}</p>`)
    .join('');
}

function buildCompanionTable(rows) {
  if (!Array.isArray(rows) || rows.length === 0) return '';
  const header = '<tr><th>Index Name</th><th>Table</th><th>Column(s)</th><th>Type</th><th>Reason</th></tr>';
  const body = rows.map(r => `<tr>
      <td>${esc(String(r.name ?? ''))}</td>
      <td>${esc(String(r.table ?? ''))}</td>
      <td>${esc(String(r.columns ?? ''))}</td>
      <td>${esc(String(r.type ?? ''))}</td>
      <td>${esc(String(r.reason ?? ''))}</td>
    </tr>`).join('');
  return `<div class="companion-table-wrapper">
      <div class="companion-table-title">Index plan</div>
      <table class="companion-table"><thead>${header}</thead><tbody>${body}</tbody></table>
    </div>`;
}

function buildSection(d) {
  const companionBlock = buildCompanionTable(d.companionTable);
  const detailsBlock = d.details
    ? `<details class="diagram-meta">
        <summary>Details</summary>
        <div class="meta-body">${renderParagraphs(d.details)}</div>
      </details>`
    : '';
  const rationaleBlock = d.rationale
    ? `<details class="diagram-meta">
        <summary>Design rationale</summary>
        <div class="meta-body">${renderParagraphs(d.rationale)}</div>
      </details>`
    : '';
  return `
    <section class="diagram-section" id="diagram-${esc(d.id)}" data-id="${esc(d.id)}" data-title="${esc(d.title)}">
      <h2>${esc(d.title)}</h2>
      ${d.description ? `<p class="desc">${esc(d.description)}</p>` : ''}
      <div class="controls">
        <button class="btn btn-zoom-in">＋ Zoom In</button>
        <button class="btn btn-zoom-out">－ Zoom Out</button>
        <button class="btn btn-reset">⊙ Reset</button>
        <span class="zoom-level">100%</span>
        <button class="btn btn-primary btn-download">⬇ Download PNG</button>
      </div>
      <div class="diagram-viewport">
        <div class="diagram-inner">
          <pre class="mermaid">${esc(d.code)}</pre>
        </div>
      </div>
      ${companionBlock}${detailsBlock}${rationaleBlock}
    </section>`;
}

function buildHtml(data) {
  const title = data.title ?? 'Architecture Design';
  const generatedAt = data.generatedAt
    ? new Date(data.generatedAt).toLocaleString(undefined, {
        dateStyle: 'medium', timeStyle: 'short',
      })
    : new Date().toLocaleString();
  const diagrams = Array.isArray(data.diagrams) ? data.diagrams : [];

  const tocItems = diagrams.map(buildTocItem).join('\n        ');
  const sections = diagrams.map(buildSection).join('\n');

  // NOTE: backticks and ${...} inside the <script> block are escaped as \` and \${...}
  // because they live inside an outer JS template literal.
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Architecture: ${esc(title)}</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #f0f2f5; color: #1a1a2e; line-height: 1.5; }
    header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
             color: #fff; padding: 28px 40px; }
    header h1 { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.4px; }
    header .meta { opacity: 0.6; margin-top: 6px; font-size: 0.85rem; }
    .container { max-width: 1440px; margin: 0 auto; padding: 28px 40px; }
    #toc { background: #fff; border-radius: 10px; padding: 20px 24px;
           margin-bottom: 28px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    #toc h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;
               color: #6b7280; margin-bottom: 12px; }
    #toc ul { list-style: none; display: flex; flex-wrap: wrap; gap: 8px; }
    #toc a { text-decoration: none; background: #f3f4f6; color: #374151;
              padding: 5px 14px; border-radius: 20px; font-size: 0.83rem; transition: all .15s; }
    #toc a:hover { background: #4f46e5; color: #fff; }
    .diagram-section { background: #fff; border-radius: 10px; padding: 24px 28px;
                        margin-bottom: 24px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    .diagram-section h2 { font-size: 1.2rem; font-weight: 600; margin-bottom: 6px; color: #111827; }
    .diagram-section .desc { color: #6b7280; font-size: 0.88rem; margin-bottom: 16px; }
    .controls { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; flex-wrap: wrap; }
    .btn { padding: 5px 13px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px;
            cursor: pointer; font-size: 0.8rem; color: #374151; transition: all .15s; user-select: none; }
    .btn:hover { background: #f9fafb; border-color: #9ca3af; }
    .btn-primary { background: #4f46e5; color: #fff; border-color: #4f46e5; }
    .btn-primary:hover { background: #4338ca; border-color: #4338ca; }
    .zoom-level { font-size: 0.78rem; color: #9ca3af; min-width: 44px; text-align: center; }
    .diagram-viewport { overflow: hidden; border: 1px solid #e5e7eb; border-radius: 6px;
                         background: #fafafa; min-height: 200px; cursor: grab; position: relative; }
    .diagram-viewport:active { cursor: grabbing; }
    .diagram-inner { transform-origin: 0 0; display: inline-block; padding: 20px; will-change: transform; }
    .diagram-inner svg { max-width: none !important; height: auto; display: block; }
    .mermaid { display: block; }
    .companion-table-wrapper { margin-top: 16px; border-top: 1px solid #e5e7eb; padding-top: 14px; overflow-x: auto; }
    .companion-table-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.6px; color: #6b7280; margin-bottom: 8px; }
    .companion-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
    .companion-table th { background: #f3f4f6; text-align: left; padding: 7px 10px;
      font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; white-space: nowrap; }
    .companion-table td { padding: 6px 10px; border-bottom: 1px solid #f3f4f6; color: #374151; vertical-align: top; }
    .companion-table tr:last-child td { border-bottom: none; }
    .companion-table tbody tr:hover td { background: #f9fafb; }
    .diagram-meta { border-top: 1px solid #e5e7eb; margin-top: 14px; }
    .diagram-meta summary { cursor: pointer; font-size: 0.8rem; font-weight: 600;
      color: #6b7280; padding: 10px 0; user-select: none; list-style: none; }
    .diagram-meta summary::-webkit-details-marker { display: none; }
    .diagram-meta[open] summary { color: #374151; }
    .meta-body { padding: 2px 0 12px; }
    .meta-body p { font-size: 0.87rem; color: #374151; line-height: 1.7; margin-bottom: 8px; }
    .meta-body p:last-child { margin-bottom: 0; }
    .render-error { background: #fff5f5; border: 2px solid #fca5a5; border-radius: 6px;
      padding: 14px 18px; margin: 8px 0; }
    .render-error strong { display: block; margin-bottom: 8px; font-size: 0.88rem; color: #991b1b; }
    .render-error pre { font-size: 0.76rem; white-space: pre-wrap; word-break: break-word;
      background: #fee2e2; padding: 10px 12px; border-radius: 4px; color: #7f1d1d;
      margin: 0; max-height: 260px; overflow-y: auto; }
    footer { text-align: center; padding: 20px; color: #9ca3af; font-size: 0.76rem;
              border-top: 1px solid #e5e7eb; margin-top: 8px; }
    @media (max-width: 600px) {
      header, .container { padding-left: 16px; padding-right: 16px; }
      header h1 { font-size: 1.35rem; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Architecture: ${esc(title)}</h1>
    <div class="meta">Generated ${esc(generatedAt)} &nbsp;·&nbsp; Reload page to see diagram updates</div>
  </header>

  <div class="container">
    <nav id="toc">
      <h2>Diagrams in this document</h2>
      <ul>
        ${tocItems}
      </ul>
    </nav>

    ${sections}
  </div>

  <footer>architecture-designer &nbsp;·&nbsp; MermaidJS v11.16 &nbsp;·&nbsp; Reload to reflect diagram changes</footer>

  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.esm.min.mjs';
    import elkLayouts from 'https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.1.4/dist/mermaid-layout-elk.esm.min.mjs';

    mermaid.registerLayoutLoaders(elkLayouts);

    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      fontFamily: 'system-ui, sans-serif',
      er: { useMaxWidth: false },
      sequence: { useMaxWidth: false },
      flowchart: { useMaxWidth: false, nodeSpacing: 60, rankSpacing: 80 },
      c4: { useMaxWidth: false },
    });

    // Render each diagram individually so errors appear on the page, not just in DevTools
    const mermaidEls = Array.from(document.querySelectorAll('.mermaid'));
    await Promise.allSettled(
      mermaidEls.map(async (el) => {
        const section = el.closest('.diagram-section');
        const id = section?.dataset?.id ?? ('d' + Math.random().toString(36).slice(2));
        const code = el.textContent;
        try {
          const { svg } = await mermaid.render('mermaid-render-' + id, code);
          const tmp = document.createElement('div');
          tmp.innerHTML = svg;
          const svgEl = tmp.firstElementChild;
          if (svgEl) el.replaceWith(svgEl);
        } catch (renderErr) {
          const msg = String(renderErr.message ?? renderErr)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
          const errDiv = document.createElement('div');
          errDiv.className = 'render-error';
          errDiv.innerHTML = '<strong>⚠ Mermaid render error in &ldquo;' + id + '&rdquo;</strong><pre>' + msg + '</pre>';
          el.replaceWith(errDiv);
          console.error('Mermaid render error [' + id + ']:', renderErr);
        }
      })
    );

    // ── Per-diagram zoom / pan / download ───────────────────────────────────
    const states = {};

    document.querySelectorAll('.diagram-section').forEach(section => {
      const id = section.dataset.id;
      const viewport = section.querySelector('.diagram-viewport');
      const inner = section.querySelector('.diagram-inner');
      if (!viewport || !inner) return;

      const svg = inner.querySelector('svg');
      if (svg) {
        svg.removeAttribute('style');
        svg.style.maxWidth = 'none';
        svg.style.height = 'auto';
        svg.style.display = 'block';
      }

      states[id] = { scale: 1, x: 0, y: 0 };

      function applyTransform() {
        const s = states[id];
        inner.style.transform = \`translate(\${s.x}px, \${s.y}px) scale(\${s.scale})\`;
        const el = section.querySelector('.zoom-level');
        if (el) el.textContent = Math.round(s.scale * 100) + '%';
      }

      // Zoom buttons
      section.querySelector('.btn-zoom-in')?.addEventListener('click', () => {
        states[id].scale = Math.min(8, states[id].scale * 1.25);
        applyTransform();
      });
      section.querySelector('.btn-zoom-out')?.addEventListener('click', () => {
        states[id].scale = Math.max(0.1, states[id].scale / 1.25);
        applyTransform();
      });
      section.querySelector('.btn-reset')?.addEventListener('click', () => {
        states[id] = { scale: 1, x: 0, y: 0 };
        applyTransform();
      });

      // Mouse wheel zoom (cursor-centered)
      viewport.addEventListener('wheel', (e) => {
        e.preventDefault();
        const rect = viewport.getBoundingClientRect();
        const cx = e.clientX - rect.left;
        const cy = e.clientY - rect.top;
        const factor = e.deltaY < 0 ? 1.1 : 0.9;
        const s = states[id];
        const newScale = Math.min(8, Math.max(0.1, s.scale * factor));
        s.x = cx - (cx - s.x) * (newScale / s.scale);
        s.y = cy - (cy - s.y) * (newScale / s.scale);
        s.scale = newScale;
        applyTransform();
      }, { passive: false });

      // Touch pinch zoom
      let lastPinchDist = null;
      let lastPinchMid = null;
      viewport.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
          lastPinchDist = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
          );
          const rect = viewport.getBoundingClientRect();
          lastPinchMid = {
            x: (e.touches[0].clientX + e.touches[1].clientX) / 2 - rect.left,
            y: (e.touches[0].clientY + e.touches[1].clientY) / 2 - rect.top,
          };
        }
      }, { passive: true });
      viewport.addEventListener('touchmove', (e) => {
        if (e.touches.length !== 2 || lastPinchDist === null) return;
        e.preventDefault();
        const dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const factor = dist / lastPinchDist;
        const s = states[id];
        const newScale = Math.min(8, Math.max(0.1, s.scale * factor));
        if (lastPinchMid) {
          s.x = lastPinchMid.x - (lastPinchMid.x - s.x) * (newScale / s.scale);
          s.y = lastPinchMid.y - (lastPinchMid.y - s.y) * (newScale / s.scale);
        }
        s.scale = newScale;
        applyTransform();
        lastPinchDist = dist;
      }, { passive: false });
      viewport.addEventListener('touchend', () => {
        lastPinchDist = null; lastPinchMid = null;
      }, { passive: true });

      // Mouse drag pan
      let dragStart = null;
      viewport.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return;
        dragStart = { ox: states[id].x, oy: states[id].y, mx: e.clientX, my: e.clientY };
        e.preventDefault();
      });
      window.addEventListener('mousemove', (e) => {
        if (!dragStart) return;
        states[id].x = dragStart.ox + (e.clientX - dragStart.mx);
        states[id].y = dragStart.oy + (e.clientY - dragStart.my);
        applyTransform();
      });
      window.addEventListener('mouseup', () => { dragStart = null; });

      // PNG download
      section.querySelector('.btn-download')?.addEventListener('click', async () => {
        const svgEl = inner.querySelector('svg');
        if (!svgEl) { alert('Diagram SVG not found — it may still be rendering.'); return; }

        // Use viewBox for natural dimensions to avoid zoom/pan transform skew from getBoundingClientRect
        let W = 0, H = 0;
        const vb = svgEl.getAttribute('viewBox');
        if (vb) {
          const parts = vb.trim().split(/[\s,]+/);
          if (parts.length >= 4) { W = Math.round(parseFloat(parts[2])); H = Math.round(parseFloat(parts[3])); }
        }
        if (!W || !H) {
          W = Math.round(parseFloat(svgEl.getAttribute('width'))) || 0;
          H = Math.round(parseFloat(svgEl.getAttribute('height'))) || 0;
        }
        if (!W || !H) {
          const rect = svgEl.getBoundingClientRect();
          W = Math.round(rect.width); H = Math.round(rect.height);
        }
        W = Math.max(W, 200); H = Math.max(H, 200);
        const DPR = Math.max(window.devicePixelRatio || 1, 2);

        const clone = svgEl.cloneNode(true);
        clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        clone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
        clone.setAttribute('width', String(W));
        clone.setAttribute('height', String(H));
        clone.removeAttribute('style');

        const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        bg.setAttribute('x', '0'); bg.setAttribute('y', '0');
        bg.setAttribute('width', '100%'); bg.setAttribute('height', '100%');
        bg.setAttribute('fill', 'white');
        clone.insertBefore(bg, clone.firstChild);

        const svgStr = new XMLSerializer().serializeToString(clone);
        // data URI avoids blob-URL cross-origin canvas taint that silently breaks toBlob() in some browsers
        const dataUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgStr);

        const filename = (section.dataset.title || id)
          .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '.png';

        try {
          await new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
              try {
                const canvas = document.createElement('canvas');
                canvas.width = Math.round(W * DPR);
                canvas.height = Math.round(H * DPR);
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.scale(DPR, DPR);
                ctx.drawImage(img, 0, 0, W, H);
                canvas.toBlob((pngBlob) => {
                  if (!pngBlob) { reject(new Error('PNG blob generation failed')); return; }
                  const a = document.createElement('a');
                  a.download = filename;
                  a.href = URL.createObjectURL(pngBlob);
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
                  resolve();
                }, 'image/png');
              } catch (e) { reject(e); }
            };
            img.onerror = () => reject(new Error('SVG image load failed'));
            img.src = dataUrl;
          });
        } catch (err) {
          alert(\`Download failed: \${err.message}\`);
        }
      });

      applyTransform();
    });
  </script>
</body>
</html>`;
}

// ── HTTP server ──────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${port}`);
  if (url.pathname !== '/' && url.pathname !== '/index.html') {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not found');
    return;
  }

  try {
    const raw = fs.readFileSync(DIAGRAMS_PATH, 'utf8');
    const data = JSON.parse(raw);
    const html = buildHtml(data);
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store',
    });
    res.end(html);
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(
      `Failed to load diagrams.json.\n\n` +
      `Expected file: ${DIAGRAMS_PATH}\n\n` +
      `Error: ${err.message}\n\n` +
      `Make sure the architecture-designer skill has written diagrams.json before starting the server.`
    );
  }
});

server.on('error', (err) => {
  process.stderr.write(`Server error: ${err.message}\n`);
  process.exit(1);
});

server.listen(port, '127.0.0.1', () => {
  const url = `http://localhost:${port}`;
  process.stdout.write(`\nArchitecture preview server running at ${url}\n`);
  process.stdout.write(`Diagrams source: ${DIAGRAMS_PATH}\n`);
  process.stdout.write(`Reload the browser page to reflect any diagram updates.\n`);
  process.stdout.write(`Leave this server running — there is no stop script.\n\n`);

  // Open browser cross-platform
  let cmd, args;
  switch (process.platform) {
    case 'win32':
      cmd = 'cmd';
      args = ['/c', 'start', '', url];
      break;
    case 'darwin':
      cmd = 'open';
      args = [url];
      break;
    default:
      cmd = 'xdg-open';
      args = [url];
  }
  const child = spawn(cmd, args, { detached: true, stdio: 'ignore' });
  child.on('error', () => {
    process.stderr.write(`Warning: could not open browser automatically.\n`);
    process.stderr.write(`Please open ${url} manually in your browser.\n`);
  });
  child.unref();
});
