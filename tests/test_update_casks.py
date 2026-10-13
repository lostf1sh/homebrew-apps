import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import update_casks as updater


REPO = "example/Example"
OLD_HASH = "a" * 64
NEW_HASH = "b" * 64


def cask(version="1.2.3", checksum=OLD_HASH, filename="Example.dmg"):
    return (
        'cask "example" do\n'
        f'  version "{version}"\n'
        f'  sha256 "{checksum}"\n\n'
        f'  url "https://github.com/{REPO}/releases/download/v#{{version}}/{filename}"\n'
        '  app "Example.app"\n'
        'end\n'
    )


def release(version="1.2.3", checksum=NEW_HASH, filename="Example.dmg"):
    return {
        "tag_name": f"v{version}",
        "assets": [{
            "name": filename,
            "digest": f"sha256:{checksum}" if checksum else None,
            "browser_download_url": f"https://github.com/{REPO}/releases/download/v{version}/{filename}",
        }],
    }


class PrepareUpdateTests(unittest.TestCase):
    def test_replaced_asset_at_same_version_is_verified_and_updated(self):
        downloader = Mock(return_value=NEW_HASH)
        after = updater.prepare_update(cask(), release(), REPO, "Example", downloader)
        self.assertEqual(after, cask(checksum=NEW_HASH))
        downloader.assert_called_once_with(
            f"https://github.com/{REPO}/releases/download/v1.2.3/Example.dmg",
            f"sha256:{NEW_HASH}",
        )
        downloader.reset_mock()
        self.assertEqual(updater.prepare_update(after, release(), REPO, "Example", downloader), after)
        downloader.assert_not_called()

    def test_matching_digest_skips_download(self):
        downloader = Mock()
        self.assertEqual(
            updater.prepare_update(cask(), release(checksum=OLD_HASH), REPO, "Example", downloader),
            cask(),
        )
        downloader.assert_not_called()

    def test_renamed_asset_at_same_version_updates_url(self):
        downloader = Mock(return_value=OLD_HASH)
        self.assertEqual(
            updater.prepare_update(cask(), release(checksum=OLD_HASH, filename="Example-new.dmg"),
                                   REPO, "Example", downloader),
            cask(filename="Example-new.dmg"),
        )
        downloader.assert_called_once()

    def test_missing_digest_downloads_to_check_same_version(self):
        for checksum in (OLD_HASH, NEW_HASH):
            with self.subTest(checksum=checksum):
                downloader = Mock(return_value=checksum)
                self.assertEqual(
                    updater.prepare_update(cask(), release(checksum=None), REPO, "Example", downloader),
                    cask(checksum=checksum),
                )
                downloader.assert_called_once()

    def test_new_version_is_verified_and_updated(self):
        downloader = Mock(return_value=NEW_HASH)
        self.assertEqual(
            updater.prepare_update(cask(), release(version="1.2.4"), REPO, "Example", downloader),
            cask(version="1.2.4", checksum=NEW_HASH),
        )
        downloader.assert_called_once()

    def test_downgrade_is_skipped(self):
        downloader = Mock()
        self.assertEqual(
            updater.prepare_update(cask(), release(version="1.2.2"), REPO, "Example", downloader),
            cask(),
        )
        downloader.assert_not_called()

    def test_draft_and_prerelease_are_rejected(self):
        for flag in ("draft", "prerelease"):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                updater.prepare_update(cask(), {**release(), flag: True}, REPO, "Example", Mock())

    def test_ambiguous_assets_and_unexpected_url_are_rejected(self):
        ambiguous = release()
        ambiguous["assets"].append(release(filename="Example-other.dmg")["assets"][0])
        unexpected_url = release()
        unexpected_url["assets"][0]["browser_download_url"] = "https://example.com/Example.dmg"
        for metadata in (ambiguous, unexpected_url):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                updater.prepare_update(cask(), metadata, REPO, "Example", Mock())

    def test_invalid_digest_is_rejected_before_downloading(self):
        downloader = Mock()
        metadata = release()
        metadata["assets"][0]["digest"] = "sha256:invalid"
        with self.assertRaisesRegex(ValueError, "Invalid GitHub asset"):
            updater.prepare_update(cask(), metadata, REPO, "Example", downloader)
        downloader.assert_not_called()

    def test_download_must_match_github_digest(self):
        response = Mock()
        response.read.side_effect = [b"replacement DMG", b""]
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        with patch.object(updater.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "does not match"):
                updater.asset_sha256("https://example.com/Example.dmg", f"sha256:{OLD_HASH}")
        self.assertNotEqual(hashlib.sha256(b"replacement DMG").hexdigest(), OLD_HASH)

    def test_upstream_failure_leaves_both_casks_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            cask_dir = Path(directory)
            for token in updater.PROJECTS:
                (cask_dir / f"{token}.rb").write_text(cask())
            with patch.object(updater, "latest_release", side_effect=[release(), ValueError("upstream failed")]), \
                    patch.object(updater, "prepare_update", return_value=cask(checksum=NEW_HASH)):
                with self.assertRaisesRegex(ValueError, "upstream failed"):
                    updater.update_all(cask_dir)
            for token in updater.PROJECTS:
                self.assertEqual((cask_dir / f"{token}.rb").read_text(), cask())


if __name__ == "__main__":
    unittest.main()
