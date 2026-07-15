from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import ValidationError
except ImportError:  # The validator is installed only in its pinned CI job.
    Draft202012Validator = None
    ValidationError = Exception


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "adaptive-ui-engineer" / "skills" / "adaptive-ui-s"
SCRIPT = SKILL / "scripts" / "audit_ui.py"
SCHEMA = SKILL / "assets" / "audit-report.schema.json"
FIXTURE = ROOT / "tests" / "fixtures" / "bad"


@unittest.skipIf(Draft202012Validator is None, "jsonschema is a pinned CI-only dependency")
class AuditReportSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(FIXTURE),
                "--format",
                "json",
                "--fail-on",
                "none",
            ],
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        cls.report = json.loads(result.stdout)

    def test_complete_cli_report_matches_schema(self) -> None:
        self.validator.validate(self.report)

    def test_schema_rejects_invalid_finding_shapes(self) -> None:
        missing = copy.deepcopy(self.report)
        del missing["findings"][0]["validation_state"]
        with self.assertRaises(ValidationError):
            self.validator.validate(missing)

        extra = copy.deepcopy(self.report)
        extra["findings"][0]["unexpected"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(extra)

        invalid = copy.deepcopy(self.report)
        invalid["findings"][0]["validation_state"] = "browser_checked"
        with self.assertRaises(ValidationError):
            self.validator.validate(invalid)

        impossible = copy.deepcopy(self.report)
        impossible["findings"][0]["validation_state"] = "reproduced"
        impossible["findings"][0]["evidence_level"] = "static_inferred"
        with self.assertRaises(ValidationError):
            self.validator.validate(impossible)

        wrong_type = copy.deepcopy(self.report)
        wrong_type["findings"][0]["line"] = "1"
        with self.assertRaises(ValidationError):
            self.validator.validate(wrong_type)


if __name__ == "__main__":
    unittest.main()
