import json, sys, os

data = json.load(sys.stdin)
sources = data.get("data", {}).get("sources", [])
quality = os.environ.get("KRONO_QUALITY", "1080p").upper()

preferred = next((s for s in sources if s.get("quality", "").upper() == quality), None)
chosen = preferred or (sources[0] if sources else None)
if chosen:
    print(chosen["url"])
