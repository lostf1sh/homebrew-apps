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

SakuraCord's current release is ad-hoc signed and not notarized. macOS may require approval in System Settings → Privacy & Security on first launch, as described in the [upstream README](https://github.com/SakuraCordApp/SakuraCord#download).

## Update

Both applications include their own updater. To include them when upgrading through Homebrew:

```sh
brew update
brew upgrade --cask --greedy lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```

## Maintain

Check for new stable releases:

```sh
brew livecheck --cask lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```

Livecheck reports releases; it does not modify or publish the cask files. When a release changes, update the cask's `version`, `sha256`, and URL pattern if necessary. Download the exact upstream asset and calculate its checksum with `shasum -a 256 <file.dmg>`. Do not use a mutable `latest` URL or `sha256 :no_check`.

Validate changes before committing:

```sh
brew style --cask lostf1sh/apps/sakuracord lostf1sh/apps/compositor
brew audit --cask --online lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```

GitHub Actions runs style and online audits on pushes and pull requests. It does not install or launch either application. On Homebrew versions with tap trust enforcement, noninteractive validation may first require explicit trust for these two definitions:

```sh
brew trust --cask lostf1sh/apps/sakuracord lostf1sh/apps/compositor
```
