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
        self.assertLess(readme.index("Ask Your Agent"), readme.index("Technical Details"))
        self.assertIn("not installed by default", readme)
        self.assertIn("Do not paste names", readme)

    def test_public_install_examples_pin_the_published_release(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        install = (ROOT / "docs" / "INSTALL.md").read_text(encoding="utf-8")
        combined = readme + "\n" + install
        self.assertIn("Xopoko/poland --ref v0.2.0", combined)
        self.assertIn("Xopoko/poland@v0.2.0", combined)
        self.assertIn("--branch v0.2.0 --depth 1", combined)
        self.assertIn("git:github.com/Xopoko/poland@v0.2.0", combined)
        self.assertNotIn("marketplace add Xopoko/poland\n", combined)
        self.assertNotIn("git clone https://github.com/Xopoko/poland.git", combined)

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
        self.assertEqual({"0.2.0"}, versions)

    def test_codex_marketplace_is_explicitly_opt_in(self):
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("poland", marketplace["name"])
        self.assertEqual(1, len(marketplace["plugins"]))
        entry = marketplace["plugins"][0]
        self.assertEqual("poland", entry["name"])
        self.assertEqual({"source": "local", "path": "."}, entry["source"])
        self.assertEqual("AVAILABLE", entry["policy"]["installation"])
        self.assertNotEqual("INSTALLED_BY_DEFAULT", entry["policy"]["installation"])


if __name__ == "__main__":
    unittest.main()
