from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "poland",
    "poland-appeals-review",
    "poland-benefits-support",
    "poland-business",
    "poland-case-planning",
    "poland-citizenship-long-term",
    "poland-civic-participation",
    "poland-civil-life-events",
    "poland-consular-travel",
    "poland-consumer-banking",
    "poland-digital-government",
    "poland-disability-accessibility",
    "poland-emergency-rights",
    "poland-employment-rights",
    "poland-employment-services",
    "poland-eu-mobility",
    "poland-family-education",
    "poland-foreign-documents",
    "poland-healthcare",
    "poland-housing",
    "poland-identity",
    "poland-justice-legal-aid",
    "poland-local-services",
    "poland-pensions-seniors",
    "poland-protection-referral",
    "poland-social-insurance",
    "poland-source-verification",
    "poland-stay-residence",
    "poland-tax",
    "poland-transport-driving",
    "poland-utilities-environment",
    "poland-vehicles-road",
    "poland-work-authorization",
}
RETIRED_SKILLS = {
    "poland-automation",
    "poland-documents-language",
    "poland-immigration",
    "poland-tax-social-insurance",
    "poland-work",
}


class ContractTests(unittest.TestCase):
    def test_manifest_parity_and_mcp_binding(self):
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        for key in ("name", "version", "description", "author", "license", "keywords"):
            self.assertEqual(codex[key], claude[key])
        self.assertEqual("poland", codex["name"])
        self.assertEqual("0.2.0", codex["version"])
        self.assertEqual("./.codex-mcp.json", codex["mcpServers"])
        self.assertLessEqual(len(codex["description"]), 240)
        self.assertEqual("https://github.com/Xopoko/plug-n-skills", codex["interface"]["websiteURL"])

    def test_dual_mcp_configs_are_host_neutral_and_overrideable(self):
        codex = json.loads((ROOT / ".codex-mcp.json").read_text(encoding="utf-8"))["mcpServers"]["poland"]
        claude = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["poland"]
        self.assertEqual("python3", codex["command"])
        self.assertEqual(["-I", "-B", "./mcp/server.py"], codex["args"])
        self.assertEqual("${POLAND_PYTHON:-python3}", claude["command"])
        self.assertEqual(["-I", "-B", "${CLAUDE_PLUGIN_ROOT}/mcp/server.py"], claude["args"])
        self.assertNotIn("C:\\", json.dumps((codex, claude)))

    def test_cursor_explicitly_declares_skills_and_mcp_components(self):
        cursor = json.loads((ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual("./skills/", cursor["skills"])
        self.assertEqual("./.codex-mcp.json", cursor["mcpServers"])
        self.assertEqual("https://github.com/Xopoko/poland", cursor["homepage"])

    def test_pi_package_preserves_complete_shared_runtime(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        packaged_files = set(package["files"])
        self.assertTrue(
            {
                ".claude-plugin",
                ".codex-mcp.json",
                ".codex-plugin",
                ".cursor-plugin",
                ".mcp.json",
                "agents",
                "assets",
                "data",
                "docs",
                "lib/*.py",
                "mcp/*.py",
                "references",
                "schemas",
                "scripts/*.py",
                "skills",
            }.issubset(packaged_files)
        )
        self.assertTrue({"lib", "mcp", "scripts"}.isdisjoint(packaged_files))

    def test_skill_inventory_and_frontmatter(self):
        skill_files = list((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in skill_files})
        for path in skill_files:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            name = re.search(r"^name: (.+)$", text, re.MULTILINE)
            description = re.search(r"^description: (.+)$", text, re.MULTILINE)
            self.assertEqual(path.parent.name, name.group(1) if name else None)
            self.assertIsNotNone(description, path)
            self.assertLessEqual(len(description.group(1)), 240, path)
            self.assertNotIn("TODO", text)

    def test_router_names_every_focused_skill(self):
        router = (ROOT / "skills" / "poland" / "SKILL.md").read_text(encoding="utf-8")
        for name in EXPECTED_SKILLS - {"poland"}:
            self.assertIn(name, router)

    def test_retired_broad_skills_are_absent_from_routes(self):
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            for name in RETIRED_SKILLS:
                self.assertNotIn(f"`{name}`", text, path)
        router = (ROOT / "skills" / "poland" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/automation-playbook.md", router)

    def test_cross_skill_routes_resolve(self):
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"`(poland-[a-z0-9-]+)`", text):
                self.assertIn(target, EXPECTED_SKILLS, (path, target))

    def test_trigger_fixture_covers_positive_and_near_miss(self):
        fixture = json.loads((ROOT / "tests" / "fixtures" / "trigger-cases.json").read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED_SKILLS, set(fixture["skills"]))
        for cases in fixture["skills"].values():
            self.assertTrue(cases["should_trigger"])
            self.assertTrue(cases["should_not_trigger"])

    def test_references_are_routed_from_skills(self):
        all_skill_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "skills").glob("*/SKILL.md"))
        for reference in (ROOT / "references").glob("*.md"):
            if reference.name == "test-scenarios.md":
                continue
            self.assertIn(reference.name, all_skill_text, reference.name)

    def test_public_source_contains_no_frozen_fee_or_processing_table(self):
        tracked_text = "\n".join(
            path.read_text(encoding="utf-8")
            for directory in ("data", "skills", "references")
            for path in (ROOT / directory).rglob("*")
            if path.is_file() and path.suffix in {".json", ".md"}
        )
        self.assertNotRegex(tracked_text, r"(?i)guaranteed (approval|outcome|permit)")
        self.assertNotRegex(tracked_text, r"(?i)processing time is \d+")

    def test_hot_path_uses_operator_contract_without_persistent_cases(self):
        hot_paths = [
            path
            for path in (ROOT / "skills").glob("*/SKILL.md")
            if path.parent.name != "poland"
        ] + [
            path
            for path in (ROOT / "references").glob("*.md")
            if path.name not in {
                "architecture-decisions.md",
                "automation-playbook.md",
                "browser-safety.md",
            }
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in hot_paths)
        stale_claims = (
            "case init ./case.json",
            "case-profile.schema.json",
            "without user review",
            "prohibited even with user consent",
            "consent does not expand this boundary",
            "provide the exact official landing page and stop",
        )
        for claim in stale_claims:
            self.assertNotIn(claim, text)

        operating_contract = (ROOT / "references" / "operating-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not create or update case profiles, ledgers, or files.", operating_contract)
        self.assertIn("explicit task-scoped authorization", operating_contract)
        self.assertIn("fresh visible summary", operating_contract)
        self.assertIn("visible official receipt", operating_contract)
        digital = (ROOT / "skills" / "poland-digital-government" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("bundles no executable Browser or Computer adapter", digital)
        self.assertIn("Manual fallback", digital)


if __name__ == "__main__":
    unittest.main()
