"""
TEST FIXTURE — intentionally vulnerable Flask app for security-auditor demo.
DO NOT deploy. This file is used to demonstrate /audit and /audit-file detection.
"""
from flask import Flask, request, jsonify, redirect
import sqlite3
import os
import subprocess
import pickle
import base64

app = Flask(__name__)

# CWE-798: Hardcoded credentials
DB_PASSWORD = "super_secret_prod_123"
API_KEY = "sk-prod-abc123def456ghi789jkl"
JWT_SECRET = "jwt_signing_key_do_not_share"


def get_db():
    return sqlite3.connect("users.db")


@app.route("/users")
def get_user():
    username = request.args.get("username", "")
    conn = get_db()
    cursor = conn.cursor()
    # CWE-89: SQL Injection — direct string concatenation
    query = "SELECT id, username, email FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)


@app.route("/search")
def search():
    term = request.args.get("q", "")
    conn = get_db()
    cursor = conn.cursor()
    # CWE-89: SQL Injection via f-string
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{term}%'")
    return jsonify(cursor.fetchall())


@app.route("/run")
def run_command():
    cmd = request.args.get("cmd", "")
    # CWE-78: OS Command Injection
    result = os.system(cmd)
    return jsonify({"exit_code": result})


@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")
    # CWE-78: Command Injection via subprocess
    output = subprocess.check_output("ping -c 1 " + host, shell=True)
    return output


@app.route("/file")
def read_file():
    path = request.args.get("path", "")
    # CWE-22: Path Traversal — no sanitization
    full_path = "/var/app/data/" + path
    with open(full_path) as f:
        return f.read()


@app.route("/deserialize", methods=["POST"])
def deserialize():
    data = request.get_data()
    # CWE-502: Insecure Deserialization
    obj = pickle.loads(base64.b64decode(data))
    return jsonify({"result": str(obj)})


@app.route("/redirect")
def do_redirect():
    url = request.args.get("next", "/")
    # CWE-601: Open Redirect — no allowlist validation
    return redirect(url)


@app.route("/admin/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    # CWE-862: Missing Authorization — no admin check
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    return jsonify({"deleted": user_id})


@app.route("/eval")
def do_eval():
    expr = request.args.get("expr", "")
    # CWE-94: Code Injection via eval
    result = eval(expr)
    return jsonify({"result": result})


if __name__ == "__main__":
    # CWE-209: debug=True exposes stack traces in production
    app.run(debug=True, host="0.0.0.0")
