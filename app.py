from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello! This is the home page."

@app.route("/oauth/callback")
def oauth_callback():
    # Patreon will send data here after user clicks Allow
    code = request.args.get("code")
    state = request.args.get("state")

    # For now, just show the data we received
    return f"Received code: {code}, state: {state}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
