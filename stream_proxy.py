#!/usr/bin/env python3
"""HLS proxy: fetches stream via curl to bypass CDN TLS fingerprint blocking."""
import sys, subprocess, socket, threading, re, time, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urljoin, quote, unquote

BASE_URL = sys.argv[1]
READY_FILE = sys.argv[2] if len(sys.argv) > 2 else None
# argv[3]: explicit curl binary path passed from bash (the one confirmed to work)
CURL_BIN = sys.argv[3] if len(sys.argv) > 3 else 'curl'

CURL = [
    CURL_BIN, '-s', '-L', '--max-time', '30',
    '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    '-H', 'Referer: https://player.videasy.net/',
    '-H', 'Origin: https://player.videasy.net',
]

PORT = None

def fetch(url):
    r = subprocess.run(CURL + [url], capture_output=True, timeout=35, stdin=subprocess.DEVNULL)
    return r.stdout

def rewrite_m3u8(data, src_url):
    lines = []
    for line in data.decode('utf-8', errors='replace').splitlines():
        s = line.strip()
        if not s:
            lines.append(line)
        elif s.startswith('#'):
            lines.append(re.sub(
                r'URI="([^"]*)"',
                lambda m: f'URI="http://127.0.0.1:{PORT}/p?u={quote(urljoin(src_url, m.group(1)), safe="")}"',
                line))
        else:
            lines.append(f'http://127.0.0.1:{PORT}/p?u={quote(urljoin(src_url, s), safe="")}')
    return '\n'.join(lines).encode()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/stream.m3u8'):
            url = BASE_URL
        elif self.path.startswith('/p?u='):
            url = unquote(self.path[5:])
        else:
            self.send_error(404)
            return
        try:
            data = fetch(url)
        except Exception as e:
            print(f'[proxy] fetch error: {e}', file=sys.stderr, flush=True)
            self.send_error(502)
            return
        print(f'[proxy] got {len(data)} bytes, first: {data[:60]!r}', file=sys.stderr, flush=True)
        if data[:7] == b'#EXTM3U' or b'#EXT-X-' in data[:200]:
            data = rewrite_m3u8(data, url)
            ct = 'application/vnd.apple.mpegurl'
        else:
            ct = 'video/mp2t'
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f'[proxy] {self.path[:80]}', file=sys.stderr, flush=True)

class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def main():
    global PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        PORT = s.getsockname()[1]

    server = ThreadedServer(('127.0.0.1', PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    proxy_url = f'http://127.0.0.1:{PORT}/stream.m3u8'
    print(f'[proxy] port={PORT} curl={CURL_BIN}', file=sys.stderr, flush=True)
    if READY_FILE:
        with open(READY_FILE, 'wb') as f:
            f.write(proxy_url.encode())
    else:
        print(proxy_url, flush=True)

    while True:
        time.sleep(1)

main()
