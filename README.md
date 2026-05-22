# krono-cli

A CLI tool to stream and track TV shows from your terminal, inspired by [ani-cli](https://github.com/pystardust/ani-cli).

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

## Usage

```bash
krono-cli "Breaking Bad"     # search and stream
krono-cli --list             # show tracked shows
krono-cli --remove <tmdb_id> # remove from history
```

After watching an episode, hit Enter to auto-advance to the next one. Progress is saved to `~/.local/state/krono-cli/history.tsv`.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `KRONO_PLAYER` | `mpv` | Media player to use |
| `KRONO_QUALITY` | `1080p` | Preferred quality (1080p, 720p, 480p, 4K) |

## Credits

- Stream decryption approach inspired by [Videasy.net-Decryptor](https://github.com/walterwhite-69/Videasy.net-Decryptor)
- CLI structure inspired by [ani-cli](https://github.com/pystardust/ani-cli)
