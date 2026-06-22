#!/usr/bin/env python3
# Update (or create) an AniList list entry's progress, resolving the AniList
# media id from a MyAnimeList id when available, falling back to title search.
import sys
import json
import time
import urllib.request

ANILIST_GQL = "https://graphql.anilist.co"


def gql(query, variables, token=None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        ANILIST_GQL,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def resolve_media_id(mal_id, title, token):
    if mal_id and str(mal_id) not in ("", "0", "null"):
        try:
            data = gql(
                "query($idMal:Int){Media(idMal:$idMal,type:ANIME){id}}",
                {"idMal": int(mal_id)},
                token,
            )
            media = (data.get("data", {}) or {}).get("Media")
            if media and media.get("id"):
                return media["id"]
        except Exception:
            pass
    if title:
        try:
            data = gql(
                "query($search:String){Media(search:$search,type:ANIME){id}}",
                {"search": title},
                token,
            )
            media = (data.get("data", {}) or {}).get("Media")
            if media and media.get("id"):
                return media["id"]
        except Exception:
            pass
    return None


def main():
    if len(sys.argv) < 5:
        print("Usage: anilist_update.py <token> <mal_id> <title> <episode>", file=sys.stderr)
        sys.exit(1)

    token, mal_id, title, episode = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

    media_id = resolve_media_id(mal_id, title, token)
    if not media_id:
        print(f"Could not resolve AniList id for '{title}'", file=sys.stderr)
        sys.exit(1)

    mutation = """
    mutation($mediaId: Int, $progress: Int, $status: MediaListStatus) {
        SaveMediaListEntry(mediaId: $mediaId, progress: $progress, status: $status) {
            id
            progress
            status
        }
    }
    """
    variables = {"mediaId": media_id, "progress": episode, "status": "CURRENT"}
    try:
        result = gql(mutation, variables, token)
    except Exception as e:
        print(f"AniList update failed: {e}", file=sys.stderr)
        sys.exit(1)

    if "errors" in result:
        print(f"AniList update failed: {result['errors']}", file=sys.stderr)
        sys.exit(1)

    print(f"AniList updated: media {media_id} -> episode {episode}")


if __name__ == "__main__":
    main()
