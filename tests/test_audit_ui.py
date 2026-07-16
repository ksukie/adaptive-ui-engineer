from __future__ import annotations

import importlib.util
import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins"
    / "adaptive-ui-engineer"
    / "skills"
    / "adaptive-ui-s"
    / "scripts"
    / "audit_ui.py"
)
FIXTURES = ROOT / "tests" / "fixtures"
REPORT_SCHEMA = SCRIPT.parent.parent / "assets" / "audit-report.schema.json"


def load_auditor_module():
    spec = importlib.util.spec_from_file_location("adaptive_ui_auditor_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load auditor module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def resolved_temporary_directory():
    """Create test directories below the canonical system temp path."""

    base = Path(tempfile.gettempdir()).resolve()
    return tempfile.TemporaryDirectory(dir=str(base))


class AuditCliTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCRIPT), *(str(item) for item in arguments)]
        return subprocess.run(
            command,
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def run_json(self, target: Path, *arguments: object) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = self.run_cli(target, "--format", "json", *arguments)
        payload = json.loads(result.stdout)
        return result, payload

    def create_symlink_or_skip(
        self, target: Path, link: Path, target_is_directory: bool = False
    ) -> None:
        try:
            link.symlink_to(target, target_is_directory=target_is_directory)
        except (NotImplementedError, OSError) as exc:
            self.skipTest("Symbolic links are unavailable in this environment: {0}".format(exc))

    def test_version(self) -> None:
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "1.1.0")

    def test_good_fixture_has_no_high_priority_findings(self) -> None:
        result, payload = self.run_json(FIXTURES / "good", "--fail-on", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["tool"]["name"], "adaptive-ui-engineer")
        self.assertEqual(payload["summary"]["by_priority"]["P0"], 0)
        self.assertEqual(payload["summary"]["by_priority"]["P1"], 0)
        self.assertGreaterEqual(payload["summary"]["files_scanned"], 3)
        for finding in payload["findings"]:
            self.assertNotIn("\\", finding["path"])

    def test_foundation_asset_does_not_trigger_avoidable_rules(self) -> None:
        foundation = SCRIPT.parent.parent / "assets" / "responsive-foundation.css"
        result, payload = self.run_json(foundation, "--fail-on", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        rule_ids = {item["rule_id"] for item in payload["findings"]}
        self.assertNotIn("AUI010", rule_ids)
        self.assertNotIn("AUI011", rule_ids)

    def test_findings_follow_report_schema_metadata_enums(self) -> None:
        result, payload = self.run_json(FIXTURES / "bad", "--fail-on", "none")
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        finding_schema = schema["$defs"]["finding"]

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["schema_version"], schema["properties"]["schema_version"]["const"])
        for finding in payload["findings"]:
            self.assertEqual(set(finding), set(finding_schema["required"]))
            for field in ("confidence", "evidence_level", "validation_state"):
                self.assertIn(finding[field], finding_schema["properties"][field]["enum"])

    def test_rule_defaults_distinguish_observation_inference_and_review(self) -> None:
        result, payload = self.run_json(FIXTURES / "bad", "--fail-on", "none")
        by_rule = {item["rule_id"]: item for item in payload["findings"]}

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (by_rule["AUI020"]["evidence_level"], by_rule["AUI020"]["validation_state"]),
            ("source_observed", "not_applicable"),
        )
        self.assertEqual(
            (by_rule["AUI004"]["evidence_level"], by_rule["AUI004"]["validation_state"]),
            ("static_inferred", "not_run"),
        )
        self.assertEqual(by_rule["AUI008"]["validation_state"], "manual_review_needed")

    def test_static_auditor_cannot_emit_runtime_only_states(self) -> None:
        auditor_module = load_auditor_module()
        add_parameters = inspect.signature(auditor_module.Auditor.add).parameters
        self.assertNotIn("evidence_level", add_parameters)
        self.assertNotIn("validation_state", add_parameters)
        finding_schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))["$defs"][
            "finding"
        ]
        self.assertEqual(
            auditor_module.VALID_VALIDATION_STATES,
            set(finding_schema["properties"]["validation_state"]["enum"]),
        )
        self.assertEqual(
            auditor_module.VALID_EVIDENCE_LEVELS,
            set(finding_schema["properties"]["evidence_level"]["enum"]),
        )
        self.assertEqual(
            set(auditor_module.RULE_METADATA),
            {"AUI{0:03d}".format(number) for number in range(1, 24)},
        )
        self.assertNotIn("runtime_observed", auditor_module.STATIC_EVIDENCE_LEVELS)
        self.assertTrue(
            {"reproduced", "not_reproduced"}.isdisjoint(
                auditor_module.STATIC_VALIDATION_STATES
            )
        )
        for metadata in auditor_module.RULE_METADATA.values():
            self.assertIn(
                metadata["evidence_level"], auditor_module.STATIC_EVIDENCE_LEVELS
            )
            self.assertIn(
                metadata["default_validation_state"],
                auditor_module.STATIC_VALIDATION_STATES,
            )

    def test_bad_fixture_reports_expected_rules(self) -> None:
        result, payload = self.run_json(FIXTURES / "bad", "--fail-on", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        rule_ids = {item["rule_id"] for item in payload["findings"]}
        expected = {"AUI{0:03d}".format(number) for number in range(2, 23)}
        expected.discard("AUI001")
        self.assertTrue(expected.issubset(rule_ids), sorted(expected - rule_ids))
        self.assertIn("AUI002", rule_ids)
        self.assertIn("AUI019", rule_ids)
        self.assertIn("AUI022", rule_ids)

    def test_missing_viewport_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text("<!doctype html><html lang=\"en\"><body>Text</body></html>", encoding="utf-8")
            result, payload = self.run_json(page, "--fail-on", "none")
        self.assertEqual(result.returncode, 0)
        self.assertIn("AUI001", {item["rule_id"] for item in payload["findings"]})

    def test_priority_threshold_returns_one(self) -> None:
        result = self.run_cli(FIXTURES / "bad", "--format", "text", "--fail-on", "P1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("[P0] AUI002", result.stdout)
        self.assertIn("Evidence level: source_observed | Validation: not_applicable", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_default_threshold_does_not_fail(self) -> None:
        result = self.run_cli(FIXTURES / "bad", "--format", "text")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Findings:", result.stdout)

    def test_config_suppresses_rule_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                "<!doctype html><html lang=\"en\"><head>"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
                "<link rel=\"stylesheet\" href=\"style.css\"></head><body>OK</body></html>",
                encoding="utf-8",
            )
            (root / "style.css").write_text(".full { width: 100vw; }", encoding="utf-8")
            (root / ".adaptive-ui-engineer.json").write_text(
                json.dumps(
                    {
                        "ignore": [
                            {
                                "rule": "AUI004",
                                "paths": ["style.css"],
                                "reason": "Intentional full-bleed background.",
                            }
                        ],
                        "fail_on": "P1",
                    }
                ),
                encoding="utf-8",
            )
            result, payload = self.run_json(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["summary"]["suppressed"], 1)
        self.assertNotIn("AUI004", {item["rule_id"] for item in payload["findings"]})

    def test_config_excludes_generated_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ignored = root / "generated"
            ignored.mkdir()
            (root / "index.html").write_text(
                "<!doctype html><html lang=\"en\"><head>"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
                "</head><body>OK</body></html>",
                encoding="utf-8",
            )
            (ignored / "bad.css").write_text("body { overflow-x: hidden; }", encoding="utf-8")
            config = root / "audit.json"
            config.write_text(json.dumps({"exclude": ["generated/**"]}), encoding="utf-8")
            result, payload = self.run_json(root, "--config", config, "--fail-on", "none")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["summary"]["files_scanned"], 1)
        self.assertNotIn("AUI003", {item["rule_id"] for item in payload["findings"]})

    def test_output_file_contains_json_and_stdout_is_empty(self) -> None:
        with resolved_temporary_directory() as directory:
            output = Path(directory) / "nested" / "report.json"
            result = self.run_cli(
                FIXTURES / "good",
                "--format",
                "json",
                "--fail-on",
                "none",
                "--output",
                output,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 2)

    def test_invalid_config_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text("<html></html>", encoding="utf-8")
            config = root / "bad.json"
            config.write_text('{"unknown": true}', encoding="utf-8")
            result = self.run_cli(root, "--config", config)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown configuration keys", result.stderr)

    def test_missing_target_returns_two(self) -> None:
        result = self.run_cli(ROOT / "tests" / "does-not-exist")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Target does not exist", result.stderr)

    def test_invalid_utf8_is_handled_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_bytes(
                b'<!doctype html><html lang="en"><head><meta name="viewport" '
                b'content="width=device-width, initial-scale=1"></head><body>\xff</body></html>'
            )
            result, payload = self.run_json(page, "--fail-on", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AUI023", {item["rule_id"] for item in payload["findings"]})

    def test_framework_fixtures_scan_without_parser_failure(self) -> None:
        result, payload = self.run_json(FIXTURES / "frameworks", "--fail-on", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["summary"]["files_scanned"], 4)
        self.assertEqual(payload["summary"]["files_skipped"], 0)

    def test_json_output_is_deterministic_for_same_target(self) -> None:
        first, payload_one = self.run_json(FIXTURES / "bad", "--fail-on", "none")
        second, payload_two = self.run_json(FIXTURES / "bad", "--fail-on", "none")
        self.assertEqual(first.returncode, second.returncode)
        self.assertEqual(payload_one, payload_two)

    def test_report_paths_are_private_by_default_and_absolute_only_on_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "site"
            root.mkdir()
            (root / "index.html").write_text(
                '<!doctype html><html lang="en"><head><meta name="viewport" '
                'content="width=device-width, initial-scale=1"></head><body>OK</body></html>',
                encoding="utf-8",
            )
            external_config = parent / "audit.json"
            external_config.write_text("{}", encoding="utf-8")

            default_result, default_payload = self.run_json(
                root, "--config", external_config, "--fail-on", "none"
            )
            absolute_result, absolute_payload = self.run_json(
                root,
                "--config",
                external_config,
                "--absolute-paths",
                "--fail-on",
                "none",
            )

        self.assertEqual(default_result.returncode, 0, default_result.stderr)
        self.assertEqual(default_payload["target"], ".")
        self.assertEqual(default_payload["config"], "<external-config>")
        self.assertNotIn(str(parent), json.dumps(default_payload))
        self.assertEqual(absolute_result.returncode, 0, absolute_result.stderr)
        self.assertEqual(Path(absolute_payload["target"]), root)
        self.assertEqual(Path(absolute_payload["config"]), external_config)

    def test_redact_evidence_replaces_every_source_excerpt(self) -> None:
        result, payload = self.run_json(
            FIXTURES / "bad", "--redact-evidence", "--fail-on", "none"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(len(payload["findings"]), 0)
        self.assertEqual({item["evidence"] for item in payload["findings"]}, {"[redacted]"})

    def test_symlinked_source_is_skipped_without_reading_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "site"
            root.mkdir()
            (root / "index.html").write_text(
                '<!doctype html><html lang="en"><head><meta name="viewport" '
                'content="width=device-width, initial-scale=1"></head><body>OK</body></html>',
                encoding="utf-8",
            )
            outside = parent / "outside.css"
            outside.write_text("body { overflow-x: hidden; }", encoding="utf-8")
            self.create_symlink_or_skip(outside, root / "leak.css")

            result, payload = self.run_json(root, "--fail-on", "none")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("AUI003", {item["rule_id"] for item in payload["findings"]})
        self.assertIn(
            {"path": "leak.css", "reason": "symbolic link or reparse point"},
            payload["skipped_files"],
        )

    def test_symlink_target_is_rejected_with_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            target = parent / "index.html"
            target.write_text("<html></html>", encoding="utf-8")
            link = parent / "linked.html"
            self.create_symlink_or_skip(target, link)
            result = self.run_cli(link)
        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be a symbolic link or reparse point", result.stderr)

    def test_symlinked_automatic_config_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "site"
            root.mkdir()
            (root / "index.html").write_text("<html></html>", encoding="utf-8")
            outside = parent / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            self.create_symlink_or_skip(outside, root / ".adaptive-ui-engineer.json")
            result = self.run_cli(root)
        self.assertEqual(result.returncode, 2)
        self.assertIn("symbolic link or reparse point", result.stderr)

    def test_local_reference_cannot_escape_audit_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "site"
            root.mkdir()
            (root / "index.html").write_text(
                '<!doctype html><html lang="en"><head><meta name="viewport" '
                'content="width=device-width, initial-scale=1">'
                '<link rel="stylesheet" href="../outside/missing.css">'
                '</head><body>OK</body></html>',
                encoding="utf-8",
            )
            result, payload = self.run_json(root, "--fail-on", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("AUI022", {item["rule_id"] for item in payload["findings"]})

    def test_output_symlink_is_rejected_without_changing_its_target(self) -> None:
        with resolved_temporary_directory() as directory:
            root = Path(directory)
            outside = root / "outside.txt"
            outside.write_text("preserve me", encoding="utf-8")
            link = root / "report.json"
            self.create_symlink_or_skip(outside, link)
            result = self.run_cli(
                FIXTURES / "good",
                "--format",
                "json",
                "--fail-on",
                "none",
                "--output",
                link,
            )
            preserved = outside.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Output destination must not be", result.stderr)
        self.assertEqual(preserved, "preserve me")

    def test_output_path_cannot_traverse_a_linked_directory(self) -> None:
        with resolved_temporary_directory() as directory:
            parent = Path(directory)
            root = parent / "site"
            root.mkdir()
            outside = parent / "outside"
            outside.mkdir()
            victim = outside / "report.json"
            victim.write_text("preserve me", encoding="utf-8")
            linked_parent = root / "reports"
            self.create_symlink_or_skip(outside, linked_parent, target_is_directory=True)
            result = self.run_cli(
                FIXTURES / "good",
                "--format",
                "json",
                "--fail-on",
                "none",
                "--output",
                linked_parent / "report.json",
            )
            preserved = victim.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Output path must not traverse", result.stderr)
        self.assertEqual(preserved, "preserve me")

    def test_nul_and_oversized_sources_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<!doctype html><html lang="en"><head><meta name="viewport" '
                'content="width=device-width, initial-scale=1"></head><body>OK</body></html>',
                encoding="utf-8",
            )
            (root / "nul.css").write_bytes(b"body{}\x00hidden")
            (root / "large.css").write_bytes(b"x" * (2 * 1024 * 1024 + 1))
            result, payload = self.run_json(root, "--fail-on", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        reasons = {item["path"]: item["reason"] for item in payload["skipped_files"]}
        self.assertEqual(reasons["nul.css"], "contains NUL bytes")
        self.assertEqual(reasons["large.css"], "larger than 2 MiB")


if __name__ == "__main__":
    unittest.main()
