# Homebrew Apps

A personal Homebrew tap maintained by [lostf1sh](https://github.com/lostf1sh).
Packages download the original upstream release files. This tap is not an official distribution channel of either project.

## Install

With a current version of Homebrew:

```sh
brew install --cask lostf1sh/apps/sakuracord
brew install --cask lostf1sh/apps/compositor
```

Or add the tap first:

```sh
brew tap lostf1sh/apps
```

| Cask | Upstream | Requirements |
| --- | --- | --- |
| `sakuracord` | [SakuraCordApp/SakuraCord](https://github.com/SakuraCordApp/SakuraCord) | Apple Silicon, macOS 27 or later |
| `compositor` | [robbietilton/Compositor](https://github.com/robbietilton/Compositor) | Apple Silicon or Intel, macOS 26.5 or later |

Compositor's cask declares macOS 26 because Homebrew's macOS dependency declarations cover major releases. The application itself requires 26.5 or later.

SakuraCord's current release is ad-hoc signed and not notarized. After installation, this cask runs `/usr/bin/xattr -cr` on the installed `SakuraCord.app` bundle, including its contents. This clears all extended attributes, including quarantine, for that app only and respects a custom Homebrew `--appdir`. It does not sign or notarize the app. The structured post-install step requires Homebrew 7 or later.

## Update

Both applications include their own updater. To include them when upgrading through Homebrew:

```sh
brew update
brew upgrade --cask --greedy lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```

## Automatic cask updates

The [Update casks workflow](https://github.com/lostf1sh/homebrew-apps/actions/workflows/update.yml) checks GitHub's latest stable releases every 30 minutes, at :17 and :47 each hour. It can also be run manually from Actions. The `verify` option runs all package checks even when no update is available.

For a newer release it selects the single matching upstream DMG, downloads it, calculates SHA-256, checks GitHub's asset digest when present, and updates `version`, `sha256`, and `url`. It runs Homebrew style checks and online package audits before committing directly to `main`. If any step fails, nothing is published. Concurrent changes to `main` reject the push; the next run starts fresh. No personal access token is required.

Drafts, prereleases, and downgrades are excluded. Existing-version assets are not silently rehashed. Ambiguous asset layouts and incompatible package changes fail validation and need maintainer attention. An unchanged release does not download packages or create a commit. This updates the tap; installed applications still update through their own updater or `brew upgrade`.

[GitHub schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) can be delayed. Public-repository schedules may be disabled after 60 days without repository activity; if that happens, re-enable this workflow in Actions.

## Maintain

Check for new stable releases:

```sh
brew livecheck --cask lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```

Livecheck reports releases; the scheduled workflow above publishes updates. For a manual correction, update the cask's `version`, `sha256`, and URL pattern if necessary. Download the exact upstream asset and calculate its checksum with `shasum -a 256 <file.dmg>`. Do not use a mutable `latest` URL or `sha256 :no_check`.

Validate changes before committing:

```sh
brew style --cask lostf1sh/apps/sakuracord lostf1sh/apps/compositor
brew audit --cask --online lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```

GitHub Actions runs style and online audits on pushes and pull requests. It does not install or launch either application. On Homebrew versions with tap trust enforcement, noninteractive validation may first require explicit trust for these two definitions:

```sh
brew trust --cask lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```
