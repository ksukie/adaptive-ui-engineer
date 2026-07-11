from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / ".github" / "scripts" / "run_skills_ref.py"
SPEC = importlib.util.spec_from_file_location("run_skills_ref", RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the pinned validator runner.")
BOOTSTRAP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOTSTRAP)


def archive_with(members: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return stream.getvalue()


class FakeResponse(io.BytesIO):
    def __init__(self, payload: bytes, url: str) -> None:
        super().__init__(payload)
        self._url = url
        self.headers = {"Content-Length": str(len(payload))}

    def geturl(self) -> str:
        return self._url

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *arguments: object) -> None:
        self.close()


class ValidatorBootstrapTests(unittest.TestCase):
    def test_source_pin_uses_full_commit_and_sha256(self) -> None:
        self.assertRegex(BOOTSTRAP.COMMIT, r"^[0-9a-f]{40}$")
        self.assertRegex(BOOTSTRAP.ARCHIVE_SHA256, r"^[0-9a-f]{64}$")
        self.assertEqual(
            BOOTSTRAP.ARCHIVE_URL,
            "https://codeload.github.com/agentskills/agentskills/zip/" + BOOTSTRAP.COMMIT,
        )

    def test_extractor_accepts_only_the_expected_flat_package(self) -> None:
        members = {
            BOOTSTRAP.SOURCE_PREFIX + name: ("# " + name + "\n").encode("utf-8")
            for name in BOOTSTRAP.EXPECTED_FILES
        }
        with tempfile.TemporaryDirectory() as directory:
            source_root = BOOTSTRAP.extract_validator(
                archive_with(members), Path(directory)
            )
            extracted = {
                path.name for path in (source_root / "skills_ref").iterdir() if path.is_file()
            }
        self.assertEqual(extracted, BOOTSTRAP.EXPECTED_FILES)

    def test_extractor_rejects_unexpected_nested_source(self) -> None:
        payload = archive_with(
            {BOOTSTRAP.SOURCE_PREFIX + "nested/payload.py": b"print('unexpected')"}
        )
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                BOOTSTRAP.ValidationBootstrapError, "unexpected source path"
            ):
                BOOTSTRAP.extract_validator(payload, Path(directory))

    def test_downloader_fails_closed_on_hash_mismatch(self) -> None:
        response = FakeResponse(b"tampered", BOOTSTRAP.ARCHIVE_URL)
        with mock.patch.object(BOOTSTRAP.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(
                BOOTSTRAP.ValidationBootstrapError, "archive hash mismatch"
            ):
                BOOTSTRAP.download_archive()

    def test_downloader_rejects_redirect_to_unapproved_host(self) -> None:
        response = FakeResponse(b"payload", "https://example.invalid/archive.zip")
        with mock.patch.object(BOOTSTRAP.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(
                BOOTSTRAP.ValidationBootstrapError, "approved HTTPS host"
            ):
                BOOTSTRAP.download_archive()


if __name__ == "__main__":
    unittest.main()
