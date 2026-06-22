#!/usr/bin/env python3
# OAuth2 Authorization Code flow for AniList — reuses the same public client
# registration as curd (https://github.com/wraient/curd), so no app registration
# is required from the user. client_id/secret below are curd's published values,
# tied to the localhost:8000/oauth/callback redirect URI used here.
import sys
import json
import os
import time
import webbrowser
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

if len(sys.argv) < 2:
    print("Usage: anilist_auth.py <token_file>", file=sys.stderr)
    sys.exit(1)

token_file = sys.argv[1]
CLIENT_ID = "20686"
CLIENT_SECRET = "APfx41cOgSQVMvi88v7PbN7g6kzed2ZQRcxmACod"
PORT = 8000
REDIRECT_URI = f"http://localhost:{PORT}/oauth/callback"

auth_url = (
    "https://anilist.co/api/v2/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&response_type=code"
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

print("Opening browser for AniList authentication...")
print(f"If the browser doesn't open automatically, visit:\n{auth_url}\n")
webbrowser.open(auth_url)

t.join(timeout=300)
server.server_close()

if received["error"]:
    print(f"ERROR: AniList returned an error: {received['error']}", file=sys.stderr)
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
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "code": code,
}).encode()

req = urllib.request.Request(
    "https://anilist.co/api/v2/oauth/token",
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

token["expires_at"] = time.time() + token.get("expires_in", 31536000)

os.makedirs(os.path.dirname(os.path.abspath(token_file)), exist_ok=True)
with open(token_file, "w") as f:
    json.dump(token, f)

print("AniList authentication successful!")
print(f"Token valid for ~{token.get('expires_in', 31536000) // 86400} days.")
