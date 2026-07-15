from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "adaptive-ui-engineer"
S_SKILL = PLUGIN / "skills" / "adaptive-ui-s"
N_SKILL = PLUGIN / "skills" / "adaptive-ui-n"
SKILL = S_SKILL
SKILLS = {
    "adaptive-ui-s": S_SKILL,
    "adaptive-ui-n": N_SKILL,
}


class PackageContractTests(unittest.TestCase):
    def test_required_public_files_exist(self) -> None:
        paths = [
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            ROOT / "LICENSE",
            ROOT / "CONTRIBUTING.md",
            ROOT / "SECURITY.md",
            ROOT / "DISCLAIMER.md",
            ROOT / "DISCLAIMER.zh-CN.md",
            ROOT / "CHANGELOG.md",
            ROOT / "RELEASE_CHECKLIST.md",
            ROOT / ".github" / "workflows" / "ci.yml",
            ROOT / ".github" / "workflows" / "codeql.yml",
            ROOT / ".github" / "dependabot.yml",
            ROOT / ".github" / "requirements" / "skills-ref.txt",
            ROOT / ".github" / "scripts" / "run_skills_ref.py",
            ROOT / ".agents" / "plugins" / "marketplace.json",
            PLUGIN / ".codex-plugin" / "plugin.json",
            S_SKILL / "SKILL.md",
            S_SKILL / "agents" / "openai.yaml",
            S_SKILL / "assets" / "audit-report.schema.json",
            N_SKILL / "SKILL.md",
            N_SKILL / "agents" / "openai.yaml",
        ]
        self.assertEqual([str(path) for path in paths if not path.is_file()], [])

    def test_plugin_manifest_contract(self) -> None:
        manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "adaptive-ui-engineer")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(manifest["license"], "Apache-2.0")
        self.assertEqual(manifest["author"]["name"], "ksukie")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertNotIn("hooks", manifest)
        interface = manifest["interface"]
        self.assertEqual(interface["displayName"], "Adaptive UI Engineer")
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        self.assertTrue(all(len(item) <= 128 for item in interface["defaultPrompt"]))
        for field in ("composerIcon", "logo"):
            path = PLUGIN / interface[field].removeprefix("./")
            self.assertTrue(path.is_file(), str(path))

    def test_marketplace_points_to_plugin(self) -> None:
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["name"], "adaptive-ui-engineer")
        self.assertEqual(marketplace["interface"]["displayName"], "Adaptive UI Engineer")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "adaptive-ui-engineer")
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        source = ROOT / entry["source"]["path"].removeprefix("./")
        self.assertEqual(source.resolve(), PLUGIN.resolve())

    def test_skill_frontmatter_is_minimal_and_name_matches(self) -> None:
        for name, skill in SKILLS.items():
            with self.subTest(skill=name):
                content = (skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertLessEqual(len(content.splitlines()), 500)
                self.assertNotIn("TODO", content)
                match = re.match(r"^---\n(.*?)\n---\n", content, flags=re.DOTALL)
                self.assertIsNotNone(match)
                keys = [line.split(":", 1)[0] for line in match.group(1).splitlines() if ":" in line]
                self.assertEqual(keys, ["name", "description"])
                self.assertIn("name: {0}".format(name), match.group(1))

    def test_skill_resource_links_resolve(self) -> None:
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(((?:references|assets)/[^)]+)\)", content)
        self.assertGreaterEqual(len(set(links)), 9)
        missing = [link for link in sorted(set(links)) if not (SKILL / link).is_file()]
        self.assertEqual(missing, [])

    def test_skill_documents_a_resolved_auditor_path(self) -> None:
        documents = [
            SKILL / "SKILL.md",
            SKILL / "references" / "verification-protocol.md",
        ]
        for path in documents:
            content = path.read_text(encoding="utf-8")
            self.assertIn("<skill-root>/scripts/audit_ui.py", content)
            self.assertNotIn("python scripts/audit_ui.py", content)

    def test_openai_metadata_references_real_assets_and_skill(self) -> None:
        metadata = {
            "adaptive-ui-s": (S_SKILL, "Adaptive-UI-S", "$adaptive-ui-s"),
            "adaptive-ui-n": (N_SKILL, "Adaptive-UI-N", "$adaptive-ui-n"),
        }
        for name, (skill, display_name, invocation) in metadata.items():
            with self.subTest(skill=name):
                content = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
                self.assertIn('display_name: "{0}"'.format(display_name), content)
                self.assertIn(invocation, content)
                self.assertIn("allow_implicit_invocation: false", content)
                self.assertNotIn("allow_implicit_invocation: true", content)
                match = re.search(r'^  short_description: "([^"]+)"$', content, flags=re.MULTILINE)
                self.assertIsNotNone(match)
                self.assertGreaterEqual(len(match.group(1)), 25)
                self.assertLessEqual(len(match.group(1)), 64)

        content = (S_SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        for relative in ("assets/icon-small.svg", "assets/icon-large.svg"):
            self.assertIn(relative, content)
            self.assertTrue((S_SKILL / relative).is_file())

    def test_skill_mode_boundaries_are_documented(self) -> None:
        standard = (S_SKILL / "SKILL.md").read_text(encoding="utf-8")
        enhanced = (N_SKILL / "SKILL.md").read_text(encoding="utf-8")
        for content in (standard, enhanced):
            self.assertIn("Do not activate from a matching task description", content)
            self.assertIn("If the current message names neither Adaptive-UI-S nor Adaptive-UI-N", content)
        self.assertIn("Adaptive-UI-S never adds a completion audit automatically", standard)
        self.assertIn("User-requested final review after intermittent work", standard)
        self.assertIn("This review is required before claiming the task is complete", enhanced)
        self.assertIn("Do not turn this into a whole-repository audit", enhanced)
        self.assertIn("keep that file in scope", enhanced)
        self.assertIn("task-owned hunk", enhanced)
        self.assertIn("Before editing, confirm that the sibling auditor exists", enhanced)
        self.assertIn("do not claim an N completion", enhanced)

    def test_n_companion_resources_are_available(self) -> None:
        companion = N_SKILL.parent / "adaptive-ui-s"
        self.assertEqual(companion.resolve(), S_SKILL.resolve())
        self.assertTrue((companion / "scripts" / "audit_ui.py").is_file())
        self.assertTrue((companion / "references" / "verification-protocol.md").is_file())

    def test_rule_catalog_matches_implemented_rule_ids(self) -> None:
        script = (SKILL / "scripts" / "audit_ui.py").read_text(encoding="utf-8")
        catalog = (SKILL / "references" / "rule-catalog.md").read_text(encoding="utf-8")
        implemented = set(re.findall(r'"(AUI\d{3})"', script))
        documented = set(re.findall(r"\b(AUI\d{3})\b", catalog))
        expected = {"AUI{0:03d}".format(number) for number in range(1, 24)}
        self.assertEqual(implemented, expected)
        self.assertTrue(expected.issubset(documented))

        tree = ast.parse(script)
        metadata = None
        for node in tree.body:
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "RULE_METADATA"
            ):
                metadata = ast.literal_eval(node.value)
                break
        self.assertIsNotNone(metadata)

        documented_metadata = {}
        row_pattern = re.compile(
            r"^\| (AUI\d{3}) \| [^|]+ \| [^|]+ \| `([^`]+)` \| `([^`]+)` \|"
        )
        for line in catalog.splitlines():
            match = row_pattern.match(line)
            if match:
                documented_metadata[match.group(1)] = {
                    "evidence_level": match.group(2),
                    "default_validation_state": match.group(3),
                }
        self.assertEqual(metadata, documented_metadata)

    def test_tool_and_plugin_versions_match(self) -> None:
        manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        script = (SKILL / "scripts" / "audit_ui.py").read_text(encoding="utf-8")
        match = re.search(r'^TOOL_VERSION = "([^"]+)"$', script, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), manifest["version"])
        self.assertEqual(manifest["version"], "1.0.0")

    def test_runtime_auditor_uses_only_standard_library_modules(self) -> None:
        script_path = SKILL / "scripts" / "audit_ui.py"
        source = script_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".", 1)[0])
        allowed = {
            "__future__",
            "argparse",
            "dataclasses",
            "fnmatch",
            "html",
            "json",
            "os",
            "pathlib",
            "re",
            "stat",
            "sys",
            "tempfile",
            "typing",
            "urllib",
        }
        self.assertEqual(sorted(roots - allowed), [])
        for dangerous in (
            "eval(",
            "exec(",
            "os.system(",
            "shell=True",
            "pickle.loads(",
            "yaml.load(",
            "urllib.request",
        ):
            self.assertNotIn(dangerous, source)

    def test_json_assets_are_valid(self) -> None:
        config_schema = json.loads(
            (SKILL / "assets" / "audit-config.schema.json").read_text(encoding="utf-8")
        )
        report_schema = json.loads(
            (SKILL / "assets" / "audit-report.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(config_schema["type"], "object")
        self.assertEqual(
            config_schema["$id"],
            "https://raw.githubusercontent.com/ksukie/adaptive-ui-engineer/v1.0.0/"
            "plugins/adaptive-ui-engineer/skills/adaptive-ui-s/assets/"
            "audit-config.schema.json",
        )
        self.assertEqual(report_schema["properties"]["schema_version"]["const"], 2)
        finding = report_schema["$defs"]["finding"]
        self.assertTrue(
            {"confidence", "evidence_level", "validation_state"}.issubset(
                finding["required"]
            )
        )
        self.assertEqual(
            set(finding["properties"]["validation_state"]["enum"]),
            {
                "not_applicable",
                "not_run",
                "reproduced",
                "not_reproduced",
                "manual_review_needed",
            },
        )
        evals = json.loads((ROOT / "tests" / "evals" / "trigger-cases.json").read_text(encoding="utf-8"))
        self.assertEqual(evals["schema_version"], 2)
        self.assertEqual(set(evals), {"schema_version", "skills"})
        self.assertEqual(
            {skill["name"] for skill in evals["skills"]},
            {"adaptive-ui-s", "adaptive-ui-n"},
        )
        for skill in evals["skills"]:
            self.assertEqual(set(skill), {"name", "display_name", "positive", "negative"})
            self.assertGreaterEqual(len(skill["positive"]), 4)
            self.assertGreaterEqual(len(skill["negative"]), 5)
            for group in ("positive", "negative"):
                for case in skill[group]:
                    self.assertEqual(set(case), {"prompt", "reason"})
                    self.assertTrue(case["prompt"].strip())
                    self.assertTrue(case["reason"].strip())
        standard = next(skill for skill in evals["skills"] if skill["name"] == "adaptive-ui-s")
        enhanced = next(skill for skill in evals["skills"] if skill["name"] == "adaptive-ui-n")
        self.assertEqual(standard["display_name"], "Adaptive-UI-S")
        self.assertEqual(enhanced["display_name"], "Adaptive-UI-N")
        self.assertTrue(any("cosmetic" in case["reason"] for case in standard["negative"]))
        self.assertTrue(any("mandatory" in case["reason"] for case in enhanced["positive"]))

    def test_readmes_state_current_release_and_portability_boundary(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("### Evidence status for 1.0.0", english)
        self.assertIn("### 1.0.0 证据状态", chinese)
        self.assertNotIn("future CI", english)
        self.assertNotIn("未来 CI", chinese)
        self.assertIn("`adaptive-ui-s` and `adaptive-ui-n` directories together", english)
        self.assertIn("`adaptive-ui-s` 与 `adaptive-ui-n` 保持在同级", chinese)
        self.assertIn("Both Skills declare explicit-only invocation", english)
        self.assertIn("plugin parent; it is a container", english)
        self.assertIn("两个 Skill 都声明为仅显式调用", chinese)
        self.assertIn("插件父级；它只是容器", chinese)

    def test_no_scaffold_placeholders_remain(self) -> None:
        offenders = []
        todo_marker = "[" + "TODO:"
        local_author_marker = "Local" + " developer"
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py", ".css"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if todo_marker in text or local_author_marker in text:
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [])

    def test_workflow_actions_are_pinned_to_full_commit_shas(self) -> None:
        offenders = []
        references = []
        for workflow in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
            text = workflow.read_text(encoding="utf-8")
            for match in re.finditer(r"\buses:\s*[^\s@]+@([^\s#]+)", text):
                reference = match.group(1)
                references.append(reference)
                if re.fullmatch(r"[0-9a-f]{40}", reference) is None:
                    offenders.append("{0}: {1}".format(workflow.name, reference))
        self.assertGreaterEqual(len(references), 6)
        self.assertEqual(offenders, [])

    def test_workflows_keep_untrusted_pull_requests_low_privilege(self) -> None:
        workflows = [
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        ]
        combined = "\n".join(workflows)
        self.assertNotIn("pull_request_target", combined)
        self.assertNotIn("write-all", combined)
        self.assertNotIn("id-token: write", combined)
        self.assertEqual(
            combined.count("uses: actions/checkout@"),
            combined.count("persist-credentials: false"),
        )
        self.assertIn("permissions:\n  contents: read", combined)

    def test_ci_validator_dependencies_are_exact_and_hashed(self) -> None:
        lock = (ROOT / ".github" / "requirements" / "skills-ref.txt").read_text(
            encoding="utf-8"
        )
        packages = re.findall(r"(?m)^([A-Za-z0-9_.-]+)==([^\s\\]+)", lock)
        hashes = re.findall(r"--hash=sha256:([0-9a-f]{64})", lock)
        self.assertEqual(len(packages), 11)
        self.assertEqual(len(hashes), len(packages))
        self.assertNotIn("skills-ref", {name for name, _ in packages})

        runner = (ROOT / ".github" / "scripts" / "run_skills_ref.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("38a2ff82958afee88dadf4831509e6f7e9d8ef4e", runner)
        self.assertIn(
            "e1ad0039bb3b059c1fc2528195214d511d869cf5c84b65c5510f913e52f80648",
            runner,
        )
        self.assertIn("https://codeload.github.com/agentskills/agentskills/zip/", runner)
        self.assertNotIn("git+", runner)

    def test_security_and_release_controls_are_documented(self) -> None:
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        checklist = (ROOT / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
        for phrase in (
            "private security advisory",
            "--redact-evidence",
            "symbolic links and Windows reparse points",
            "not a formal penetration test",
        ):
            self.assertIn(phrase, security)
        for phrase in (
            "Secret scanning",
            "private vulnerability reporting",
            "full commit SHAs",
            "independent audit, or certification",
        ):
            self.assertIn(phrase.lower(), checklist.lower())

    def test_bilingual_disclaimers_preserve_core_boundaries(self) -> None:
        english = (ROOT / "DISCLAIMER.md").read_text(encoding="utf-8")
        chinese = (ROOT / "DISCLAIMER.zh-CN.md").read_text(encoding="utf-8")
        english_boundaries = (
            "not legal advice",
            "No warranty or certification",
            "User responsibility",
            "Source code and report privacy",
            "Third-party names, links, and materials",
            "does not constitute penetration testing",
            "Apache License, Version 2.0 controls",
        )
        chinese_boundaries = (
            "不构成法律意见",
            "不作保证或认证声明",
            "用户责任",
            "源代码与报告隐私",
            "第三方名称、链接与材料",
            "不等同于渗透测试",
            "以 Apache License 2.0 为准",
        )
        for phrase in english_boundaries:
            self.assertIn(phrase, english)
        for phrase in chinese_boundaries:
            self.assertIn(phrase, chinese)
        self.assertIn("DISCLAIMER.zh-CN.md", english)
        self.assertIn("DISCLAIMER.md", chinese)

    def test_svg_assets_have_no_active_content_or_remote_references(self) -> None:
        offenders = []
        for path in ROOT.rglob("*.svg"):
            text = path.read_text(encoding="utf-8").lower()
            if re.search(r"<(?:script|foreignobject)\b|\bon(?:load|error)\s*=", text):
                offenders.append(path.relative_to(ROOT).as_posix())
            if re.search(r"(?:href|src)\s*=\s*['\"](?:https?:)?//", text):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(sorted(set(offenders)), [])

    def test_public_markdown_relative_links_resolve(self) -> None:
        documents = [
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            ROOT / "CONTRIBUTING.md",
            ROOT / "SECURITY.md",
            ROOT / "DISCLAIMER.md",
            ROOT / "DISCLAIMER.zh-CN.md",
            ROOT / "CHANGELOG.md",
            ROOT / "RELEASE_CHECKLIST.md",
        ]
        missing = []
        for document in documents:
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                clean = target.split("#", 1)[0]
                if not clean or re.match(r"^[a-z][a-z0-9+.-]*:", clean, flags=re.IGNORECASE):
                    continue
                resolved = (document.parent / clean).resolve()
                if not resolved.exists():
                    missing.append("{0} -> {1}".format(document.name, target))
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
