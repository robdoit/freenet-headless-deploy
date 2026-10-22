---
name: freenet-headless-deploy
description: Automates the complete pipeline for packaging, transforming, building, and deploying any static website or web application onto the decentralized Freenet network with 24/7 headless service availability and Freenet Atlas indexing.
license: MIT
author: Robert Jor Ruiz (@robdoit)
repository: https://github.com/robdoit/freenet-headless-deploy
---

# Freenet Headless Deploy Skill

This skill enables AI coding agents (Claude Code, Cursor, GitHub Copilot, Cline, Windsurf, Aider) and developers to automatically transform, package, compile, and deploy any static website or web application onto the decentralized **Freenet** peer-to-peer network with 24/7 headless background service availability.

---

## When to Use This Skill

Activate this skill when:
- The user wants to host, deploy, or publish a website or web app to the decentralized Freenet network.
- The user wants a **headless Freenet** deployment that stays online 24/7 via the background system service without needing an open browser session.
- You need to resolve broken asset paths (CSS, JS, images, fonts, archives, markdown, extensionless links) caused by Freenet contract subpath URLs (`/v1/contract/web/<CONTRACT_ID>/`).
- The user wants their Freenet site indexed and discoverable on **Freenet Atlas** (`freenet:771DvtPMwt2PumPyrFvsz7fpvU1gogcmb5qtS1yYEEH9/`).

---

## Step-by-Step Agent Workflow

### Step 1: Verify & Install Prerequisites
Ensure Rust, the `wasm32-unknown-unknown` target, the `freenet` core node binary, and the `fdev` developer CLI are installed:

```bash
# 1. Install Rust toolchain (if missing)
command -v rustc >/dev/null 2>&1 || curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# 2. Add WebAssembly compilation target
rustup target add wasm32-unknown-unknown

# 3. Install freenet node and fdev developer CLI (if missing)
command -v freenet >/dev/null 2>&1 || cargo install freenet
command -v fdev >/dev/null 2>&1 || cargo install fdev
```

---

### Step 2: Ensure the Headless Freenet Service is Running
Freenet includes a native background system service manager (`freenet service`) for continuous 24/7 headless operation:

```bash
# Install and start the native background service
freenet service install
freenet service start

# Verify service health (or recover wedged/orphaned processes via doctor)
freenet service status || freenet service doctor
```

Verify the local HTTP gateway is reachable on port `7509`:
```bash
curl -sI http://127.0.0.1:7509/
```

---

### Step 3: Transform Asset Paths & Deploy via `deploy_freenet_headless.py`
Freenet web contracts are served under subpath URLs (`/v1/contract/web/<CONTRACT_ID>/`). Root-relative paths (`/style.css`, `/app.js`, `/skills`) will fail to resolve against the node origin unless rewritten to relative paths (`./style.css`, `./app.js`, `./skills.html`).

Run the one-command deployment script:
```bash
python3 scripts/deploy_freenet_headless.py --dir ./public --key my-site-key --check-node --print-atlas
```

#### Useful CLI Flags:
- `--dir <PATH>`: Path to source static directory (must contain `index.html`).
- `--key <NAME>`: Name of the website signing keypair (e.g., `my-site-key`).
- `--staging <PATH>`: Output directory for transformed assets (default: `./freenet_staging`).
- `--timeout <SECONDS>`: Maximum seconds to wait for the node's response (default: `300`).
- `--dry-run`: Transform assets and validate without publishing to the network.
- `--check-node`: Probe `http://127.0.0.1:7509` before invoking `fdev`.
- `--print-atlas`: Output ready-to-run **Freenet Atlas** `atlasctl add` and River broadcast payloads.

---

### Step 4: Manual `fdev` Lifecycle Commands (Reference)

If executing `fdev` directly against a pre-staged directory:

```bash
# List existing website signing keys and their 43-44 char Base58 Contract IDs
fdev website list

# Initialize a new website signing keypair
fdev website init <SITE_KEY_NAME>

# First-time publish to Freenet
fdev website publish --key <SITE_KEY_NAME> <STAGING_DIR> --timeout 300

# Update an already-published website (increments version)
fdev website update --key <SITE_KEY_NAME> <STAGING_DIR> --timeout 300
```

---

### Step 5: Index on Freenet Atlas
To make the deployed contract discoverable on **Freenet Atlas** (`http://127.0.0.1:7509/v1/contract/web/771DvtPMwt2PumPyrFvsz7fpvU1gogcmb5qtS1yYEEH9/`):

1. **Page Metadata**: Ensure your HTML includes a clear `<title>`, `<meta name="description">`, and an explicit license & authorship statement in the visible text (the Atlas crawler's LLM evaluator checks for visible open-source licensing and creator attribution).
2. **River Discovery Broadcast**: Post the canonical `freenet:<CONTRACT_ID>/` locator in a River room monitored by the Atlas crawler.
3. **Curator CLI (`atlasctl`)**:
   ```bash
   atlasctl add \
     --kind "site" \
     --title "<SITE_TITLE>" \
     --snippet "<ONE_SENTENCE_FACTUAL_DESCRIPTION>" \
     --tags "freenet,headless,deploy,open-source" \
     --locator "freenet:<CONTRACT_ID>/" \
     --landing general \
     --adult-sections false \
     --volatility static
   ```

---

## Output Metrics & Artifacts

After deployment, always report the following to the user:
- **Contract ID**: The 43–44 character Base58 contract address (from `fdev website list`).
- **Local Gateway URL**: `http://127.0.0.1:7509/v1/contract/web/<CONTRACT_ID>/`
- **Freenet Locator**: `freenet:<CONTRACT_ID>/`
- **Keypair Storage Location**:
  - macOS: `$HOME/Library/Application Support/freenet/website-keys/<KEY_NAME>.toml`
  - Linux: `${XDG_DATA_HOME:-$HOME/.local/share}/freenet/website-keys/<KEY_NAME>.toml`
- **Headless Service Status**: Output of `freenet service status`.
