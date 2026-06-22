#!/usr/bin/env python3
import sys
import json
import base64
import hashlib
import subprocess
import urllib.request
import urllib.parse

ALLANIME_API = "https://api.allanime.day"
ALLANIME_REF = "https://youtu-chan.com"
AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0"
ALLANIME_KEY = hashlib.sha256(b"Xot36i3lK3:v1").digest()
PERSISTED_HASH = "d405d0edd690624b66baba3068e0edc3ac90f1597d898a1ec8db4e5c43c00fec"

EPISODE_GQL = (
    "query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, "
    "$episodeString: String!) { episode( showId: $showId translationType: $translationType "
    "episodeString: $episodeString ) { episodeString sourceUrls }}"
)

# Yt-mp4 (youtube embed) and S-mp4 (sharepoint) aren't directly streamable.
SKIP = {"Yt-mp4", "S-mp4"}


def decrypt_tobeparsed(blob_b64):
    blob = base64.b64decode(blob_b64)
    iv = blob[1:13]
    ct = blob[13:-16]
    ctr = iv + bytes.fromhex("00000002")
    p = subprocess.run(
        ["openssl", "enc", "-d", "-aes-256-ctr", "-K", ALLANIME_KEY.hex(), "-iv", ctr.hex(), "-nosalt", "-nopad"],
        input=ct, capture_output=True,
    )
    return p.stdout.decode("utf-8", errors="ignore")


def fetch_episode(show_id, episode, trans_type):
    query_vars = json.dumps({"showId": show_id, "translationType": trans_type, "episodeString": str(episode)})
    query_ext = json.dumps({"persistedQuery": {"version": 1, "sha256Hash": PERSISTED_HASH}})
    params = urllib.parse.urlencode({"variables": query_vars, "extensions": query_ext})
    url = f"{ALLANIME_API}/api?{params}"
    req = urllib.request.Request(url, headers={
        "Referer": ALLANIME_REF, "Origin": ALLANIME_REF, "User-Agent": AGENT,
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode())

    if "tobeparsed" in body.get("data", {}):
        plain = decrypt_tobeparsed(body["data"]["tobeparsed"])
        return json.loads(plain)

    # Fallback: raw POST query (may hit a captcha wall, but worth trying)
    req2 = urllib.request.Request(
        f"{ALLANIME_API}/api",
        data=json.dumps({
            "variables": {"showId": show_id, "translationType": trans_type, "episodeString": str(episode)},
            "query": EPISODE_GQL,
        }).encode(),
        headers={"Content-Type": "application/json", "Referer": ALLANIME_REF, "User-Agent": AGENT},
    )
    with urllib.request.urlopen(req2, timeout=15) as resp2:
        return json.loads(resp2.read().decode())


def main():
    show_id = sys.argv[1] if len(sys.argv) > 1 else ""
    episode = sys.argv[2] if len(sys.argv) > 2 else "1"
    trans_type = sys.argv[3] if len(sys.argv) > 3 else "sub"

    if not show_id:
        sys.exit(1)

    try:
        data = fetch_episode(show_id, episode, trans_type)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    episode_data = data.get("episode") or (data.get("data", {}) or {}).get("episode") or {}
    source_urls = episode_data.get("sourceUrls", []) or []

    for src in sorted(source_urls, key=lambda s: s.get("priority", 99), reverse=True):
        raw = src.get("sourceUrl", "")
        name = (src.get("sourceName", "") or "").replace("\t", "")
        priority = src.get("priority", 99)
        if not raw or not name or name in SKIP:
            continue
        print(f"{priority}\t{name}\t{raw}")


if __name__ == "__main__":
    main()
