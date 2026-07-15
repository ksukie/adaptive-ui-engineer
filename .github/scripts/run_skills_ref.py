#!/usr/bin/env python3
"""Run a commit- and hash-pinned Agent Skills reference validator."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import io
import stat
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Optional, Sequence
from urllib.parse import urlsplit


COMMIT = "38a2ff82958afee88dadf4831509e6f7e9d8ef4e"
ARCHIVE_URL = "https://codeload.github.com/agentskills/agentskills/zip/{0}".format(COMMIT)
ARCHIVE_SHA256 = "e1ad0039bb3b059c1fc2528195214d511d869cf5c84b65c5510f913e52f80648"
ARCHIVE_LIMIT = 5 * 1024 * 1024
SOURCE_LIMIT = 2 * 1024 * 1024
SOURCE_PREFIX = "agentskills-{0}/skills-ref/src/skills_ref/".format(COMMIT)
EXPECTED_FILES = {
    "__init__.py",
    "cli.py",
    "errors.py",
    "models.py",
    "parser.py",
    "prompt.py",
    "validator.py",
}


class ValidationBootstrapError(Exception):
    """Raised when the pinned validator cannot be authenticated or loaded."""


def download_archive() -> bytes:
    request = urllib.request.Request(
        ARCHIVE_URL,
        headers={"User-Agent": "adaptive-ui-engineer-ci/1.0.3"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_url.hostname != "codeload.github.com":
                raise ValidationBootstrapError("Validator download left the approved HTTPS host.")
            declared_length = response.headers.get("Content-Length")
            if declared_length is not None and int(declared_length) > ARCHIVE_LIMIT:
                raise ValidationBootstrapError("Validator archive exceeds the size limit.")
            payload = response.read(ARCHIVE_LIMIT + 1)
    except (OSError, ValueError) as exc:
        raise ValidationBootstrapError("Validator download failed: {0}".format(exc)) from exc
    if len(payload) > ARCHIVE_LIMIT:
        raise ValidationBootstrapError("Validator archive exceeds the size limit.")
    actual_hash = hashlib.sha256(payload).hexdigest()
    if not hmac.compare_digest(actual_hash, ARCHIVE_SHA256):
        raise ValidationBootstrapError(
            "Validator archive hash mismatch: expected {0}, received {1}.".format(
                ARCHIVE_SHA256, actual_hash
            )
        )
    return payload


def extract_validator(payload: bytes, destination: Path) -> Path:
    source_root = destination / "skills_ref_source"
    package_root = source_root / "skills_ref"
    extracted = set()
    total_size = 0
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValidationBootstrapError("Validator archive is not a valid ZIP file.") from exc

    with archive:
        for member in archive.infolist():
            if not member.filename.startswith(SOURCE_PREFIX) or member.is_dir():
                continue
            relative_text = member.filename[len(SOURCE_PREFIX) :]
            relative = PurePosixPath(relative_text)
            if len(relative.parts) != 1 or relative.name not in EXPECTED_FILES:
                raise ValidationBootstrapError("Validator archive contains an unexpected source path.")
            unix_mode = (member.external_attr >> 16) & 0o170000
            if unix_mode == stat.S_IFLNK or member.flag_bits & 0x1:
                raise ValidationBootstrapError("Validator source member is linked or encrypted.")
            total_size += member.file_size
            if member.file_size > SOURCE_LIMIT or total_size > SOURCE_LIMIT:
                raise ValidationBootstrapError("Validator source exceeds the extraction size limit.")
            package_root.mkdir(parents=True, exist_ok=True)
            target = package_root / relative.name
            target.write_bytes(archive.read(member))
            extracted.add(relative.name)

    if extracted != EXPECTED_FILES:
        missing = ", ".join(sorted(EXPECTED_FILES - extracted))
        raise ValidationBootstrapError("Validator archive is missing expected files: {0}".format(missing))
    return source_root


def run_validator(skill_path: Path) -> int:
    if not skill_path.exists():
        raise ValidationBootstrapError("Skill path does not exist: {0}".format(skill_path))
    payload = download_archive()
    with tempfile.TemporaryDirectory(prefix="adaptive-ui-skills-ref-") as directory:
        source_root = extract_validator(payload, Path(directory))
        sys.path.insert(0, str(source_root))
        try:
            from skills_ref.cli import main as skills_ref_main

            skills_ref_main.main(
                args=["validate", str(skill_path)],
                prog_name="skills-ref",
                standalone_mode=False,
            )
        except SystemExit as exc:
            return int(exc.code or 0)
        finally:
            sys.path.pop(0)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the hash-pinned Agent Skills reference validator."
    )
    parser.add_argument("skill_path", type=Path)
    arguments = parser.parse_args(argv)
    try:
        return run_validator(arguments.skill_path)
    except ValidationBootstrapError as exc:
        sys.stderr.write("skills-ref bootstrap: {0}\n".format(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
