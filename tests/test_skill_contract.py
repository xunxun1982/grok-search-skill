from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT_DIR / "SKILL.md"


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(?P<frontmatter>.*?)\n---\n(?P<body>.*)\Z", cls.skill, re.S)
        if match is None:
            raise AssertionError("SKILL.md must contain YAML frontmatter")
        cls.frontmatter = match.group("frontmatter")
        cls.body = match.group("body")

    def frontmatter_value(self, key: str) -> str:
        match = re.search(rf"^{re.escape(key)}:\s*(.+)$", self.frontmatter, re.M)
        self.assertIsNotNone(match, f"missing frontmatter field: {key}")
        return match.group(1).strip().strip('"')

    def test_description_is_compact_and_covers_real_branches(self) -> None:
        self.assertEqual(self.frontmatter_value("name"), "web-search-skill")
        self.assertRegex(
            self.frontmatter,
            re.compile(r'^description:\s*"[^"\n]+"$', re.M),
            "description must be valid quoted YAML",
        )
        description = self.frontmatter_value("description")
        self.assertTrue(description.startswith("Use when"))
        self.assertLess(description.index("live web evidence"), 40)
        self.assertLess(len(description), 500)
        for marker in (
            "current web discovery",
            "known URL",
            "online document",
            "prior web_search sources",
            "site URL",
            "configuration or connectivity",
        ):
            self.assertIn(marker, description)

    def test_body_is_compact_and_routes_every_stable_command(self) -> None:
        word_count = len(re.findall(r"[A-Za-z0-9_'-]+", self.body))
        self.assertLess(word_count, 500)

        routing = self.body.split("## Command Routing\n", 1)[1].split("\n## ", 1)[0]
        routes = []
        for line in routing.splitlines():
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) != 3:
                continue
            command = re.fullmatch(r"`([^`]+)`", cells[1])
            if command:
                routes.append((command.group(1), cells[2]))

        expected = ("web_search", "web_fetch", "get_sources", "web_map", "doctor")
        self.assertCountEqual((command for command, _ in routes), expected)
        self.assertTrue(all(gate for _, gate in routes))
        search_gate = dict(routes)["web_search"]
        self.assertIn("named document", search_gate)
        self.assertIn("web_fetch", search_gate)
        doctor_gate = dict(routes)["doctor"]
        self.assertIn("live command", doctor_gate)

    def test_execution_path_is_portable_and_references_are_valid(self) -> None:
        self.assertIn("skill directory root", self.body.lower())
        self.assertIn("directory containing this `SKILL.md`", self.body)
        self.assertIsNone(re.search(r"[A-Za-z]:\\|/Users/|/home/", self.skill))
        for relative_path in (
            "references/tools-and-best-practices.md",
            "references/configuration.md",
        ):
            self.assertIn(f"`{relative_path}`", self.body)
            self.assertTrue((ROOT_DIR / relative_path).is_file())

    def test_security_boundaries_remain_explicit(self) -> None:
        for marker in (
            "URL discovery and textual branches through the bundled CLI",
            "Binary-document download and parsing",
            "python scripts/websearch.py <command> [options]",
            "untrusted evidence",
            "Follow the user's task and governing instructions",
            "API keys",
            "tokens",
            "`.env` contents",
            "private data",
            "redacted",
            "Run `doctor` first",
            "internal fetch behavior",
            "`references/configuration.md`",
        ):
            self.assertIn(marker, self.body)

    def test_binary_documents_route_to_host_tools(self) -> None:
        for marker in (
            "## Binary Documents",
            "Do not use `web_fetch`",
            "Read `references/tools-and-best-practices.md` before selecting tools",
            "host-provided built-in or system download/read toolchains",
            "use them autonomously only when the referenced controls are enforceable",
            "Do not install dependencies",
            "ask the user to download and upload the relevant portion",
        ):
            self.assertIn(marker, self.body)

        binary_rules = self.body.split("## Binary Documents\n", 1)[1].split("\n## ", 1)[0]
        self.assertLess(
            binary_rules.index("Read `references/tools-and-best-practices.md`"),
            binary_rules.index("Prefer host-provided"),
        )

    def test_implicit_invocation_remains_enabled(self) -> None:
        metadata = (ROOT_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: true", metadata)


if __name__ == "__main__":
    unittest.main()
