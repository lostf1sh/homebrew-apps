#!/usr/bin/env python3
"""Update pinned casks from newer stable upstream GitHub releases."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {
    "sakuracord": ("SakuraCordApp/SakuraCord", "SakuraCord"),
    "compositor": ("robbietilton/Compositor", "Compositor"),
}


def version_key(value):
    if not re.fullmatch(r"\d+(?:\.\d+){1,3}", value):
        raise ValueError(f"Unsupported stable version: {value!r}")
    parts = tuple(map(int, value.split(".")))
    return parts + (0,) * (4 - len(parts))


def latest_release(repo):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "homebrew-apps-updater"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/latest", headers=headers
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def asset_sha256(url, expected):
    # No API token is sent to the asset URL or its redirects.
    request = urllib.request.Request(url, headers={"User-Agent": "homebrew-apps-updater"})
    digest = hashlib.sha256()
    with urllib.request.urlopen(request, timeout=120) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
    actual = digest.hexdigest()
    if expected and expected != f"sha256:{actual}":
        raise ValueError("Downloaded asset does not match GitHub's SHA-256 digest")
    return actual


def replace_stanza(text, name, value):
    result, count = re.subn(
        rf'^  {name} "[^"\n]+"$', lambda _: f'  {name} "{value}"', text, flags=re.MULTILINE
    )
    if count != 1:
        raise ValueError(f"Expected exactly one {name} stanza; found {count}")
    return result


def prepare_update(text, release, repo, app_name, downloader=asset_sha256):
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Refusing a draft or prerelease")
    tag = release["tag_name"]
    version = tag.removeprefix("v")
    new_key = version_key(version)
    current = re.search(r'^  version "([^"\n]+)"$', text, re.MULTILINE)
    if not current:
        raise ValueError("Missing pinned cask version")
    # Do not downgrade or silently replace the hash of an existing version.
    if new_key <= version_key(current[1]):
        return text

    assets = [a for a in release["assets"]
              if a["name"].lower().startswith(app_name.lower())
              and a["name"].lower().endswith(".dmg")]
    if len(assets) != 1:
        raise ValueError(f"Expected one {app_name} DMG; found {len(assets)}")
    asset = assets[0]
    if not re.fullmatch(r"[A-Za-z0-9._-]+\.dmg", asset["name"]):
        raise ValueError("Unsupported asset filename")
    url = f'https://github.com/{repo}/releases/download/{tag}/{asset["name"]}'
    if asset["browser_download_url"] != url:
        raise ValueError("Unexpected asset download URL")
    checksum = downloader(url, asset.get("digest"))
    if not re.fullmatch(r"[a-f0-9]{64}", checksum):
        raise ValueError("Invalid SHA-256")
    # All interpolated metadata above is allowlisted before entering Ruby source.
    template = url.replace(version, "#{version}")
    for name, value in (("version", version), ("sha256", checksum), ("url", template)):
        text = replace_stanza(text, name, value)
    return text


def update_all(cask_dir):
    pending = []
    for token, (repo, app_name) in PROJECTS.items():
        path = cask_dir / f"{token}.rb"
        before = path.read_text()
        after = prepare_update(before, latest_release(repo), repo, app_name)
        if before != after:
            pending.append((path, after))
        print(f'{token}: {"update available" if before != after else "up to date"}')
    # Prepare both first: an upstream error must not leave a partial update.
    for path, content in pending:
        path.write_text(content)
    return bool(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cask-dir", type=Path, default=ROOT / "Casks")
    args = parser.parse_args()
    changed = update_all(args.cask_dir)
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as file:
            file.write(f'changed={str(changed).lower()}\n')


if __name__ == "__main__":
    main()
