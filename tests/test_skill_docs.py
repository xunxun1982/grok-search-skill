from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

ABSOLUTE_INSTALL_PATHS = (
    re.compile(r"[A-Za-z]:[\\/][^\n`]*skills", re.IGNORECASE),
    re.compile(r"~[\\/]\.(?:agents|cc-switch|codex)", re.IGNORECASE),
)


class SkillDocumentationTests(unittest.TestCase):
    def test_skill_entrypoint_requires_skill_root_workdir_without_absolute_paths(self) -> None:
        content = (ROOT_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("skill directory root", content)
        self.assertIn("containing this `SKILL.md`", content)
        self.assertIn("shell working directory", content)
        self.assertIn("python scripts/websearch.py <command> [options]", content)

        for pattern in ABSOLUTE_INSTALL_PATHS:
            self.assertIsNone(pattern.search(content))

    def test_reference_commands_inherit_skill_root_workdir_rule(self) -> None:
        content = (ROOT_DIR / "references" / "tools-and-best-practices.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Run these commands from the skill directory root", content)
        self.assertIn("not the user's project directory", content)
        self.assertIn("python scripts/websearch.py web_search", content)

        for pattern in ABSOLUTE_INSTALL_PATHS:
            self.assertIsNone(pattern.search(content))


if __name__ == "__main__":
    unittest.main()
