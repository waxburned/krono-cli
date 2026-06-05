#!/usr/bin/env python3
"""Read cached videasy session token. Set it with: krono-cli --set-session TOKEN"""
import json, os, sys, time

CACHE_FILE = os.path.join(
    os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")),
    "krono-cli", "session.json"
)

try:
    with open(CACHE_FILE) as f:
        d = json.load(f)
    if d.get("expiresAt", 0) > time.time() * 1000 + 60_000:
        print(d["token"], flush=True)
        sys.exit(0)
except Exception:
    pass

sys.exit(1)
