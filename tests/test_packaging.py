"""Tests for packaging metadata needed by installed RegPulse builds."""

from __future__ import annotations

from pathlib import Path
import tomllib


def test_pyproject_includes_template_package_data_and_dynamic_version_source():
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert data["project"]["scripts"]["regpulse"] == "src.cli:run"
    assert data["project"]["dynamic"] == ["version"]
    assert data["tool"]["setuptools"]["dynamic"]["version"] == {"attr": "src.__version__"}
    assert data["tool"]["setuptools"]["package-data"]["src"] == ["templates/*.j2"]
