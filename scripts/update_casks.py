#!/usr/bin/env python3
"""Update pinned casks from stable upstream releases and replaced assets."""

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
    current_key = version_key(current[1])
    # Do not downgrade, but check for replaced assets at the pinned version.
    if new_key < current_key:
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
    expected = asset.get("digest")
    if expected and not re.fullmatch(r"sha256:[a-f0-9]{64}", expected):
        raise ValueError("Invalid GitHub asset SHA-256 digest")
    template = url.replace(version, "#{version}")
    if new_key == current_key:
        checksum_stanza = re.search(r'^  sha256 "([a-f0-9]{64})"$', text, re.MULTILINE)
        url_stanza = re.search(r'^  url "([^"\n]+)"$', text, re.MULTILINE)
        if not checksum_stanza or not url_stanza:
            raise ValueError("Missing pinned cask checksum or URL")
        # GitHub's digest avoids downloading unchanged releases every 30 minutes.
        if expected == f"sha256:{checksum_stanza[1]}" and url_stanza[1] == template:
            return text
    # A changed digest (or unavailable digest) must be verified by downloading.
    checksum = downloader(url, expected)
    if not re.fullmatch(r"[a-f0-9]{64}", checksum):
        raise ValueError("Invalid SHA-256")
    # All interpolated metadata above is allowlisted before entering Ruby source.
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
            before_version = re.search(r'^  version "([^"\n]+)"$', before, re.MULTILINE)[1]
            after_version = re.search(r'^  version "([^"\n]+)"$', after, re.MULTILINE)[1]
            reason = "asset changed at pinned version" if before_version == after_version else "update available"
            print(f"{token}: {reason}")
        else:
            print(f"{token}: up to date")
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
