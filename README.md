# Freenet Headless Deploy

[![License: MIT](https://img.shields.io/badge/License-MIT-30d158.svg)](./LICENSE)
[![Freenet Protocol](https://img.shields.io/badge/Freenet-v0.2.114%2B-007FFF.svg)](https://freenet.org)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-Universal-ffffff.svg)](./SKILL.md)

**Automated CLI tool & universal AI agent skill for packaging, building, and hosting static web applications on Freenet with 24/7 headless daemon availability.**

- **Clearnet Gateway**: [https://headless.robdoit.work/skills](https://headless.robdoit.work/skills)
- **Freenet Contract Locator**: `freenet:CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi/skills.html`
- **Local Freenet Gateway**: `http://127.0.0.1:7509/v1/contract/web/CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi/skills.html`
- **Freenet Atlas Directory**: `http://127.0.0.1:7509/v1/contract/web/771DvtPMwt2PumPyrFvsz7fpvU1gogcmb5qtS1yYEEH9/`

---

## Terminal Preview

```text
$ python3 scripts/deploy_freenet_headless.py --dir ./public --key my-site-key --check-node

✅ Local Freenet gateway (http://127.0.0.1:7509) is online.
🧹 Staging assets from './public' to './freenet_staging'...
✨ Transformed root-relative asset paths across 27 file(s).
🚀 Publishing website to Freenet network (key: my-site-key)...

🎉 Freenet Headless Deployment Complete!
🔗 Contract ID       : CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi
🌐 Local Gateway URL : http://127.0.0.1:7509/v1/contract/web/CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi/
📍 Freenet Locator   : freenet:CvvqJDgMBUtqWiXqEypXLU9cXFNMhFuPruPPdZ4NWuPi/
```

---

## Why Freenet Headless Deploy?

Hosting a web application on the decentralized [Freenet](https://freenet.org) network typically requires solving three hurdles:
1. **Subpath Asset Resolution**: Freenet serves web contracts under `/v1/contract/web/<CONTRACT_ID>/`. Standard root-relative links (`/style.css`, `/app.js`, `/skills`) break unless rewritten to subpath-safe relative references (`./style.css`, `./app.js`, `./skills.html`).
2. **Idempotent Key & Contract Lifecycle**: Distinguishing between initializing a new signing keypair (`fdev website init`), publishing for the first time (`fdev website publish`), and updating an existing live contract (`fdev website update`).
3. **24/7 Headless Availability & Discovery**: Running Freenet as a persistent background system service (`freenet service`) and formatting signed metadata for discovery on **Freenet Atlas**.

**Freenet Headless Deploy** automates the entire pipeline in a single zero-dependency Python 3 script and provides a drop-in `SKILL.md` for AI coding agents.

---

## Quickstart

### 1. Prerequisites

Ensure the Rust toolchain, WASM target, `freenet` node binary, and `fdev` developer CLI are installed and the background service is running:

```bash
# Install Rust & WASM target
command -v rustc >/dev/null 2>&1 || curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
rustup target add wasm32-unknown-unknown

# Install Freenet core node and fdev CLI
cargo install freenet fdev

# Install and start the 24/7 headless background service
freenet service install
freenet service start
freenet service status
```

### 2. Standalone 1-Line `curl` Install (Optional)

If you only want the standalone deployment script in your current project without cloning the full repository:

```bash
curl -sSL https://raw.githubusercontent.com/robdoit/freenet-headless-deploy/main/scripts/deploy_freenet_headless.py -o deploy_freenet_headless.py
```

### 3. Deploy Any Static Website in One Command

```bash
python3 scripts/deploy_freenet_headless.py \
  --dir ./public \
  --key my-site-key \
  --check-node \
  --print-atlas
```

### 4. Dry-Run & Inspect Staged Assets

Preview all asset path transformations without publishing to the network:

```bash
python3 scripts/deploy_freenet_headless.py \
  --dir ./public \
  --key my-site-key \
  --dry-run \
  --print-atlas
```

---

## AI Coding Agent Integration

`Freenet Headless Deploy` follows the universal [`SKILL.md`](./SKILL.md) specification and works out of the box with major AI coding assistants:

### Claude Code
```bash
mkdir -p .claude/skills/freenet-headless-deploy
cp -r SKILL.md scripts/ .claude/skills/freenet-headless-deploy/
```

### Cursor / Windsurf / Cline / GitHub Copilot / Aider
```bash
mkdir -p .agents/skills/freenet-headless-deploy
cp -r SKILL.md scripts/ .agents/skills/freenet-headless-deploy/
```
Or reference [`SKILL.md`](./SKILL.md) directly in your `.cursorrules` or repository instructions.

---

## CLI Reference

```text
usage: deploy_freenet_headless.py [-h] --dir DIR --key KEY [--staging STAGING]
                                  [--timeout TIMEOUT] [--dry-run]
                                  [--check-node] [--print-atlas]
                                  [--atlas-path ATLAS_PATH]

Options:
  --dir DIR                 Path to static website directory (must contain index.html)
  --key KEY                 Name of website signing keypair (e.g. my-site-key)
  --staging STAGING         Path to staging output directory (default: ./freenet_staging)
  --timeout TIMEOUT         Maximum seconds to wait for Freenet node response (default: 300)
  --dry-run                 Transform assets into staging directory without publishing
  --check-node              Verify local Freenet HTTP gateway (127.0.0.1:7509) before deploying
  --print-atlas             Output ready-to-run Freenet Atlas registration & River commands
  --atlas-path ATLAS_PATH   Subpath within the contract to index in Freenet Atlas (default: /)
```

---

## Indexing on Freenet Atlas

[Freenet Atlas](https://github.com/freenet/atlas) (`http://127.0.0.1:7509/v1/contract/web/771DvtPMwt2PumPyrFvsz7fpvU1gogcmb5qtS1yYEEH9/`) is the decentralized discovery layer for Freenet.

Running `deploy_freenet_headless.py` with `--print-atlas` outputs:
1. **River Discovery Broadcast**: Ready to paste into a River room monitored by the Atlas crawler.
2. **Curator CLI Command (`atlasctl add`)**: Pre-formatted with verified `--kind "site"`, `--landing general`, `--adult-sections false`, and `--volatility static` flags.

---

## Running Tests

```bash
make test
# or directly:
python3 -m unittest discover -s tests -v
```

---

## License

Released under the [MIT License](./LICENSE). Created and maintained by **Robert Jor Ruiz** ([@robdoit](https://github.com/robdoit)).
