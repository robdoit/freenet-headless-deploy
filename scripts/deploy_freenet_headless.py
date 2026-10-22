#!/usr/bin/env python3
"""
Freenet Headless Deploy — Automated CLI & AI Agent Deployment Script
Transforms root-relative asset paths for Freenet subpaths, manages website
signing keys, deploys static web directories via `fdev`, and generates
Freenet Atlas indexing metadata.

License: MIT
Author: Robert Jor Ruiz (@robdoit)
Repository: https://github.com/robdoit/freenet-headless-deploy

Usage:
    python3 deploy_freenet_headless.py --dir ./public --key my-site-key
    python3 deploy_freenet_headless.py --dir ./public --key my-site-key --dry-run --print-atlas
"""

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Dict, Optional, Tuple

STATIC_EXTENSIONS = (
    "css|js|mjs|wasm|map|json|xml|txt|md|py|pdf|"
    "png|jpg|jpeg|gif|svg|webp|ico|avif|"
    "woff|woff2|ttf|otf|eot|"
    "zip|tar|gz|tgz|xz|"
    "html|htm|mp4|webm|mp3|wav"
)

PATH_REPLACEMENTS = [
    # Root-relative assets & downloadable files (exclude protocol-relative // and /v1/contract/web/)
    (
        rf'href="/(?!/|v1/contract/web/)([^"#?]+\.({STATIC_EXTENSIONS}))([#?][^"]*)?"',
        r'href="./\1\3"',
    ),
    (
        rf'src="/(?!/|v1/contract/web/)([^"#?]+\.({STATIC_EXTENSIONS}))([#?][^"]*)?"',
        r'src="./\1\3"',
    ),
    # CSS url(/path) references (single-quoted, double-quoted, or unquoted)
    (
        rf'url\(\s*([\'"]?)/(?!/|v1/contract/web/)([^)\'"]+\.({STATIC_EXTENSIONS}))([#?][^)\'"]*)?\1\s*\)',
        r"url(\1./\2\4\1)",
    ),
    # Root-relative extensionless top-level page routes (e.g. /terms -> ./terms.html, /skills#top -> ./skills.html#top)
    (
        r'href="/(?!/|v1/contract/web/)([a-zA-Z0-9_-]+)([#?][^"]*)?"',
        r'href="./\1.html\2"',
    ),
    # Root index link
    (r'href="/"', r'href="./index.html"'),
]


def transform_content(content: str) -> str:
    """Apply Freenet subpath-safe relative path replacements to file content."""
    modified = content
    for pattern, replacement in PATH_REPLACEMENTS:
        modified = re.sub(pattern, replacement, modified)
    return modified


def transform_asset_paths(source_dir: str, staging_dir: str) -> Tuple[str, int]:
    """Copy source_dir to staging_dir and rewrite root-relative paths across web files."""
    print(f"🧹 Staging assets from '{source_dir}' to '{staging_dir}'...")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    shutil.copytree(source_dir, staging_dir)

    transformed_count = 0
    for root, _, files in os.walk(staging_dir):
        for file in files:
            if file.endswith((".html", ".htm", ".css", ".js", ".mjs")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                modified = transform_content(content)
                if modified != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(modified)
                    transformed_count += 1

    print(f"✨ Transformed root-relative asset paths across {transformed_count} file(s).")
    return staging_dir, transformed_count


def get_env() -> Dict[str, str]:
    """Ensure ~/.cargo/bin is present on PATH for fdev and freenet binaries."""
    env = os.environ.copy()
    cargo_bin = os.path.expanduser("~/.cargo/bin")
    if cargo_bin not in env.get("PATH", ""):
        env["PATH"] = f"{cargo_bin}:{env.get('PATH', '')}"
    return env


def parse_fdev_key_list(output: str) -> Dict[str, str]:
    """Parse `fdev website list` output into a mapping of {key_name: contract_id}."""
    keys: Dict[str, str] = {}
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) >= 2:
            key_name, contract_id = parts[0], parts[1]
            if len(contract_id) in (43, 44):
                keys[key_name] = contract_id
    return keys


def list_fdev_keys(fdev_bin: str, env: Dict[str, str]) -> Dict[str, str]:
    """Return existing website keys mapped to their Freenet contract IDs."""
    res = subprocess.run(
        [fdev_bin, "website", "list"],
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return {}
    return parse_fdev_key_list(res.stdout)


def check_local_node(gateway_url: str = "http://127.0.0.1:7509/") -> bool:
    """Verify the local Freenet HTTP gateway is responding."""
    req = urllib.request.Request(gateway_url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status < 500
    except urllib.error.HTTPError as e:
        # Even a 400/404 from the gateway means the daemon is listening
        return e.code < 500
    except Exception:
        return False


def extract_html_metadata(html_path: str) -> Tuple[str, str]:
    """Extract <title> and <meta name="description"> from an HTML file."""
    title = "Freenet Web Application"
    snippet = "Decentralized web application published with Freenet Headless Deploy."
    if not os.path.exists(html_path):
        return title, snippet

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    if title_match:
        raw_title = re.sub(r"\s+", " ", title_match.group(1)).strip()
        if raw_title:
            title = html.unescape(raw_title)[:200]

    desc_match = re.search(
        r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
        content,
        re.IGNORECASE,
    )
    if not desc_match:
        desc_match = re.search(
            r'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']',
            content,
            re.IGNORECASE,
        )
    if desc_match:
        raw_desc = re.sub(r"\s+", " ", desc_match.group(1)).strip()
        if raw_desc:
            snippet = html.unescape(raw_desc)[:500]

    return title, snippet


def format_atlas_submission(
    contract_id: str,
    path: str = "/",
    title: str = "Freenet Headless Deploy",
    snippet: str = "Open-source CLI tool and AI agent skill for packaging, building, and hosting static web applications on Freenet with 24/7 headless service availability.",
    tags: str = "freenet,headless,deploy,agent-skill,open-source",
) -> str:
    """Format verified Freenet Atlas CLI and River discovery payloads."""
    normalized_path = path if path.startswith("/") else f"/{path}"
    locator = f"freenet:{contract_id}{normalized_path}"
    safe_title = title.replace('"', '\\"')
    safe_snippet = snippet.replace('"', '\\"')
    return (
        "\n🧭 Freenet Atlas Discovery & Indexing Payloads\n"
        "================================================\n"
        f"• Atlas Directory URL : http://127.0.0.1:7509/v1/contract/web/771DvtPMwt2PumPyrFvsz7fpvU1gogcmb5qtS1yYEEH9/\n"
        f"• Resource Locator    : {locator}\n\n"
        "1. River Discovery Room Broadcast:\n"
        f"   {locator} — {title}: {snippet}\n\n"
        "2. Curator CLI Command (atlasctl):\n"
        "   atlasctl add \\\n"
        '     --kind "site" \\\n'
        f'     --title "{safe_title}" \\\n'
        f'     --snippet "{safe_snippet}" \\\n'
        f'     --tags "{tags}" \\\n'
        f'     --locator "{locator}" \\\n'
        "     --landing general \\\n"
        "     --adult-sections false \\\n"
        "     --volatility static\n"
    )


def deploy_to_freenet(staging_dir: str, key_name: str, timeout: int = 300) -> Optional[str]:
    """Initialize keypair if needed, deploy via `fdev`, and return the Contract ID."""
    env = get_env()
    fdev_bin = shutil.which("fdev", path=env["PATH"])
    if not fdev_bin:
        print("❌ Error: 'fdev' CLI tool not found. Please run 'cargo install fdev' first.")
        sys.exit(1)

    existing_keys = list_fdev_keys(fdev_bin, env)
    is_new_key = key_name not in existing_keys

    if is_new_key:
        print(f"🔑 Initializing new website signing keypair '{key_name}'...")
        init_res = subprocess.run(
            [fdev_bin, "website", "init", key_name],
            env=env,
            capture_output=True,
            text=True,
        )
        if init_res.returncode != 0:
            print(f"❌ Failed to initialize keypair '{key_name}':\n{init_res.stderr}")
            sys.exit(init_res.returncode)
        existing_keys = list_fdev_keys(fdev_bin, env)

    contract_id = existing_keys.get(key_name)
    timeout_args = ["--timeout", str(timeout)]

    if is_new_key:
        print(f"🚀 Publishing new website to Freenet (key: {key_name})...")
        cmd = [fdev_bin, "website", "publish", "--key", key_name, staging_dir] + timeout_args
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    else:
        print(f"🚀 Updating existing website on Freenet (key: {key_name})...")
        cmd = [fdev_bin, "website", "update", "--key", key_name, staging_dir] + timeout_args
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            print("ℹ️  Update did not find an existing live state; falling back to initial publish...")
            pub_cmd = [fdev_bin, "website", "publish", "--key", key_name, staging_dir] + timeout_args
            res = subprocess.run(pub_cmd, env=env, capture_output=True, text=True)

    if res.stdout:
        print(res.stdout.strip())

    if res.returncode == 0:
        if not contract_id:
            contract_id = list_fdev_keys(fdev_bin, env).get(key_name)
        print("\n🎉 Freenet Headless Deployment Complete!")
        if contract_id:
            print(f"🔗 Contract ID       : {contract_id}")
            print(f"🌐 Local Gateway URL : http://127.0.0.1:7509/v1/contract/web/{contract_id}/")
            print(f"📍 Freenet Locator   : freenet:{contract_id}/")
        return contract_id
    else:
        print(f"❌ Deployment error:\n{res.stderr}")
        sys.exit(res.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freenet Headless Deploy — One-Command P2P Web Deployment CLI"
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Path to static website directory (must contain index.html)",
    )
    parser.add_argument(
        "--key",
        required=True,
        help="Name of website signing keypair (e.g. my-site-key)",
    )
    parser.add_argument(
        "--staging",
        default="./freenet_staging",
        help="Path to staging output directory (default: ./freenet_staging)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximum seconds to wait for Freenet node response (default: 300)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Transform assets into staging directory without publishing to Freenet",
    )
    parser.add_argument(
        "--check-node",
        action="store_true",
        help="Verify local Freenet HTTP gateway (127.0.0.1:7509) before deploying",
    )
    parser.add_argument(
        "--print-atlas",
        action="store_true",
        help="Output ready-to-run Freenet Atlas registration & River broadcast commands",
    )
    parser.add_argument(
        "--atlas-path",
        default="/",
        help="Subpath within the contract to index in Freenet Atlas (default: /)",
    )
    args = parser.parse_args()

    abs_source = os.path.abspath(args.dir)
    abs_staging = os.path.abspath(args.staging)

    index_html = os.path.join(abs_source, "index.html")
    if not os.path.exists(index_html):
        print(f"❌ Error: Target directory '{abs_source}' does not contain an index.html file.")
        sys.exit(1)

    if args.check_node:
        if check_local_node():
            print("✅ Local Freenet gateway (http://127.0.0.1:7509) is online.")
        else:
            print(
                "⚠️  Warning: Local Freenet gateway (http://127.0.0.1:7509) is not responding.\n"
                "   Start the headless service via: freenet service install && freenet service start"
            )
            if not args.dry_run:
                sys.exit(1)

    staging_dir, _ = transform_asset_paths(abs_source, abs_staging)

    contract_id: Optional[str] = None
    if args.dry_run:
        print(f"✅ Dry-run complete. Staged files are ready at: {staging_dir}")
        env = get_env()
        fdev_bin = shutil.which("fdev", path=env["PATH"])
        if fdev_bin:
            contract_id = list_fdev_keys(fdev_bin, env).get(args.key)
    else:
        contract_id = deploy_to_freenet(staging_dir, args.key, timeout=args.timeout)

    if args.print_atlas:
        target_html = (
            os.path.join(staging_dir, args.atlas_path.lstrip("/"))
            if args.atlas_path not in ("", "/")
            else os.path.join(staging_dir, "index.html")
        )
        title, snippet = extract_html_metadata(target_html)
        cid_display = contract_id or "<YOUR_CONTRACT_ID>"
        print(format_atlas_submission(cid_display, path=args.atlas_path, title=title, snippet=snippet))


if __name__ == "__main__":
    main()
