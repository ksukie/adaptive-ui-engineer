from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "adaptiveui-skill"
S_SKILL = PLUGIN / "skills" / "adaptiveui-s"
N_SKILL = PLUGIN / "skills" / "adaptiveui-n"
MODE_SELECTION_GUIDE = S_SKILL / "references" / "mode-selection.md"
VERIFICATION_PROTOCOL = S_SKILL / "references" / "verification-protocol.md"
RELEASE_METADATA = S_SKILL / "release.json"
UPDATE_CHECKER = S_SKILL / "scripts" / "check_update.py"
PLUGIN_HOOKS = PLUGIN / "hooks" / "hooks.json"
SKILL = S_SKILL
SKILLS = {
    "adaptiveui-s": S_SKILL,
    "adaptiveui-n": N_SKILL,
}


class PackageContractTests(unittest.TestCase):
    def test_required_public_files_exist(self) -> None:
        paths = [
            ROOT / "README.md",
            ROOT / "README.en.md",
            ROOT / "docs" / "images" / "adaptiveui-skill-workflow.png",
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
            MODE_SELECTION_GUIDE,
            RELEASE_METADATA,
            UPDATE_CHECKER,
            PLUGIN_HOOKS,
        ]
        self.assertEqual([str(path) for path in paths if not path.is_file()], [])

    def test_plugin_manifest_contract(self) -> None:
        manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "adaptiveui-skill")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(manifest["license"], "Apache-2.0")
        self.assertEqual(manifest["author"]["name"], "ksukie")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertNotIn("hooks", manifest)
        interface = manifest["interface"]
        self.assertEqual(interface["displayName"], "AdaptiveUI-SKILL")
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        self.assertTrue(all(len(item) <= 128 for item in interface["defaultPrompt"]))
        for field in ("composerIcon", "logo"):
            path = PLUGIN / interface[field].removeprefix("./")
            self.assertTrue(path.is_file(), str(path))

    def test_marketplace_points_to_plugin(self) -> None:
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["name"], "adaptiveui-skill")
        self.assertEqual(marketplace["interface"]["displayName"], "AdaptiveUI-SKILL")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "adaptiveui-skill")
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
            "adaptiveui-s": (S_SKILL, "AdaptiveUI-S", "$adaptiveui-s"),
            "adaptiveui-n": (N_SKILL, "AdaptiveUI-N", "$adaptiveui-n"),
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
            self.assertIn("If the current message names neither AdaptiveUI-S nor AdaptiveUI-N", content)
        self.assertIn("AdaptiveUI-S never adds a completion audit automatically", standard)
        self.assertIn("User-requested final review after intermittent work", standard)
        self.assertIn("This review is required before claiming the task is complete", enhanced)
        self.assertIn("Do not turn this into a whole-repository audit", enhanced)
        self.assertIn("keep that file in scope", enhanced)
        self.assertIn("task-owned hunk", enhanced)
        self.assertIn("Before editing, confirm that the sibling auditor exists", enhanced)
        self.assertIn("do not claim an N completion", enhanced)
        self.assertIn("AdaptiveUI-S owns an explicitly read-only request", standard)
        self.assertIn("use AdaptiveUI-S for an explicitly read-only request", enhanced)
        self.assertIn("If the current message invokes only N but explicitly forbids edits", enhanced)
        self.assertIn("do not silently activate S", enhanced)

    def test_skills_gate_each_explicit_request_by_actual_ui_relevance(self) -> None:
        standard = (S_SKILL / "SKILL.md").read_text(encoding="utf-8")
        enhanced = (N_SKILL / "SKILL.md").read_text(encoding="utf-8")
        for content in (standard, enhanced):
            self.assertIn("even when the prompt never mentions UI", content)
            self.assertIn("Treat every valid explicit invocation as activation of the UI workflow", content)
            self.assertIn("## UI-relevance gate", content)
            self.assertIn("Do not require the user to mention UI", content)
            self.assertIn(
                "Classify each prompt fact by its actual in-scope adaptive UI effect, not by its wording",
                content,
            )
            self.assertIn("Direct adaptive UI constraints", content)
            self.assertIn("Indirect adaptive UI constraints", content)
            self.assertIn("Outside-scope facts", content)
            self.assertIn("standalone copywriting or typo fixes", content)
            self.assertIn("cosmetic-only changes", content)
            self.assertIn("Do not invent a hypothetical UI dependency", content)
            self.assertIn("Do not default to a whole-repository scan", content)
            self.assertIn("Naming a page or component alone is not enough", content)
            self.assertIn(
                "Of the prompt facts, let only direct and indirect adaptive UI constraints",
                content,
            )
            self.assertIn("inspected project evidence and applicable local instructions", content)
            self.assertIn("Use this gate to partition the AdaptiveUI portion", content)
            self.assertIn("A clear request in the same message can separately authorize broader work", content)
            self.assertIn("a background fact or the Skill invocation alone cannot", content)
            self.assertIn("inspect the project entry-point or route map", content)
            self.assertIn(
                "If that bounded inspection finds no in-scope adaptive UI effect",
                content,
            )
            self.assertIn("rendered character encoding", content)
        self.assertIn("named or derived AdaptiveUI scope", standard)
        self.assertIn("post-change style audit not applicable", enhanced)
        self.assertIn("every task-owned change made after the baseline", enhanced)
        self.assertIn("Exclude task-owned backend, database, deployment", enhanced)

        s_metadata = (S_SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        n_metadata = (N_SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("adaptive-UI effects, even if I do not mention UI", s_metadata)
        self.assertIn("Implement only its adaptive-UI effects", n_metadata)

    def test_skills_keep_repository_publication_explicit_and_silent(self) -> None:
        for skill in (S_SKILL, N_SKILL):
            with self.subTest(skill=skill.name):
                content = (skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("## Repository-publication boundary", content)
                self.assertIn(
                    "Do not stage, commit, push, tag, open or update a pull request, or create a GitHub release",
                    content,
                )
                self.assertIn("A request to commit authorizes only the requested commit", content)
                self.assertIn("Do not proactively mention this default in the completion report.", content)

    def test_n_companion_resources_are_available(self) -> None:
        companion = N_SKILL.parent / "adaptiveui-s"
        self.assertEqual(companion.resolve(), S_SKILL.resolve())
        self.assertTrue((companion / "scripts" / "audit_ui.py").is_file())
        self.assertTrue((companion / "references" / "verification-protocol.md").is_file())
        self.assertTrue((companion / "references" / "mode-selection.md").is_file())
        self.assertTrue((companion / "scripts" / "check_update.py").is_file())
        self.assertTrue((companion / "release.json").is_file())

    def test_shared_mode_selection_guide_preserves_the_two_skill_boundary(self) -> None:
        guide = MODE_SELECTION_GUIDE.read_text(encoding="utf-8")
        standard = (S_SKILL / "SKILL.md").read_text(encoding="utf-8")
        enhanced = (N_SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`AdaptiveUI-S`", guide)
        self.assertIn("`AdaptiveUI-N`", guide)
        self.assertIn("does not activate either workflow", guide)
        self.assertIn("$adaptiveui-s", guide)
        self.assertIn("$adaptiveui-n", guide)
        self.assertIn("Standalone copywriting, typo-only edits, and cosmetic-only changes", guide)
        self.assertIn("If only N is invoked for an explicitly read-only request", guide)
        self.assertIn("S owns an explicitly read-only request", guide)
        self.assertIn("N owns an implementation request", guide)
        self.assertIn("[mode-selection.md](references/mode-selection.md)", standard)
        self.assertIn("choosing S or N and invocation examples", standard)
        self.assertIn("<s-skill-root>/references/mode-selection.md", enhanced)
        discovered = sorted(
            path.name for path in (PLUGIN / "skills").iterdir() if (path / "SKILL.md").is_file()
        )
        self.assertEqual(discovered, ["adaptiveui-n", "adaptiveui-s"])

    def test_preview_encoding_verification_is_layered_and_bounded(self) -> None:
        protocol = VERIFICATION_PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("## 3. Verify preview character encoding", protocol)
        self.assertIn("source bytes, HTML declarations, HTTP metadata", protocol)
        self.assertIn('<meta charset="utf-8">', protocol)
        self.assertIn("first 1024 bytes", protocol)
        self.assertIn("Content-Type: text/html; charset=utf-8", protocol)
        self.assertIn("document.characterSet", protocol)
        self.assertIn("file://", protocol)
        self.assertIn("AUI024", protocol)
        self.assertIn("do not silently migrate an established non-UTF-8 file", protocol)

    def test_rule_catalog_matches_implemented_rule_ids(self) -> None:
        script = (SKILL / "scripts" / "audit_ui.py").read_text(encoding="utf-8")
        catalog = (SKILL / "references" / "rule-catalog.md").read_text(encoding="utf-8")
        implemented = set(re.findall(r'"(AUI\d{3})"', script))
        documented = set(re.findall(r"\b(AUI\d{3})\b", catalog))
        expected = {"AUI{0:03d}".format(number) for number in range(1, 25)}
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
        checker = UPDATE_CHECKER.read_text(encoding="utf-8")
        release = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
        match = re.search(r'^TOOL_VERSION = "([^"]+)"$', script, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), manifest["version"])
        self.assertEqual(release["version"], manifest["version"])
        self.assertIn(
            '"User-Agent": "adaptiveui-skill-update-check/{0}"'.format(
                manifest["version"]
            ),
            checker,
        )
        self.assertEqual(manifest["version"], "2.0.0")

    def test_update_release_metadata_contract(self) -> None:
        release = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
        self.assertEqual(
            set(release), {"version", "released_at", "release_sequence", "summary"}
        )
        self.assertRegex(release["version"], r"^\d+\.\d+\.\d+$")
        self.assertRegex(release["released_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(release["release_sequence"], 9)
        self.assertEqual(set(release["summary"]), {"zh-CN", "en"})
        for summary in release["summary"].values():
            self.assertTrue(summary.strip())
            self.assertLessEqual(len(summary), 240)
            self.assertNotRegex(summary, r"[\r\n]")

    def test_plugin_hook_runs_only_the_shared_update_checker(self) -> None:
        hooks = json.loads(PLUGIN_HOOKS.read_text(encoding="utf-8"))
        self.assertEqual(set(hooks), {"hooks"})
        self.assertEqual(set(hooks["hooks"]), {"UserPromptSubmit"})
        entry = hooks["hooks"]["UserPromptSubmit"][0]
        self.assertNotIn("matcher", entry)
        handler = entry["hooks"][0]
        self.assertEqual(handler["type"], "command")
        self.assertIn("$PLUGIN_ROOT/skills/adaptiveui-s/scripts/check_update.py", handler["command"])
        self.assertIn("$env:PLUGIN_ROOT", handler["commandWindows"])
        self.assertIn("--hook", handler["command"])
        self.assertIn("--hook", handler["commandWindows"])
        self.assertLessEqual(handler["timeout"], 6)

    def test_skills_document_the_shared_update_notice_protocol(self) -> None:
        standard = (S_SKILL / "SKILL.md").read_text(encoding="utf-8")
        enhanced = (N_SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Update-notice protocol", standard)
        self.assertIn("<skill-root>/scripts/check_update.py", standard)
        self.assertIn("## Update-notice protocol", enhanced)
        self.assertIn("<s-skill-root>/scripts/check_update.py", enhanced)
        for content in (standard, enhanced):
            self.assertIn("36 hours", content)
            self.assertIn("20%", content)
            self.assertIn("12-hour floor", content)
            self.assertIn("no automatic update occurred", content)

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

    def test_update_scheduler_uses_only_approved_standard_library_modules(self) -> None:
        source = UPDATE_CHECKER.read_text(encoding="utf-8")
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
            "datetime",
            "json",
            "os",
            "pathlib",
            "re",
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
            "subprocess.",
            "socket.",
            "pickle.",
            "yaml.",
            "requests.",
        ):
            self.assertNotIn(dangerous, source)
        self.assertIn(
            '"https://raw.githubusercontent.com/ksukie/AdaptiveUI-SKILL/main/"',
            source,
        )

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
            "https://raw.githubusercontent.com/ksukie/AdaptiveUI-SKILL/v2.0.0/"
            "plugins/adaptiveui-skill/skills/adaptiveui-s/assets/"
            "audit-config.schema.json",
        )
        self.assertEqual(report_schema["properties"]["schema_version"]["const"], 3)
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
        self.assertEqual(evals["schema_version"], 3)
        self.assertEqual(set(evals), {"schema_version", "skills"})
        self.assertEqual(
            {skill["name"] for skill in evals["skills"]},
            {"adaptiveui-s", "adaptiveui-n"},
        )
        for skill in evals["skills"]:
            self.assertEqual(
                set(skill), {"name", "display_name", "positive", "negative", "behavior"}
            )
            self.assertGreaterEqual(len(skill["positive"]), 4)
            self.assertGreaterEqual(len(skill["negative"]), 5)
            for group in ("positive", "negative"):
                for case in skill[group]:
                    self.assertEqual(set(case), {"prompt", "reason"})
                    self.assertTrue(case["prompt"].strip())
                    self.assertTrue(case["reason"].strip())
            self.assertGreaterEqual(len(skill["behavior"]), 6)
            for case in skill["behavior"]:
                self.assertEqual(set(case), {"prompt", "expected", "reason"})
                self.assertTrue(case["prompt"].strip())
                self.assertTrue(case["expected"].strip())
                self.assertTrue(case["reason"].strip())
        standard = next(skill for skill in evals["skills"] if skill["name"] == "adaptiveui-s")
        enhanced = next(skill for skill in evals["skills"] if skill["name"] == "adaptiveui-n")
        self.assertEqual(standard["display_name"], "AdaptiveUI-S")
        self.assertEqual(enhanced["display_name"], "AdaptiveUI-N")
        self.assertTrue(any("cosmetic" in case["reason"] for case in standard["negative"]))
        self.assertTrue(any("mandatory" in case["reason"] for case in enhanced["positive"]))
        for skill in (standard, enhanced):
            invocation = "${0}".format(skill["name"])
            self.assertTrue(all(invocation in case["prompt"] for case in skill["positive"]))
            self.assertTrue(all(invocation not in case["prompt"] for case in skill["negative"]))
            self.assertTrue(
                any("without UI terminology" in case["reason"] for case in skill["positive"])
            )
            self.assertTrue(
                any(
                    "PostgreSQL" in case["prompt"] and "Kubernetes" in case["prompt"]
                    for case in skill["positive"]
                )
            )
            self.assertTrue(
                any(
                    "optimize this PostgreSQL query" in case["prompt"]
                    and "no in-scope adaptive UI effect" in case["reason"]
                    for case in skill["positive"]
                )
            )
            behavior = skill["behavior"]
            self.assertTrue(
                any(
                    "blue to green and fix a typo" in case["prompt"]
                    and "no in-scope adaptive UI effect" in case["expected"]
                    and "outside this workflow" in case["expected"]
                    for case in behavior
                )
            )
            self.assertTrue(
                any(
                    "Use both $adaptiveui-s and $adaptiveui-n" in case["prompt"]
                    and "read-only" in case["expected"]
                    for case in behavior
                )
            )
            self.assertTrue(
                any(
                    "garbled" in case["prompt"]
                    and "document.characterSet" in case["expected"]
                    for case in behavior
                )
            )
        self.assertTrue(
            any(
                "Do not inspect or edit" in case["expected"]
                and "current-message S invocation" in case["expected"]
                for case in enhanced["behavior"]
            )
        )
        self.assertTrue(
            any(
                "every task-owned hunk" in case["expected"]
                and "exclude API-only" in case["expected"]
                for case in enhanced["behavior"]
            )
        )

    def test_readmes_state_current_release_and_portability_boundary(self) -> None:
        english = (ROOT / "README.en.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertFalse((ROOT / "README.zh-CN.md").exists())
        self.assertIn("[English](README.en.md)", chinese)
        self.assertIn("[简体中文](README.md)", english)
        self.assertIn("docs/images/adaptiveui-skill-workflow.png", chinese)
        self.assertIn("docs/images/adaptiveui-skill-workflow.png", english)
        self.assertIn("### Evidence status for 2.0.0", english)
        self.assertIn("### 2.0.0 证据状态", chinese)
        self.assertIn("mode-selection guide", english)
        self.assertIn("模式选择说明", chinese)
        self.assertNotIn("future CI", english)
        self.assertNotIn("未来 CI", chinese)
        self.assertIn("`adaptiveui-s` and `adaptiveui-n` directories together", english)
        self.assertIn("`adaptiveui-s` 与 `adaptiveui-n` 保持在同级", chinese)
        self.assertIn("Both Skills declare explicit-only invocation", english)
        self.assertIn("plugin parent; it is a container", english)
        self.assertIn("两个 Skill 都声明为仅显式调用", chinese)
        self.assertIn("插件父级；它只是容器", chinese)
        self.assertIn("UI-relevance gating", english)
        self.assertIn("even when the remaining prompt does not mention UI", english)
        self.assertIn("a clear broader request in the same message", english)
        self.assertIn("Skill invocation alone cannot authorize it", english)
        self.assertIn("Browser-preview encoding verification", english)
        self.assertIn("AUI024", english)
        self.assertIn("document.characterSet", english)
        self.assertIn("UI 相关性门控", chinese)
        self.assertIn("不要求其余提示词出现“UI”", chinese)
        self.assertIn("背景信息或 Skill 调用本身不构成授权", chinese)
        self.assertIn("网页预览编码验证", chinese)
        self.assertIn("AUI024", chinese)
        self.assertIn("只读请求由 S 负责，实施请求由 N 负责", chinese)
        self.assertIn("### Optional update notices", english)
        self.assertIn("### 可选更新提醒", chinese)
        self.assertIn("ADAPTIVE_UI_UPDATE_CHECK=0", english)
        self.assertIn("ADAPTIVE_UI_UPDATE_CHECK=0", chinese)

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
            "Update scheduler security boundaries",
            "display-only data",
            "not a formal penetration test",
        ):
            self.assertIn(phrase, security)
        for phrase in (
            "Secret scanning",
            "private vulnerability reporting",
            "full commit SHAs",
            "release_sequence",
            "20%",
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
            ROOT / "README.en.md",
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
