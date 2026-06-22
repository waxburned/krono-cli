#!/usr/bin/env python3
import sys
import json
import urllib.request

ALLANIME_API = "https://api.allanime.day/api"
ALLANIME_REF = "https://allanime.to"

query = sys.argv[1] if len(sys.argv) > 1 else ""
trans_type = sys.argv[2] if len(sys.argv) > 2 else "sub"

if not query:
    sys.exit(1)

gql = json.dumps({
    "query": (
        "query($search:SearchInput,$limit:Int,$page:Int,$translationType:VaildTranslationTypeEnumType,"
        "$countryOrigin:VaildCountryOriginEnumType){"
        "shows(search:$search,limit:$limit,page:$page,translationType:$translationType,"
        "countryOrigin:$countryOrigin){edges{_id name availableEpisodes malId}}}"
    ),
    "variables": {
        "search": {"allowAdult": False, "query": query},
        "limit": 40,
        "page": 1,
        "translationType": trans_type,
        "countryOrigin": "ALL"
    }
}).encode()

req = urllib.request.Request(
    ALLANIME_API,
    data=gql,
    headers={
        "Content-Type": "application/json",
        "Referer": ALLANIME_REF,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    },
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

edges = (data.get("data", {}) or {}).get("shows", {}).get("edges", []) or []
for edge in edges:
    show_id = edge.get("_id", "")
    name = (edge.get("name", "") or "").replace("\t", " ")
    mal_id = str(edge.get("malId") or "")
    avail = edge.get("availableEpisodes", {}) or {}
    ep_count = avail.get(trans_type) or avail.get("sub") or 0
    if show_id and name:
        print(f"{show_id}\t{name}\t{ep_count}\t{mal_id}")
