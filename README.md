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
krono-cli -p Breaking Bad         # pick source manually for a TV show
krono-cli --movie -p Inception    # pick source manually for a movie
krono-cli --list                  # show tracked shows and progress
krono-cli --remove <tmdb_id>      # remove a show from history
```

After watching an episode, hit Enter to auto-advance to the next one. Progress is saved to `~/.local/state/krono-cli/history.tsv`.

## Source Picker (-p)

The `-p` / `--pick` flag probes all available sources in parallel and lets you choose before playback starts:

```
Pick source:
  cdn             545ms  subs: ✓
  mb-flix         1.2s   subs: ✗
  downloader2     1.8s   subs: ✓
```

Sources that fail verification are excluded from the list automatically.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `KRONO_PLAYER` | `mpv` | Media player to use |
| `KRONO_QUALITY` | `1080p` | Preferred quality (1080p, 720p, 480p, 4K) |
| `KRONO_DEBUG` | `0` | Set to `1` to show provider debug output |

## Troubleshooting

**"No stream URL found"** — Ensure you ran `npm install` after cloning. Missing node dependencies will cause silent decryption failures.

**"No working sources found"** — If you have a restrictive outbound firewall (e.g. `ufw default deny outgoing`), ensure outbound HTTPS is allowed:

```bash
sudo ufw allow out 443/tcp
```

## Credits

- Stream decryption approach inspired by [Videasy.net-Decryptor](https://github.com/walterwhite-69/Videasy.net-Decryptor)
- CLI structure inspired by [ani-cli](https://github.com/pystardust/ani-cli)
