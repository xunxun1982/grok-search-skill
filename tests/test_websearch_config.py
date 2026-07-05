from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import websearch  # noqa: E402


class ConfigBomTests(unittest.TestCase):
    def test_normalize_utf8_bom_config_rewrites_file_on_current_platform(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            normalized = b'GROK_SEARCH_MODEL = "model"\n'
            config_path.write_bytes(websearch.UTF8_BOM + normalized)

            self.assertEqual(
                websearch.normalize_utf8_bom_config(config_path, config_path.read_bytes()),
                normalized,
            )

            self.assertEqual(config_path.read_bytes(), normalized)

    def test_normalize_utf8_bom_config_preserves_inode_and_mode(self) -> None:
        if os.name == "nt":
            self.skipTest("POSIX inode and mode behavior")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            normalized = b'GROK_SEARCH_MODEL = "model"\n'
            config_path.write_bytes(websearch.UTF8_BOM + normalized)
            os.chmod(config_path, 0o600)
            before = config_path.stat()

            websearch.normalize_utf8_bom_config(config_path, config_path.read_bytes())

            after = config_path.stat()
            self.assertEqual(after.st_ino, before.st_ino)
            self.assertEqual(after.st_uid, before.st_uid)
            self.assertEqual(after.st_gid, before.st_gid)
            self.assertEqual(after.st_mode & 0o777, 0o600)
            self.assertEqual(config_path.read_bytes(), normalized)

    def test_normalize_utf8_bom_config_does_not_create_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            normalized = b'GROK_SEARCH_MODEL = "model"\n'
            config_path.write_bytes(websearch.UTF8_BOM + normalized)

            websearch.normalize_utf8_bom_config(config_path, config_path.read_bytes())

            self.assertEqual(list(Path(temp_dir).glob("*.tmp")), [])
            self.assertEqual(list(Path(temp_dir).glob(".*.tmp")), [])

    def test_normalize_utf8_bom_config_failure_raises_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            normalized = b'GROK_SEARCH_MODEL = "model"\n'
            config_path.write_bytes(websearch.UTF8_BOM + normalized)
            raw = config_path.read_bytes()

            with (
                mock.patch.object(Path, "open", side_effect=PermissionError("denied")),
                self.assertRaises(websearch.ConfigError),
            ):
                websearch.normalize_utf8_bom_config(config_path, raw)

            self.assertEqual(config_path.read_bytes(), websearch.UTF8_BOM + normalized)
            self.assertEqual(list(Path(temp_dir).glob("*.tmp")), [])
            self.assertEqual(list(Path(temp_dir).glob(".*.tmp")), [])

    def test_read_config_file_parses_bom_config_when_normalization_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            normalized = b'GROK_SEARCH_MODEL = "model"\n'
            config_path.write_bytes(websearch.UTF8_BOM + normalized)

            with mock.patch.object(
                websearch,
                "normalize_utf8_bom_config",
                side_effect=websearch.ConfigError("denied"),
            ):
                values = websearch.read_config_file(config_path)

            self.assertEqual(values["GROK_SEARCH_MODEL"], "model")
            self.assertEqual(config_path.read_bytes(), websearch.UTF8_BOM + normalized)


class SearchFallbackTests(unittest.TestCase):
    def test_search_result_status_reports_skip_reason(self) -> None:
        self.assertEqual(
            websearch.search_result_status({"skip_reason": "does not support recency filters"}),
            "does not support recency filters",
        )

    def test_duckduckgo_search_explains_recency_skip_without_network_request(self) -> None:
        cfg = websearch.Config({})

        with mock.patch.object(websearch, "request_json") as request_json:
            result = websearch.duckduckgo_search(
                cfg,
                "latest ai news",
                max_sources=5,
                detailed=False,
                include_domains=[],
                exclude_domains=[],
                recency_days=7,
                search_mode="news",
            )

        request_json.assert_not_called()
        self.assertEqual(
            result,
            {
                "answer": "",
                "sources": [],
                "provider": "duckduckgo",
                "skip_reason": "does not support recency filters",
            },
        )

    def test_duckduckgo_search_explains_domain_skip_without_network_request(self) -> None:
        cfg = websearch.Config({})

        with mock.patch.object(websearch, "request_json") as request_json:
            result = websearch.duckduckgo_search(
                cfg,
                "python",
                max_sources=5,
                detailed=False,
                include_domains=["example.com"],
                exclude_domains=[],
                recency_days=None,
            )

        request_json.assert_not_called()
        self.assertEqual(
            result,
            {
                "answer": "",
                "sources": [],
                "provider": "duckduckgo",
                "skip_reason": "does not support domain filters",
            },
        )
