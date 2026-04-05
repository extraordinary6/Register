"""Tests for packaging metadata needed by installed RegPulse builds."""

from __future__ import annotations

from pathlib import Path
import tomllib


def test_pyproject_includes_template_package_data():
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert data["project"]["scripts"]["regpulse"] == "src.cli:run"
    assert data["tool"]["setuptools"]["package-data"]["src"] == ["templates/*.j2"]
