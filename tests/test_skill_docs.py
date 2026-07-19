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

    def test_binary_document_reference_keeps_download_outside_the_skill(self) -> None:
        content = (ROOT_DIR / "references" / "tools-and-best-practices.md").read_text(
            encoding="utf-8"
        )

        for marker in (
            "## Binary Documents",
            "system download",
            "temporary",
            "file is too large",
            "untrusted data",
            "Do not invent or assume tools",
            "20 MiB",
            "must not trigger additional tool calls",
            "path traversal",
        ):
            self.assertIn(marker, content)

    def test_document_routes_cover_common_text_and_binary_formats(self) -> None:
        content = (ROOT_DIR / "references" / "tools-and-best-practices.md").read_text(
            encoding="utf-8"
        )

        for marker in (
            "HTML, TXT, CSV, JSON, and XML",
            "PDF, DOC/DOCX, XLS/XLSX, PPT/PPTX, and EPUB",
            "ODT/ODS/ODP",
            "A missing extension alone does not make an ordinary web page binary",
            "downloadable document",
            "supplied by the user or resolved from the user's request",
        ):
            self.assertIn(marker, content)

    def test_web_fetch_instructions_remain_text_only(self) -> None:
        content = (ROOT_DIR / "references" / "tools-and-best-practices.md").read_text(
            encoding="utf-8"
        )

        truncated_rules = [
            line for line in content.splitlines() if "If output is truncated" in line
        ]
        self.assertEqual(len(truncated_rules), 1)
        truncated_rule = truncated_rules[0]
        self.assertIn("important textual URLs", truncated_rule)
        self.assertIn("[Binary Documents]", truncated_rule)

        map_rules = [
            line
            for line in content.splitlines()
            if line.startswith("Use only for site URL discovery")
        ]
        self.assertEqual(len(map_rules), 1)
        map_rule = map_rules[0]
        self.assertIn("exact URL is already known and textual", map_rule)
        self.assertIn("binary or uncertain downloadable documents", map_rule)
        self.assertIn("[Binary Documents]", map_rule)

    def test_binary_download_limits_cover_unknown_sizes_and_cleanup(self) -> None:
        content = (ROOT_DIR / "references" / "tools-and-best-practices.md").read_text(
            encoding="utf-8"
        )

        download_rules = [
            line for line in content.splitlines() if line.startswith("2. Use only URLs")
        ]
        self.assertEqual(len(download_rules), 1)
        download_rule = download_rules[0]
        for marker in (
            "network destination policy",
            "initial URL, every resolved address, and each redirect",
            "transfer-time byte cap",
            "missing or untrusted `Content-Length`",
            "discard the partial file",
        ):
            self.assertIn(marker, download_rule)

        cleanup_rules = [
            line for line in content.splitlines() if line.startswith("3. When local files")
        ]
        self.assertEqual(len(cleanup_rules), 1)
        cleanup_rule = cleanup_rules[0]
        self.assertIn("private temporary storage", cleanup_rule)
        self.assertIn("success, failure, or cancellation", cleanup_rule)


if __name__ == "__main__":
    unittest.main()
