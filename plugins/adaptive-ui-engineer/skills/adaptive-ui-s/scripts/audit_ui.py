#!/usr/bin/env python3
"""Read-only static triage for responsive UI, accessibility, and complexity risks."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote, urlsplit


TOOL_NAME = "adaptive-ui-engineer"
TOOL_VERSION = "1.0.3"
SCHEMA_VERSION = 2
MAX_FILE_BYTES = 2 * 1024 * 1024

SUPPORTED_SUFFIXES: Set[str] = {
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".astro",
}

CSS_SUFFIXES = {".css", ".scss", ".sass", ".less"}
DOCUMENT_SUFFIXES = {".html", ".htm"}
MARKUP_SUFFIXES = DOCUMENT_SUFFIXES | {".vue", ".svelte", ".astro", ".jsx", ".tsx"}
SCRIPT_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro"}

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".next",
    ".nuxt",
    ".svelte-kit",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "vendor",
}

DEFAULT_EXCLUDE_PATTERNS = ("**/*.min.js", "**/*.min.css", "**/*.map")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_EVIDENCE_LEVELS = {"source_observed", "static_inferred", "runtime_observed"}
VALID_VALIDATION_STATES = {
    "not_applicable",
    "not_run",
    "reproduced",
    "not_reproduced",
    "manual_review_needed",
}
STATIC_EVIDENCE_LEVELS = {"source_observed", "static_inferred"}
STATIC_VALIDATION_STATES = {"not_applicable", "not_run", "manual_review_needed"}

# Each rule owns the evidence semantics emitted by this static auditor.
# Runtime-only values remain in the report schema for a future browser verifier,
# but this module cannot emit them.
RULE_METADATA: Dict[str, Dict[str, str]] = {
    "AUI001": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI002": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI003": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI004": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI005": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI006": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI007": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI008": {"evidence_level": "static_inferred", "default_validation_state": "manual_review_needed"},
    "AUI009": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI010": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI011": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI012": {"evidence_level": "source_observed", "default_validation_state": "manual_review_needed"},
    "AUI013": {"evidence_level": "source_observed", "default_validation_state": "manual_review_needed"},
    "AUI014": {"evidence_level": "static_inferred", "default_validation_state": "manual_review_needed"},
    "AUI015": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI016": {"evidence_level": "static_inferred", "default_validation_state": "manual_review_needed"},
    "AUI017": {"evidence_level": "static_inferred", "default_validation_state": "not_run"},
    "AUI018": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI019": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI020": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI021": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI022": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
    "AUI023": {"evidence_level": "source_observed", "default_validation_state": "not_applicable"},
}


class AuditError(Exception):
    """Raised for configuration, input, or output errors."""


@dataclass(frozen=True)
class IgnoreEntry:
    rule: str
    paths: Tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class AuditConfig:
    exclude: Tuple[str, ...] = ()
    ignore: Tuple[IgnoreEntry, ...] = ()
    fail_on: str = "none"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    priority: str
    confidence: str
    evidence_level: str
    validation_state: str
    category: str
    path: str
    line: int
    message: str
    evidence: str
    recommendation: str


def absolute_path(path: Path) -> Path:
    """Return a normalized absolute path without resolving links."""

    return Path(os.path.abspath(os.fspath(path)))


def stat_is_link_or_reparse(info: os.stat_result) -> bool:
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def is_link_or_reparse(path: Path) -> bool:
    return stat_is_link_or_reparse(os.lstat(os.fspath(path)))


def path_traverses_link_or_reparse(path: Path) -> bool:
    """Check existing path components without resolving their destinations."""

    candidate = absolute_path(path)
    cursor = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        cursor = cursor / part
        if not os.path.lexists(os.fspath(cursor)):
            break
        if is_link_or_reparse(cursor):
            return True
    return False


def sanitized_os_error(action: str, error: OSError) -> str:
    """Describe a filesystem failure without embedding an absolute path."""

    error_number = getattr(error, "errno", None)
    if error_number is None:
        return action
    return "{0} (errno {1})".format(action, error_number)


def safe_read_bytes(
    path: Path, limit: int = MAX_FILE_BYTES
) -> Tuple[Optional[bytes], Optional[str]]:
    """Read one regular file without following a final link or reparse point."""

    try:
        before = os.lstat(os.fspath(path))
    except OSError as exc:
        return None, sanitized_os_error("stat failed", exc)
    if stat_is_link_or_reparse(before):
        return None, "symbolic link or reparse point"
    if not stat.S_ISREG(before.st_mode):
        return None, "not a regular file"
    if before.st_size > limit:
        return None, "larger than 2 MiB"

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor: Optional[int] = None
    try:
        descriptor = os.open(os.fspath(path), flags)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            return None, "not a regular file"
        if (
            before.st_ino
            and opened.st_ino
            and (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            return None, "file changed during audit"
        if opened.st_size > limit:
            return None, "larger than 2 MiB"
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            descriptor = None
            payload = handle.read(limit + 1)
    except OSError as exc:
        return None, sanitized_os_error("read failed", exc)
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if len(payload) > limit:
        return None, "larger than 2 MiB"
    return payload, None


def normalized_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def path_matches(path: str, pattern: str) -> bool:
    clean_path = normalized_path(path)
    clean_pattern = pattern.replace("\\", "/").lstrip("./")
    if not clean_pattern:
        return False
    if fnmatch.fnmatchcase(clean_path, clean_pattern):
        return True
    if clean_pattern.startswith("**/") and fnmatch.fnmatchcase(clean_path, clean_pattern[3:]):
        return True
    if clean_pattern.endswith("/**"):
        prefix = clean_pattern[:-3].rstrip("/")
        return clean_path == prefix or clean_path.startswith(prefix + "/")
    return False


def load_config(path: Optional[Path]) -> AuditConfig:
    if path is None:
        return AuditConfig()
    raw, read_error = safe_read_bytes(path)
    if read_error is not None or raw is None:
        raise AuditError(
            "Cannot read configuration {0}: {1}".format(path, read_error or "read failed")
        )
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError("Cannot read configuration {0}: {1}".format(path, exc)) from exc
    if not isinstance(payload, dict):
        raise AuditError("Configuration root must be a JSON object.")

    unknown = sorted(set(payload) - {"exclude", "ignore", "fail_on"})
    if unknown:
        raise AuditError("Unknown configuration keys: {0}".format(", ".join(unknown)))

    exclude_raw = payload.get("exclude", [])
    if not isinstance(exclude_raw, list) or not all(
        isinstance(item, str) and item.strip() for item in exclude_raw
    ):
        raise AuditError("'exclude' must be an array of non-empty strings.")

    ignore_entries: List[IgnoreEntry] = []
    ignore_raw = payload.get("ignore", [])
    if not isinstance(ignore_raw, list):
        raise AuditError("'ignore' must be an array.")
    for index, item in enumerate(ignore_raw):
        if not isinstance(item, dict) or set(item) != {"rule", "paths", "reason"}:
            raise AuditError(
                "ignore[{0}] must contain exactly rule, paths, and reason.".format(index)
            )
        rule = item["rule"]
        paths = item["paths"]
        reason = item["reason"]
        if not isinstance(rule, str) or re.fullmatch(r"AUI\d{3}", rule) is None:
            raise AuditError("ignore[{0}].rule must match AUI000.".format(index))
        if not isinstance(paths, list) or not paths or not all(
            isinstance(candidate, str) and candidate.strip() for candidate in paths
        ):
            raise AuditError("ignore[{0}].paths must be a non-empty string array.".format(index))
        if not isinstance(reason, str) or len(reason.strip()) < 4:
            raise AuditError("ignore[{0}].reason must explain the suppression.".format(index))
        ignore_entries.append(
            IgnoreEntry(rule=rule, paths=tuple(paths), reason=reason.strip())
        )

    fail_on = payload.get("fail_on", "none")
    if fail_on not in set(PRIORITY_ORDER) | {"none"}:
        raise AuditError("'fail_on' must be P0, P1, P2, P3, or none.")

    return AuditConfig(
        exclude=tuple(item.strip() for item in exclude_raw),
        ignore=tuple(ignore_entries),
        fail_on=fail_on,
    )


def compact_evidence(value: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


class MarkupInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_html = False
        self.html_lang: Optional[str] = None
        self.viewport: Optional[Tuple[int, str]] = None
        self.ids: Dict[str, List[int]] = {}
        self.missing_alt: List[Tuple[int, str]] = []
        self.missing_iframe_title: List[Tuple[int, str]] = []
        self.local_references: List[Tuple[int, str, str]] = []

    def handle_startendtag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        self.handle_starttag(tag, attrs)

    def handle_starttag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        tag_name = tag.lower()
        line = self.getpos()[0]
        attr_map = {name.lower(): value for name, value in attrs}

        if tag_name == "html":
            self.has_html = True
            self.html_lang = (attr_map.get("lang") or "").strip()
        if tag_name == "meta" and (attr_map.get("name") or "").lower() == "viewport":
            self.viewport = (line, attr_map.get("content") or "")

        identifier = attr_map.get("id")
        if identifier:
            self.ids.setdefault(identifier, []).append(line)

        if tag_name == "img" and "alt" not in attr_map:
            self.missing_alt.append((line, attr_map.get("src") or "<missing src>"))
        if tag_name == "iframe" and not (attr_map.get("title") or "").strip():
            self.missing_iframe_title.append((line, attr_map.get("src") or "<missing src>"))

        reference: Optional[str] = None
        if tag_name in {"img", "script", "source", "video", "audio", "embed"}:
            reference = attr_map.get("src")
        elif tag_name == "link" and set((attr_map.get("rel") or "").lower().split()).intersection(
            {"stylesheet", "icon", "preload", "modulepreload", "manifest"}
        ):
            reference = attr_map.get("href")
        if reference:
            self.local_references.append((line, tag_name, reference))


class Auditor:
    def __init__(self, root: Path, target: Path, config: AuditConfig) -> None:
        self.root = root
        self.target = target
        self.config = config
        self.findings: List[Finding] = []
        self.suppressed = 0
        self.scanned_files = 0
        self.skipped_files: List[Dict[str, str]] = []

    def add(
        self,
        rule_id: str,
        priority: str,
        confidence: str,
        category: str,
        path: str,
        line: int,
        message: str,
        evidence: str,
        recommendation: str,
    ) -> None:
        if priority not in PRIORITY_ORDER:
            raise ValueError("Unknown priority: {0}".format(priority))
        if confidence not in VALID_CONFIDENCE:
            raise ValueError("Unknown confidence: {0}".format(confidence))
        try:
            metadata = RULE_METADATA[rule_id]
        except KeyError as exc:
            raise ValueError("Missing rule metadata: {0}".format(rule_id)) from exc
        resolved_evidence_level = metadata["evidence_level"]
        resolved_validation_state = metadata["default_validation_state"]
        if resolved_evidence_level not in STATIC_EVIDENCE_LEVELS:
            raise ValueError(
                "Static auditor cannot emit evidence level: {0}".format(
                    resolved_evidence_level
                )
            )
        if resolved_validation_state not in STATIC_VALIDATION_STATES:
            raise ValueError(
                "Static auditor cannot emit validation state: {0}".format(
                    resolved_validation_state
                )
            )
        for entry in self.config.ignore:
            if entry.rule == rule_id and any(path_matches(path, item) for item in entry.paths):
                self.suppressed += 1
                return
        self.findings.append(
            Finding(
                rule_id=rule_id,
                priority=priority,
                confidence=confidence,
                evidence_level=resolved_evidence_level,
                validation_state=resolved_validation_state,
                category=category,
                path=normalized_path(path),
                line=max(1, line),
                message=message,
                evidence=compact_evidence(evidence),
                recommendation=recommendation,
            )
        )

    def relative(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.name

    def analyze(self) -> None:
        files, skipped = collect_files(self.target, self.root, self.config.exclude)
        self.skipped_files.extend(skipped)
        if not files:
            raise AuditError("No supported interface files were found under {0}.".format(self.target))
        for path in files:
            raw, read_error = safe_read_bytes(path)
            if read_error is not None or raw is None:
                self.skipped_files.append(
                    {"path": self.relative(path), "reason": read_error or "read failed"}
                )
                continue
            if b"\x00" in raw:
                self.skipped_files.append(
                    {"path": self.relative(path), "reason": "contains NUL bytes"}
                )
                continue
            encoding_replaced = False
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")
                encoding_replaced = True
            self.scanned_files += 1
            self.analyze_file(path, text, encoding_replaced)
        self.findings.sort(
            key=lambda item: (
                PRIORITY_ORDER[item.priority],
                item.path.lower(),
                item.line,
                item.rule_id,
            )
        )

    def analyze_file(self, path: Path, text: str, encoding_replaced: bool) -> None:
        suffix = path.suffix.lower()
        rel_path = self.relative(path)
        if encoding_replaced:
            self.add(
                "AUI023",
                "P3",
                "high",
                "maintainability",
                rel_path,
                1,
                "The file is not valid UTF-8 and required replacement characters.",
                "Invalid UTF-8 byte sequence",
                "Convert the source to UTF-8 and confirm that visible text is unchanged.",
            )

        if suffix in DOCUMENT_SUFFIXES:
            self.analyze_document(path, text)
        if suffix in MARKUP_SUFFIXES:
            self.analyze_markup_patterns(path, text)
        if suffix in CSS_SUFFIXES:
            self.analyze_css(path, text, text, 0)
        elif suffix in {".html", ".htm", ".vue", ".svelte", ".astro"}:
            for segment, offset in extract_style_segments(text):
                self.analyze_css(path, text, segment, offset)
        elif suffix in SCRIPT_SUFFIXES and re.search(
            r"(?:styled\.|createGlobalStyle|\bcss\s*`)", text
        ):
            self.analyze_css(path, text, text, 0)
        if suffix in SCRIPT_SUFFIXES:
            self.analyze_script(path, text)

    def analyze_document(self, path: Path, text: str) -> None:
        rel_path = self.relative(path)
        parser = MarkupInspector()
        try:
            parser.feed(text)
        except Exception as exc:  # HTMLParser is tolerant; retain a safe diagnostic boundary.
            self.skipped_files.append(
                {"path": rel_path, "reason": "markup parse failed: {0}".format(exc)}
            )
            return

        if parser.viewport is None:
            self.add(
                "AUI001",
                "P1",
                "high",
                "viewport",
                rel_path,
                1,
                "The HTML document has no viewport meta element.",
                "No meta[name=viewport] found",
                "Add width=device-width and initial-scale=1 without disabling zoom.",
            )
        else:
            viewport_line, content = parser.viewport
            lowered = content.lower()
            restricted = "user-scalable=no" in re.sub(r"\s+", "", lowered)
            maximum = re.search(r"maximum-scale\s*=\s*([0-9.]+)", lowered)
            if maximum:
                try:
                    restricted = restricted or float(maximum.group(1)) < 5.0
                except ValueError:
                    restricted = True
            if restricted:
                self.add(
                    "AUI002",
                    "P0",
                    "high",
                    "accessibility",
                    rel_path,
                    viewport_line,
                    "The viewport configuration restricts user zoom.",
                    content,
                    "Remove user-scalable=no and restrictive maximum-scale values.",
                )

        if not parser.has_html or not parser.html_lang:
            self.add(
                "AUI018",
                "P2",
                "high",
                "semantics",
                rel_path,
                1,
                "The document does not declare a non-empty language.",
                "Missing or empty html[lang]",
                "Set the document language, such as lang=\"en\" or lang=\"zh-CN\".",
            )

        for identifier, lines in sorted(parser.ids.items()):
            if len(lines) > 1:
                self.add(
                    "AUI019",
                    "P1",
                    "high",
                    "semantics",
                    rel_path,
                    lines[1],
                    "The document contains a duplicate id.",
                    "id={0!r} appears on lines {1}".format(identifier, lines),
                    "Use a unique id and update labels, fragments, and ARIA references.",
                )

        for line, source in parser.missing_alt:
            self.add(
                "AUI020",
                "P1",
                "high",
                "accessibility",
                rel_path,
                line,
                "An image has no alt attribute.",
                "img src={0!r}".format(source),
                "Add meaningful alternative text or alt=\"\" for a truly decorative image.",
            )

        for line, source in parser.missing_iframe_title:
            self.add(
                "AUI021",
                "P1",
                "high",
                "accessibility",
                rel_path,
                line,
                "An iframe has no accessible title.",
                "iframe src={0!r}".format(source),
                "Add a concise title that identifies the embedded content.",
            )

        for line, tag, reference in parser.local_references:
            resolved = resolve_local_reference(reference, path, self.root)
            if resolved is not None and not resolved.exists():
                self.add(
                    "AUI022",
                    "P1",
                    "high",
                    "resources",
                    rel_path,
                    line,
                    "A local interface resource does not exist.",
                    "{0} reference {1!r}".format(tag, reference),
                    "Correct the path or restore the referenced resource.",
                )

    def analyze_markup_patterns(self, path: Path, text: str) -> None:
        rel_path = self.relative(path)
        checks = (
            (
                "AUI003",
                "P1",
                r"<body\b[^>]*\bclass(?:Name)?\s*=\s*['\"][^'\"]*\boverflow-x-hidden\b",
                "A body utility globally hides horizontal overflow.",
                "Remove the global clipping utility and repair the overflowing descendant.",
            ),
            (
                "AUI004",
                "P2",
                r"\b(?:w-screen|min-w-screen|max-w-screen)\b",
                "A viewport-width utility may include scrollbar or embedding width.",
                "Prefer container-relative width unless the element is intentionally full-bleed.",
            ),
            (
                "AUI005",
                "P2",
                r"\bh-screen\b",
                "A fixed viewport-height utility may be obscured by mobile browser chrome.",
                "Use content height or pair a vh fallback with a dynamic viewport unit.",
            ),
            (
                "AUI006",
                "P1",
                r"\border-(?:first|last|none|[-]?\d+)\b",
                "A utility changes visual order independently of DOM order.",
                "Keep major content in semantic DOM order or document a verified exception.",
            ),
            (
                "AUI007",
                "P1",
                r"\bsnap-mandatory\b",
                "Mandatory scroll snapping can block natural reading and zoomed navigation.",
                "Use native scrolling or proximity snapping only when the interaction requires it.",
            ),
            (
                "AUI009",
                "P2",
                r"\btransition-all\b",
                "A transition-all utility animates unrelated property changes.",
                "List the intended transition properties explicitly.",
            ),
            (
                "AUI010",
                "P1",
                r"\boutline-none\b",
                "A utility removes the focus outline.",
                "Provide a clearly visible focus-visible replacement before removing the outline.",
            ),
        )
        for rule_id, priority, pattern, message, recommendation in checks:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                self.add(
                    rule_id,
                    priority,
                    "medium",
                    category_for_rule(rule_id),
                    rel_path,
                    line_number(text, match.start()),
                    message,
                    match.group(0),
                    recommendation,
                )

    def analyze_css(self, path: Path, full_text: str, css: str, base_offset: int) -> None:
        rel_path = self.relative(path)

        global_clip = re.search(
            r"(?is)(?P<selector>(?:html|body|:root)(?:\s*,\s*(?:html|body|:root))*)\s*"
            r"\{(?P<body>[^{}]*?overflow-x\s*:\s*(?:hidden|clip)[^{}]*?)\}",
            css,
        )
        if global_clip:
            self.add(
                "AUI003",
                "P1",
                "high",
                "overflow",
                rel_path,
                line_number(full_text, base_offset + global_clip.start()),
                "A root selector globally clips horizontal overflow.",
                global_clip.group(0),
                "Find the overflowing descendant and repair its intrinsic or positioned width.",
            )

        viewport_width = re.search(
            r"(?i)(?:inline-size|width|max-width|min-width|max-inline-size|min-inline-size)\s*:"
            r"\s*[^;{}]*\b100vw\b",
            css,
        )
        if viewport_width:
            self.add(
                "AUI004",
                "P2",
                "medium",
                "overflow",
                rel_path,
                line_number(full_text, base_offset + viewport_width.start()),
                "Viewport width sizing may overflow containers or include scrollbar width.",
                viewport_width.group(0),
                "Prefer 100%/100vi in a deliberate containing block, or document full-bleed intent.",
            )

        for height_match in re.finditer(
            r"(?i)(?:block-size|height|min-height|min-block-size)\s*:\s*100vh\b", css
        ):
            block_start = css.rfind("{", 0, height_match.start())
            block_end = css.find("}", height_match.end())
            block = css[max(0, block_start) : block_end if block_end >= 0 else len(css)]
            if re.search(r"100(?:d|s|l)vh\b", block, flags=re.IGNORECASE) is None:
                self.add(
                    "AUI005",
                    "P2",
                    "medium",
                    "viewport",
                    rel_path,
                    line_number(full_text, base_offset + height_match.start()),
                    "A viewport-height declaration has no modern mobile viewport fallback.",
                    height_match.group(0),
                    "Prefer natural height, or add an appropriate dvh/svh declaration after the vh fallback.",
                )
                break

        order_match = re.search(r"(?im)(?<![-\w])order\s*:\s*-?\d+", css)
        if order_match:
            self.add(
                "AUI006",
                "P1",
                "high",
                "semantics",
                rel_path,
                line_number(full_text, base_offset + order_match.start()),
                "CSS changes visual order independently of DOM order.",
                order_match.group(0),
                "Keep major sections in semantic DOM order and reserve order for verified minor decoration.",
            )

        snap_match = re.search(r"(?i)scroll-snap-type\s*:[^;{}]*\bmandatory\b", css)
        if snap_match:
            self.add(
                "AUI007",
                "P1",
                "high",
                "interaction",
                rel_path,
                line_number(full_text, base_offset + snap_match.start()),
                "Mandatory scroll snapping can obstruct natural and zoomed navigation.",
                snap_match.group(0),
                "Use native scrolling or proximity snapping after keyboard and zoom testing.",
            )

        motion_match = re.search(
            r"(?i)(?:animation(?:-name)?|transition(?:-property)?)\s*:", css
        )
        if motion_match and "prefers-reduced-motion" not in css:
            self.add(
                "AUI008",
                "P2",
                "medium",
                "motion",
                rel_path,
                line_number(full_text, base_offset + motion_match.start()),
                "Motion is declared without a reduced-motion branch in this stylesheet.",
                motion_match.group(0),
                "Disable or simplify non-essential motion under prefers-reduced-motion: reduce.",
            )

        transition_all = re.search(r"(?i)transition(?:-property)?\s*:[^;{}]*\ball\b", css)
        if transition_all:
            self.add(
                "AUI009",
                "P2",
                "high",
                "motion",
                rel_path,
                line_number(full_text, base_offset + transition_all.start()),
                "A transition animates all changing properties.",
                transition_all.group(0),
                "List only the properties whose animation communicates state.",
            )

        outline = re.search(
            r"(?i)outline(?:-style)?\s*:\s*(?:none|0(?:[a-z%]+)?)(?![\w.])", css
        )
        if outline:
            self.add(
                "AUI010",
                "P1",
                "medium",
                "focus",
                rel_path,
                line_number(full_text, base_offset + outline.start()),
                "A declaration removes the visible focus outline.",
                outline.group(0),
                "Confirm the same selector provides a visible keyboard focus replacement.",
            )

        important_matches = collect_important_outside_reduced_motion(css)
        if len(important_matches) >= 3:
            self.add(
                "AUI011",
                "P2",
                "high",
                "maintainability",
                rel_path,
                line_number(full_text, base_offset + important_matches[0].start()),
                "The stylesheet accumulates multiple !important overrides.",
                "{0} occurrences of !important".format(len(important_matches)),
                "Resolve specificity and source-order ownership instead of appending overrides.",
            )

        breakpoints = collect_breakpoints(css)
        if len(breakpoints) > 6:
            first_media = re.search(r"@media\b", css, flags=re.IGNORECASE)
            self.add(
                "AUI012",
                "P2",
                "medium",
                "responsive",
                rel_path,
                line_number(full_text, base_offset + (first_media.start() if first_media else 0)),
                "The stylesheet uses many distinct viewport breakpoints.",
                "{0} distinct breakpoints: {1}".format(
                    len(breakpoints), ", ".join(format_number(item) + "px" for item in breakpoints)
                ),
                "Merge near-duplicates and retain only breakpoints tied to structural content pressure.",
            )

        radii = collect_literal_radii(css)
        if len(radii) >= 6:
            first_radius = re.search(r"border(?:-[a-z]+)*-radius\s*:", css, flags=re.IGNORECASE)
            self.add(
                "AUI013",
                "P2",
                "medium",
                "visual-system",
                rel_path,
                line_number(full_text, base_offset + (first_radius.start() if first_radius else 0)),
                "The stylesheet uses a fragmented literal radius scale.",
                "{0} distinct values: {1}".format(len(radii), ", ".join(sorted(radii))),
                "Map radii to semantic control, button, card, panel, showcase, pill, and circle tokens.",
            )

    def analyze_script(self, path: Path, text: str) -> None:
        rel_path = self.relative(path)
        event_match = re.search(
            r"addEventListener\s*\(\s*['\"](?:wheel|touchmove)['\"]", text
        )
        if event_match and re.search(r"\.preventDefault\s*\(", text):
            self.add(
                "AUI014",
                "P1",
                "medium",
                "interaction",
                rel_path,
                line_number(text, event_match.start()),
                "A global-style wheel or touch listener may intercept native scrolling.",
                event_match.group(0),
                "Remove interception for content pages or constrain it to a justified component with escape behavior.",
            )

        viewport_match = re.search(
            r"(?:window\.)?(?:innerWidth|outerWidth)|document\.documentElement\.clientWidth", text
        )
        layout_write = re.search(
            r"(?:\.style\.(?:width|height|transform)|\.style\.setProperty|setAttribute\s*\(\s*['\"]style)",
            text,
        )
        if viewport_match and layout_write:
            self.add(
                "AUI015",
                "P2",
                "medium",
                "complexity",
                rel_path,
                line_number(text, viewport_match.start()),
                "JavaScript reads viewport width and writes layout styles.",
                viewport_match.group(0) + " … " + layout_write.group(0),
                "Move continuous sizing to CSS; keep JavaScript only for semantic state that CSS cannot express.",
            )

        clone_match = re.search(r"\.cloneNode\s*\(", text)
        if clone_match:
            self.add(
                "AUI016",
                "P2",
                "high",
                "complexity",
                rel_path,
                line_number(text, clone_match.start()),
                "The interface clones DOM content, commonly for an infinite carousel.",
                clone_match.group(0),
                "Prefer a finite native sequence or verify semantics, focus, IDs, and duplicate announcements.",
            )

        interval_match = re.search(r"\bsetInterval\s*\(", text)
        if interval_match and re.search(r"carousel|slider?|advance|nextSlide", text, flags=re.IGNORECASE):
            self.add(
                "AUI017",
                "P2",
                "medium",
                "motion",
                rel_path,
                line_number(text, interval_match.start()),
                "A carousel-like interface appears to advance on a timer.",
                interval_match.group(0),
                "Require a user goal, pause controls, focus/hover pause, and reduced-motion behavior.",
            )

    def result(
        self,
        config_path: Optional[Path],
        absolute_paths: bool = False,
        redact_evidence: bool = False,
    ) -> Dict[str, Any]:
        counts = {priority: 0 for priority in PRIORITY_ORDER}
        for finding in self.findings:
            counts[finding.priority] += 1
        findings = [asdict(item) for item in self.findings]
        if redact_evidence:
            for item in findings:
                item["evidence"] = "[redacted]"
        return {
            "schema_version": SCHEMA_VERSION,
            "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
            "target": report_path(self.target, self.root, absolute_paths, "<external-target>"),
            "config": (
                report_path(config_path, self.root, absolute_paths, "<external-config>")
                if config_path
                else None
            ),
            "summary": {
                "files_scanned": self.scanned_files,
                "files_skipped": len(self.skipped_files),
                "findings": len(self.findings),
                "suppressed": self.suppressed,
                "by_priority": counts,
            },
            "findings": findings,
            "skipped_files": self.skipped_files,
        }


def category_for_rule(rule_id: str) -> str:
    return {
        "AUI003": "overflow",
        "AUI004": "overflow",
        "AUI005": "viewport",
        "AUI006": "semantics",
        "AUI007": "interaction",
        "AUI009": "motion",
        "AUI010": "focus",
    }.get(rule_id, "responsive")


def collect_files(
    target: Path, root: Path, extra_patterns: Sequence[str]
) -> Tuple[List[Path], List[Dict[str, str]]]:
    if target.is_file():
        files = [target] if target.suffix.lower() in SUPPORTED_SUFFIXES else []
        return files, []

    files: List[Path] = []
    skipped: List[Dict[str, str]] = []
    patterns = tuple(DEFAULT_EXCLUDE_PATTERNS) + tuple(extra_patterns)
    for current, directories, names in os.walk(str(target), followlinks=False):
        current_path = Path(current)
        retained: List[str] = []
        for directory in directories:
            candidate = current_path / directory
            rel = safe_relative(candidate, root)
            if directory in DEFAULT_EXCLUDE_DIRS or any(
                path_matches(rel, pattern) for pattern in extra_patterns
            ):
                continue
            try:
                if is_link_or_reparse(candidate):
                    skipped.append({"path": rel, "reason": "symbolic link or reparse point"})
                    continue
            except OSError as exc:
                skipped.append({"path": rel, "reason": sanitized_os_error("stat failed", exc)})
                continue
            retained.append(directory)
        directories[:] = retained

        for name in names:
            path = current_path / name
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            rel = safe_relative(path, root)
            if any(path_matches(rel, pattern) for pattern in patterns):
                continue
            try:
                if is_link_or_reparse(path):
                    skipped.append({"path": rel, "reason": "symbolic link or reparse point"})
                    continue
            except OSError as exc:
                skipped.append({"path": rel, "reason": sanitized_os_error("stat failed", exc)})
                continue
            files.append(path)
    return (
        sorted(files, key=lambda item: normalized_path(str(item)).lower()),
        sorted(skipped, key=lambda item: (item["path"].lower(), item["reason"])),
    )


def safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def report_path(path: Path, root: Path, absolute: bool, external_label: str) -> str:
    if absolute:
        return str(path)
    if is_within(path, root):
        return path.relative_to(root).as_posix()
    return external_label


def resolve_local_reference(reference: str, source: Path, root: Path) -> Optional[Path]:
    value = reference.strip()
    if not value or any(token in value for token in ("{{", "}}", "${", "<%", "%>")):
        return None
    lowered = value.lower()
    if lowered.startswith(("data:", "http:", "https:", "//", "mailto:", "tel:", "javascript:", "blob:", "#")):
        return None
    parsed = urlsplit(value)
    path_value = unquote(parsed.path)
    if not path_value or path_value.startswith(("@/", "~/")):
        return None
    if path_value.startswith("/"):
        candidate = root / path_value.lstrip("/")
    else:
        candidate = source.parent / path_value

    lexical_root = absolute_path(root)
    lexical_candidate = absolute_path(candidate)
    if not is_within(lexical_candidate, lexical_root):
        return None

    cursor = lexical_root
    for part in lexical_candidate.relative_to(lexical_root).parts:
        cursor = cursor / part
        try:
            info = os.lstat(os.fspath(cursor))
        except FileNotFoundError:
            break
        except OSError:
            return None
        if stat_is_link_or_reparse(info):
            return None
    return lexical_candidate


def extract_style_segments(text: str) -> Iterable[Tuple[str, int]]:
    for match in re.finditer(r"(?is)<style\b[^>]*>(.*?)</style\s*>", text):
        yield match.group(1), match.start(1)


def collect_important_outside_reduced_motion(css: str) -> List[re.Match[str]]:
    ranges: List[Tuple[int, int]] = []
    for media in re.finditer(
        r"(?is)@media\b[^{}]*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)[^{]*\{",
        css,
    ):
        start = media.end()
        depth = 1
        for index in range(start, len(css)):
            if css[index] == "{":
                depth += 1
            elif css[index] == "}":
                depth -= 1
                if depth == 0:
                    ranges.append((start, index))
                    break
    return [
        match
        for match in re.finditer(r"!important\b", css, flags=re.IGNORECASE)
        if not any(start <= match.start() < end for start, end in ranges)
    ]


def collect_breakpoints(css: str) -> List[float]:
    values: Set[float] = set()
    pattern = re.compile(
        r"(?is)@media[^{}]*\((?:min|max)-(?:width|inline-size)\s*:\s*([0-9.]+)(px|rem|em)\)"
    )
    for match in pattern.finditer(css):
        value = float(match.group(1))
        if match.group(2).lower() in {"rem", "em"}:
            value *= 16.0
        values.add(round(value, 2))
    return sorted(values)


def collect_literal_radii(css: str) -> Set[str]:
    values: Set[str] = set()
    pattern = re.compile(r"(?i)border(?:-[a-z]+)*-radius\s*:\s*([^;{}]+)")
    for match in pattern.finditer(css):
        value = re.sub(r"\s+", " ", match.group(1).strip().lower())
        value = re.sub(r"\s*!important\s*$", "", value)
        if any(token in value for token in ("var(", "calc(", "clamp(", "env(")):
            continue
        if value in {"0", "0px", "0rem", "50%", "999px", "9999px", "inherit", "initial"}:
            continue
        if re.fullmatch(r"[0-9.]+(?:px|rem|em|%)", value):
            values.add(value)
    return values


def format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else str(value)


def normalize_fail_on(value: str) -> str:
    return "none" if value.lower() == "none" else value.upper()


def threshold_breached(findings: Sequence[Finding], threshold: str) -> bool:
    if threshold == "none":
        return False
    limit = PRIORITY_ORDER[threshold]
    return any(PRIORITY_ORDER[item.priority] <= limit for item in findings)


def format_text(result: Dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "Adaptive UI Engineer {0}".format(result["tool"]["version"]),
        "Target: {0}".format(result["target"]),
        "Scanned: {0} | Skipped: {1} | Findings: {2} | Suppressed: {3}".format(
            summary["files_scanned"],
            summary["files_skipped"],
            summary["findings"],
            summary["suppressed"],
        ),
        "Priorities: P0={P0} P1={P1} P2={P2} P3={P3}".format(
            **summary["by_priority"]
        ),
    ]
    if not result["findings"]:
        lines.append("No findings.")
    for item in result["findings"]:
        lines.extend(
            [
                "",
                "[{priority}] {rule_id} {path}:{line} ({confidence} confidence)".format(**item),
                item["message"],
                "Evidence level: {evidence_level} | Validation: {validation_state}".format(
                    **item
                ),
                "Evidence: {0}".format(item["evidence"]),
                "Recommendation: {0}".format(item["recommendation"]),
            ]
        )
    if result["skipped_files"]:
        lines.append("")
        lines.append("Skipped files:")
        for item in result["skipped_files"]:
            lines.append("- {0}: {1}".format(item["path"], item["reason"]))
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only responsive UI and accessibility triage."
    )
    parser.add_argument("target", help="Interface file or project directory to audit")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--config", help="Path to .adaptive-ui-engineer.json")
    parser.add_argument(
        "--fail-on",
        type=normalize_fail_on,
        choices=("P0", "P1", "P2", "P3", "none"),
        help="Return exit code 1 when this priority or a higher one is present",
    )
    parser.add_argument(
        "--absolute-paths",
        action="store_true",
        help="Include absolute target and configuration paths in the report",
    )
    parser.add_argument(
        "--redact-evidence",
        action="store_true",
        help="Replace source excerpts with a redaction marker for report sharing",
    )
    parser.add_argument("--output", help="Write the report to this file instead of stdout")
    parser.add_argument("--version", action="version", version=TOOL_VERSION)
    return parser


def configure_utf8_streams() -> None:
    """Make redirected CLI output deterministic across Windows and POSIX hosts."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def write_report(path: Path, report: str) -> None:
    """Write a report atomically and refuse an existing link destination."""

    if path_traverses_link_or_reparse(path.parent):
        raise AuditError("Output path must not traverse a symbolic link or reparse point.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path_traverses_link_or_reparse(path.parent):
        raise AuditError("Output path must not traverse a symbolic link or reparse point.")
    if os.path.lexists(os.fspath(path)):
        try:
            destination = os.lstat(os.fspath(path))
        except OSError as exc:
            raise AuditError(
                "Cannot inspect output destination: {0}".format(
                    sanitized_os_error("stat failed", exc)
                )
            ) from exc
        if stat_is_link_or_reparse(destination):
            raise AuditError("Output destination must not be a symbolic link or reparse point.")
        if not stat.S_ISREG(destination.st_mode):
            raise AuditError("Output destination must be a regular file.")

    temporary: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=".adaptive-ui-engineer-",
            suffix=".tmp",
            dir=str(path.parent),
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(report)
        os.replace(os.fspath(temporary), os.fspath(path))
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def run(argv: Optional[Sequence[str]] = None) -> int:
    configure_utf8_streams()
    args = build_parser().parse_args(argv)
    try:
        target = absolute_path(Path(args.target).expanduser())
        try:
            target_info = os.lstat(os.fspath(target))
        except FileNotFoundError:
            raise AuditError("Target does not exist: {0}".format(target))
        if stat_is_link_or_reparse(target_info):
            raise AuditError("Target must not be a symbolic link or reparse point.")
        if not (stat.S_ISDIR(target_info.st_mode) or stat.S_ISREG(target_info.st_mode)):
            raise AuditError("Target must be a regular file or directory.")
        root = target if stat.S_ISDIR(target_info.st_mode) else target.parent

        config_path: Optional[Path]
        if args.config:
            config_path = absolute_path(Path(args.config).expanduser())
        else:
            candidate = root / ".adaptive-ui-engineer.json"
            config_path = candidate if os.path.lexists(os.fspath(candidate)) else None
        config = load_config(config_path)

        auditor = Auditor(root=root, target=target, config=config)
        auditor.analyze()
        result = auditor.result(
            config_path,
            absolute_paths=args.absolute_paths,
            redact_evidence=args.redact_evidence,
        )
        report = (
            json.dumps(result, ensure_ascii=False, indent=2) + "\n"
            if args.format == "json"
            else format_text(result)
        )

        if args.output:
            output = absolute_path(Path(args.output).expanduser())
            write_report(output, report)
        else:
            sys.stdout.write(report)

        fail_on = args.fail_on if args.fail_on is not None else config.fail_on
        return 1 if threshold_breached(auditor.findings, fail_on) else 0
    except (AuditError, OSError, UnicodeError) as exc:
        sys.stderr.write("adaptive-ui-engineer: {0}\n".format(exc))
        return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
