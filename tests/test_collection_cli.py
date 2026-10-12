"""Command-level validation and dry-run defaults; no network access."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from collection_fixtures import manifest_data
from enterprise_mind.ingestion.__main__ import main


class CollectionCLITests(unittest.TestCase):
    def test_validate_and_dry_run_are_offline(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "sources.yaml"
            manifest.write_text(json.dumps(manifest_data(approved=False)), encoding="utf-8")
            with (
                patch("socket.create_connection", side_effect=AssertionError("network forbidden")),
                patch("socket.getaddrinfo", side_effect=AssertionError("DNS forbidden")),
            ):
                for arguments in (["validate", "--manifest", str(manifest)],
                                  ["collect", "--manifest", str(manifest),
                                   "--source", "fictional-hr"]):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        self.assertEqual(main(arguments), 0)
                    self.assertIsInstance(json.loads(output.getvalue()), dict)
            self.assertFalse((Path(folder) / "data").exists())

    def test_unapproved_download_returns_error_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "sources.yaml"
            manifest.write_text(json.dumps(manifest_data(approved=False)), encoding="utf-8")
            error = io.StringIO()
            with (
                patch("socket.create_connection", side_effect=AssertionError("network forbidden")),
                patch("socket.getaddrinfo", side_effect=AssertionError("DNS forbidden")),
            ):
                with redirect_stderr(error):
                    result = main(["collect", "--manifest", str(manifest),
                                   "--source", "fictional-hr", "--download"])
            self.assertEqual(result, 2)
            self.assertIn("download rejected", error.getvalue())


if __name__ == "__main__":
    unittest.main()
