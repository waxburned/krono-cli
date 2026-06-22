#!/usr/bin/env python3
# Fetch the authenticated user's "Currently Watching" (+ Repeating) anime list.
import sys
import json
import urllib.request

ANILIST_GQL = "https://graphql.anilist.co"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def gql(query, variables, token):
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        ANILIST_GQL,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    if len(sys.argv) < 2:
        print("Usage: anilist_watching.py <token>", file=sys.stderr)
        sys.exit(1)
    token = sys.argv[1]

    viewer = gql("query{Viewer{id}}", {}, token)
    viewer_id = ((viewer.get("data") or {}).get("Viewer") or {}).get("id")
    if not viewer_id:
        print("Could not resolve AniList viewer id", file=sys.stderr)
        sys.exit(1)

    query = """
    query($userId: Int) {
        MediaListCollection(userId: $userId, type: ANIME, status_in: [CURRENT, REPEATING]) {
            lists {
                entries {
                    progress
                    media {
                        id
                        idMal
                        episodes
                        title { romaji english }
                    }
                }
            }
        }
    }
    """
    data = gql(query, {"userId": viewer_id}, token)
    lists = ((data.get("data") or {}).get("MediaListCollection") or {}).get("lists", []) or []

    for lst in lists:
        for entry in lst.get("entries", []) or []:
            media = entry.get("media") or {}
            titles = media.get("title") or {}
            display_title = (titles.get("english") or titles.get("romaji") or "").replace("\t", " ")
            romaji_title = (titles.get("romaji") or display_title).replace("\t", " ")
            mal_id = str(media.get("idMal") or "")
            progress = entry.get("progress") or 0
            episodes = media.get("episodes")
            episodes = str(episodes) if episodes else ""
            print(f"{media.get('id')}\t{mal_id}\t{display_title}\t{progress}\t{episodes}\t{romaji_title}")


if __name__ == "__main__":
    main()
