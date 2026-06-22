# krono-cli

> **Disclaimer:** krono-cli is intended for educational purposes only. It does not host or distribute any content. All streams are sourced from third-party services. Use at your own risk and in accordance with the laws of your country.

A CLI tool to stream and track TV shows and movies from your terminal, inspired by [ani-cli](https://github.com/pystardust/ani-cli).

## Platform Support

| Platform | Status |
|---|---|
| Linux | ✅ Fully supported |
| macOS | ✅ Should work (install deps via homebrew) |
| Windows | ✅ Supported via Git Bash (see [windows branch](https://github.com/waxburned/krono-cli/tree/windows)) |

## Dependencies

- `fzf` — interactive selection
- `mpv` — media player
- `node` (18+) — stream decryption
- `curl` — HTTP requests
- `python3` — parsing
- `openssl` — anime stream decryption (already present on Linux/macOS/Git Bash)

## Installation

```bash
git clone https://github.com/waxburned/krono-cli
cd krono-cli
npm install
ln -s "$PWD/krono-cli" ~/.local/bin/krono-cli
```

> All 4 steps are required. `npm install` installs decryption dependencies; the `ln -s` line lets you run `krono-cli` from anywhere.

## Usage

```bash
krono-cli Breaking Bad            # search and stream a TV show
krono-cli --movie Inception       # search and stream a movie
krono-cli --anime                 # anime menu: continue from AniList or search
krono-cli --anime kaiju no 8      # search and stream an anime directly (subbed by default)
krono-cli --anime --dub one piece # search and stream an anime, dubbed
krono-cli -p Breaking Bad         # pick source manually for a TV show
krono-cli --movie -p Inception    # pick source manually for a movie
krono-cli --anime -p kaiju no 8   # pick source manually for an anime (sub + dub)
krono-cli --list                  # show tracked shows and progress
krono-cli --remove <tmdb_id>      # remove a show from history
krono-cli --mal-auth              # authenticate with MyAnimeList
krono-cli --anilist-auth          # authenticate with AniList
```

After watching an episode, hit Enter to auto-advance to the next one. Progress is saved to `~/.local/state/krono-cli/history.tsv` (anime to `anime_history.tsv`).

## Source Picker (-p)

The `-p` / `--pick` flag probes all available sources in parallel and lets you choose before playback starts:

```
Pick source:
  cdn             545ms  subs: ✓
  mb-flix         1.2s   subs: ✗
  downloader2     1.8s   subs: ✓
```

For anime, both sub and dub variants are probed across every provider at once, so you can pick exactly which audio/sub combination you want:

```
Pick source:
  Mp4          sub    480ms
  Luf-Mp4      sub    1.1s
  Mp4          dub    610ms
  Fm-Hls       dub    1.4s
```

Sources that fail verification are excluded from the list automatically.

## Anime (allanime)

Anime search, episode listing, and streaming go through the same allanime backend used by [ani-cli](https://github.com/pystardust/ani-cli) and [curd](https://github.com/wraient/curd). No extra setup needed.

Running `krono-cli --anime` with no title opens a menu:

```bash
krono-cli --anime
# Anime:
#   Currently Watching (AniList)
#   Search anime
```

"Currently Watching" pulls your AniList list (requires `--anilist-auth`), matches each entry to allanime by MyAnimeList ID, and resumes from the next unwatched episode. "Search anime" behaves like a direct title search:

```bash
krono-cli --anime/-a [title]
krono-cli --anime --dub [title]   # dubbed audio instead of subbed
```

Anime progress is tracked separately from TV/movies in `~/.local/state/krono-cli/anime_history.tsv`, with resume support the same as shows.

## MyAnimeList Tracking

Watched anime episodes can auto-sync to your MyAnimeList list. Requires your own MAL API client (free, takes a minute):

1. Register an app at [myanimelist.net/apiconfig](https://myanimelist.net/apiconfig) (App Type: "other"; the redirect URI doesn't matter — krono-cli intercepts it locally)
2. Copy the Client ID
3. Run:

```bash
MAL_CLIENT_ID=<your_client_id> krono-cli --mal-auth
```

This opens your browser to authorize, then saves a token to `~/.local/state/krono-cli/mal_token.json`. After that, finishing an anime episode automatically updates your MAL list's watched-episode count. Tokens auto-refresh.

## AniList Tracking

AniList tracking works out of the box — no app registration required:

```bash
krono-cli --anilist-auth
```

This reuses the same public OAuth client [curd](https://github.com/wraient/curd) uses, so there's nothing to set up. Watched anime episodes automatically update your AniList progress (resolved via MyAnimeList ID when available, falling back to title search).

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `KRONO_PLAYER` | `mpv` | Media player to use |
| `KRONO_QUALITY` | `1080p` | Preferred quality (1080p, 720p, 480p, 4K) |
| `KRONO_DEBUG` | `0` | Set to `1` to show provider debug output |
| `MAL_CLIENT_ID` | — | Your MyAnimeList API client ID, needed for `--mal-auth` |

## Troubleshooting

**"No stream URL found"** — Ensure you ran `npm install` after cloning. Missing node dependencies will cause silent decryption failures.

**"No working sources found"** — If you have a restrictive outbound firewall (e.g. `ufw default deny outgoing`), ensure outbound HTTPS is allowed:

```bash
sudo ufw allow out 443/tcp
```

## Credits

- Stream decryption approach inspired by [Videasy.net-Decryptor](https://github.com/walterwhite-69/Videasy.net-Decryptor)
- CLI structure inspired by [ani-cli](https://github.com/pystardust/ani-cli)
