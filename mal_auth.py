#!/usr/bin/env python3
# OAuth2 PKCE (plain) flow for MyAnimeList — mirrors the approach used by curd
# (https://github.com/wraient/curd), which is the proven, working reference.
import sys
import json
import os
import time
import secrets
import string
import webbrowser
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

if len(sys.argv) < 3:
    print("Usage: mal_auth.py <client_id> <token_file>", file=sys.stderr)
    sys.exit(1)

client_id = sys.argv[1]
token_file = sys.argv[2]
PORT = 8123
REDIRECT_URI = f"http://localhost:{PORT}/oauth/callback"

CHARS = string.ascii_letters + string.digits + "-._~"
code_verifier = "".join(secrets.choice(CHARS) for _ in range(64))  # MAL PKCE: code_challenge == code_verifier

auth_url = (
    "https://myanimelist.net/v1/oauth2/authorize"
    f"?response_type=code"
    f"&client_id={urllib.parse.quote(client_id)}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&code_challenge={urllib.parse.quote(code_verifier)}"
)

received = {"code": None, "error": None}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        received["code"] = (qs.get("code") or [None])[0]
        received["error"] = (qs.get("error") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Authentication complete. You can close this tab and return to your terminal.</h2>")

    def log_message(self, *args):
        pass


server = HTTPServer(("localhost", PORT), Handler)
t = threading.Thread(target=server.handle_request)
t.daemon = True
t.start()

print("Opening browser for MyAnimeList authentication...")
print(f"If the browser doesn't open automatically, visit:\n{auth_url}\n")
webbrowser.open(auth_url)

t.join(timeout=300)
server.server_close()

if received["error"]:
    print(f"ERROR: MyAnimeList returned an error: {received['error']}", file=sys.stderr)
    sys.exit(1)

code = received["code"]
if not code:
    print("No callback received automatically.", file=sys.stderr)
    code = input("Paste the full callback URL or just the code: ").strip()
    if "code=" in code:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query).get("code", [""])[0]
    if not code:
        print("ERROR: No authorization code received", file=sys.stderr)
        sys.exit(1)

body = urllib.parse.urlencode({
    "client_id": client_id,
    "code": code,
    "code_verifier": code_verifier,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
}).encode()

req = urllib.request.Request(
    "https://myanimelist.net/v1/oauth2/token",
    data=body,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        token = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"ERROR: Token exchange failed: {e.read().decode()}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Token exchange failed: {e}", file=sys.stderr)
    sys.exit(1)

token["expires_at"] = time.time() + token.get("expires_in", 2592000)
token["client_id"] = client_id

os.makedirs(os.path.dirname(os.path.abspath(token_file)), exist_ok=True)
with open(token_file, "w") as f:
    json.dump(token, f)

print("MyAnimeList authentication successful!")
print(f"Token valid for ~{token.get('expires_in', 2592000) // 86400} days (refresh token saved for renewal).")
