# krono-cli

> **Disclaimer:** krono-cli is intended for educational purposes only. It does not host or distribute any content. All streams are sourced from third-party services. Use at your own risk and in accordance with the laws of your country.

A CLI tool to stream and track TV shows from your terminal, inspired by [ani-cli](https://github.com/pystardust/ani-cli).

## Platform Support

| Platform | Status |
|---|---|
| Linux | ✅ Fully supported |
| macOS | ✅ Should work (install deps via homebrew) |
| Windows | ✅ Supported via Git Bash (see [Windows Setup](#windows-setup)) |

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

## Windows Setup

### 1. Install Git for Windows

Download and install from [git-scm.com](https://git-scm.com/download/win). This gives you Git Bash, which is the shell krono-cli runs in on Windows.

### 2. Install dependencies via Scoop

Open **PowerShell** and run:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
scoop bucket add extras
scoop install fzf mpv nodejs python
```

### 3. Clone and set up krono-cli

Open **Git Bash** and run:

```bash
git clone https://github.com/waxburned/krono-cli ~/krono-cli
cd ~/krono-cli
git checkout windows
npm install
```

### 4. Add to PATH

Add these lines to `~/.bashrc` (create it if it doesn't exist):

```bash
export PATH="$PATH:/c/Users/$USERNAME/scoop/shims"
export PATH="$PATH:/c/Users/$USERNAME/scoop/apps/mpv/current"
export PATH="$PATH:/c/Users/$USERNAME/scoop/apps/nodejs/current"
export PATH="$PATH:$HOME/krono-cli"
```

Then create a shim so Git Bash can find mpv:

```bash
printf '#!/bin/bash\nexec "/c/Users/$USERNAME/scoop/apps/mpv/current/mpv.exe" "$@"\n' > /c/Users/$USERNAME/scoop/shims/mpv
chmod +x /c/Users/$USERNAME/scoop/shims/mpv
```

### 5. Run

Open a new Git Bash window and run:

```bash
krono-cli "Breaking Bad"
```

## Credits

- Stream decryption approach inspired by [Videasy.net-Decryptor](https://github.com/walterwhite-69/Videasy.net-Decryptor)
- CLI structure inspired by [ani-cli](https://github.com/pystardust/ani-cli)
