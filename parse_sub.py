import json, sys

data = json.load(sys.stdin)
subs = data.get("data", {}).get("subtitles", [])
en = next((s for s in subs if "english" in s.get("language", "").lower()), None)
if en:
    print(en["url"])
