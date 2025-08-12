from flask import Flask, request, jsonify
import sqlite3
import requests
import time

app = Flask(__name__)
DB_FILE = "database.db"
CLIENT_ID = "G-VKLJT-nGjdbLSOgjc5fYdSCWACzqOJA8DDOk5T4yMAPRZ11KQi0_-aa1chNsnQ"

# Ensure table exists
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS oauth_token (
            id TEXT PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            expires_in INTEGER,
            expires_at INTEGER,
            scope TEXT,
            token_type TEXT
        )
    """)
    conn.commit()
    conn.close()

# Store token data in DB
def store_token(id_value, token_data):
    expires_in = token_data.get("expires_in")
    expires_at = int(time.time()) + int(expires_in) if expires_in else None

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO oauth_token 
        (id, access_token, refresh_token, expires_in, expires_at, scope, token_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        id_value,
        token_data.get("access_token"),
        token_data.get("refresh_token"),
        expires_in,
        expires_at,
        token_data.get("scope"),
        token_data.get("token_type")
    ))
    conn.commit()
    conn.close()

# Get token record from DB
def get_token(id_value):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows dict-like access
    c = conn.cursor()
    c.execute("SELECT * FROM oauth_token WHERE id = ?", (id_value,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    session_id = request.args.get("state")

    token_url = "https://www.patreon.com/api/oauth2/token"
    payload = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": "https://test-patreon-oauth-handler.onrender.com/oauth/callback"
    }

    resp = requests.post(token_url, data=payload)
    token_data = resp.json()

    store_token(session_id, token_data)

    return jsonify({"message": "Token stored successfully"})

@app.route("/oauth/token/<session_id>")
def oauth_token_session_id(session_id):
    token_record = get_token(session_id)
    if token_record:
        return jsonify({"data": token_record})
    return jsonify({"error": "Token not found"}), 404

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
