from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackageSurfaceTests(unittest.TestCase):
    def test_standalone_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_package.py")],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"])

    def test_public_onboarding_is_agent_first_and_opt_in(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertLess(readme.index("Ask Your Agent"), readme.index("Optional Technical Tools"))
        self.assertIn("not installed by default", readme)
        self.assertIn("Do not paste names", readme)

    def test_public_issue_templates_reject_personal_data(self):
        templates = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml")
        )
        self.assertIn("personal data", templates)
        self.assertIn("credentials", templates)

    def test_release_version_parity(self):
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        cursor = json.loads((ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        versions = {codex["version"], claude["version"], cursor["version"], marketplace["version"], marketplace["plugins"][0]["version"], package["version"]}
        self.assertEqual({"0.1.0"}, versions)


if __name__ == "__main__":
    unittest.main()
