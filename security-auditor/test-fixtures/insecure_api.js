/**
 * TEST FIXTURE — intentionally vulnerable Express API for security-auditor demo.
 * DO NOT deploy. Used to demonstrate /audit and /audit-file detection.
 */
const express = require("express");
const { exec, execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const serialize = require("serialize-javascript");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// CWE-798: Hardcoded credentials
const JWT_SECRET = "hardcoded_jwt_secret_key_abc123";
const DB_URL = "mongodb://admin:password123@prod-db.internal:27017/appdb";
const STRIPE_KEY = "sk_live_[REDACTED_DEMO_FIXTURE]";

// CWE-79: Reflected XSS — user input rendered directly in HTML response
app.get("/search", (req, res) => {
  const query = req.query.q || "";
  res.setHeader("Content-Type", "text/html");
  res.send(`
    <html><body>
      <h1>Search results for: ${query}</h1>
    </body></html>
  `);
});

// CWE-78: OS Command Injection via exec with user input
app.post("/convert", (req, res) => {
  const filename = req.body.filename;
  exec(`convert uploads/${filename} output/${filename}.pdf`, (err, stdout, stderr) => {
    if (err) return res.status(500).json({ error: stderr });
    res.json({ output: stdout, file: `output/${filename}.pdf` });
  });
});

// CWE-78: Command injection via execSync
app.get("/ping", (req, res) => {
  const host = req.query.host;
  const result = execSync(`ping -c 3 ${host}`).toString();
  res.json({ result });
});

// CWE-22: Path Traversal — path.join does not sanitize ../ sequences
app.get("/static/:filename", (req, res) => {
  const filePath = path.join(__dirname, "public", req.params.filename);
  res.sendFile(filePath);
});

// CWE-601: Open Redirect — no destination validation
app.get("/redirect", (req, res) => {
  const destination = req.query.url;
  res.redirect(destination);
});

// CWE-862: No authorization check on admin endpoint
app.delete("/admin/users/:id", (req, res) => {
  // Deletes user without verifying the caller is an admin
  const userId = req.params.id;
  res.json({ message: `User ${userId} deleted`, success: true });
});

// CWE-639: IDOR — user can access any order by changing the ID
app.get("/orders/:orderId", (req, res) => {
  // No check that req.user.id owns this order
  const orderId = req.params.orderId;
  res.json({ orderId, items: ["item1", "item2"], userId: "any" });
});

// CWE-502: Insecure deserialization — eval-based deserialization
app.post("/state", (req, res) => {
  const state = req.body.state;
  // eval used to deserialize state from client
  const parsed = eval("(" + state + ")");
  res.json({ restored: parsed });
});

// CWE-918: SSRF — fetches user-controlled URL without allowlist
app.get("/proxy", async (req, res) => {
  const targetUrl = req.query.url;
  const response = await fetch(targetUrl);
  const data = await response.text();
  res.send(data);
});

// CWE-352: Missing CSRF protection on state-changing POST
app.post("/profile/update", (req, res) => {
  const { email, username } = req.body;
  // No CSRF token validated
  res.json({ updated: { email, username } });
});

app.listen(3000, () => {
  console.log("Server running on port 3000");
});

module.exports = app;
