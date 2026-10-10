"""Dependency-free scaffold checks; run with Python 3.12 unittest discovery."""

import os
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PackageSmokeTests(unittest.TestCase):
    """Check the public import contract without installing the distribution."""

    def test_package_import_is_quiet_and_dependency_free(self) -> None:
        # -I ignores site/PYTHONPATH configuration; -S disables site-packages.
        # A separate interpreter avoids hiding dependencies behind cached imports.
        code = (
            "import sys; "
            f"sys.path.insert(0, {str(PROJECT_ROOT / 'src')!r}); "
            "import enterprise_mind"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_package_version_matches_distribution_metadata(self) -> None:
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as metadata_file:
            metadata = tomllib.load(metadata_file)
        code = (
            "import sys; "
            f"sys.path.insert(0, {str(PROJECT_ROOT / 'src')!r}); "
            "import enterprise_mind; print(enterprise_mind.__version__)"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), metadata["project"]["version"])


if __name__ == "__main__":
    unittest.main()
