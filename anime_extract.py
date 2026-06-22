#!/usr/bin/env python3
import sys
import json
import re
import urllib.request

ALLANIME_BASE = "allanime.day"
ALLANIME_REF = "https://youtu-chan.com"
AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0"

encoded = sys.argv[1] if len(sys.argv) > 1 else ""
provider = sys.argv[2] if len(sys.argv) > 2 else ""

CLOCK_PROVIDERS = {"Luf-Mp4", "Default"}


def hex_xor(s):
    s = s.strip()
    try:
        return bytes(int(s[i:i + 2], 16) ^ 56 for i in range(0, len(s), 2)).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def fetch(url, timeout=8):
    req = urllib.request.Request(url, headers={"Referer": ALLANIME_REF, "User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_clock(decoded_path):
    decoded_path = decoded_path.replace("/clock", "/clock.json")
    body = fetch(f"https://{ALLANIME_BASE}{decoded_path}")
    data = json.loads(body)
    links = data.get("links", []) or []
    hls = [l for l in links if l.get("hls") and l.get("link")]
    if hls:
        return hls[0]["link"]
    if links and links[0].get("link"):
        return links[0]["link"]
    return ""


def extract_mp4upload(embed_url):
    body = fetch(embed_url)
    m = re.search(r'src:\s*"([^"]+)"', body)
    return m.group(1) if m else ""


if not encoded:
    sys.exit(1)

referer = ALLANIME_REF
try:
    if provider in CLOCK_PROVIDERS or encoded.startswith("--"):
        hex_str = encoded.split("--")[-1]
        decoded = hex_xor(hex_str)
        if not decoded:
            sys.exit(1)
        url = extract_clock(decoded)
    elif provider == "Mp4":
        url = extract_mp4upload(encoded)
        referer = "https://mp4upload.com"
    else:
        # Ok (ok.ru), Sw (streamwish), Fm-Hls (filemoon) need provider-specific
        # unpacking we don't support yet — bare embed pages aren't playable streams.
        sys.exit(1)
except Exception:
    sys.exit(1)

if not url:
    sys.exit(1)
print(f"{url}\t{referer}")
