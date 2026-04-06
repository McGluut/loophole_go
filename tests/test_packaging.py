from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


class PackagingTests(unittest.TestCase):
    def test_pyproject_declares_editable_installable_package_layout(self) -> None:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        data = tomllib.loads(pyproject.read_text())

        self.assertEqual(data["build-system"]["build-backend"], "setuptools.build_meta")
        self.assertIn("setuptools", " ".join(data["build-system"]["requires"]))

        package_find = data["tool"]["setuptools"]["packages"]["find"]
        self.assertIn("loophole*", package_find["include"])
        self.assertIn("sessions*", package_find["exclude"])
