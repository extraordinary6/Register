"""Tests for CLI entrypoint wiring and CLI behavior."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

import src.cli


def test_main_py_delegates_to_src_cli_run(monkeypatch):
    """The repo-root entrypoint should be a thin wrapper around src.cli.run."""
    called = {"count": 0}

    def fake_run(argv=None):
        called["count"] += 1
        assert argv is None

    monkeypatch.setattr(src.cli, "run", fake_run)

    main_path = Path(__file__).resolve().parents[1] / "main.py"
    runpy.run_path(str(main_path), run_name="__main__")

    assert called["count"] == 1


def test_template_excel_does_not_require_input(tmp_path):
    out_dir = tmp_path / "out"
    src.cli.main(["--output_dir", str(out_dir), "--template_excel"])
    assert (out_dir / "register_template.xlsx").exists()


def test_input_excel_required_without_template(tmp_path):
    out_dir = tmp_path / "out"
    with pytest.raises(SystemExit) as exc:
        src.cli.main(["--output_dir", str(out_dir)])
    assert exc.value.code == 2


def test_bus_auto_includes_rtl(monkeypatch, sample_excel, tmp_path):
    generated = []

    class StubRtl:
        def __init__(self, bank):
            pass

        def generate(self, output_dir):
            generated.append("rtl")
            return str(Path(output_dir) / "rtl.v")

    class StubUvm:
        def __init__(self, bank):
            pass

        def generate(self, output_dir):
            generated.append("uvm")
            return str(Path(output_dir) / "uvm.sv")

    class StubApb:
        def __init__(self, bank):
            pass

        def generate(self, output_dir):
            generated.append("apb")
            return str(Path(output_dir) / "apb.v")

    monkeypatch.setattr(src.cli, "RtlGenerator", StubRtl)
    monkeypatch.setattr(src.cli, "UvmGenerator", StubUvm)
    monkeypatch.setattr(src.cli, "ApbWrapperGenerator", StubApb)
    monkeypatch.setitem(src.cli._GENERATORS, "rtl", ("RTL (Verilog)", StubRtl))
    monkeypatch.setitem(src.cli._GENERATORS, "uvm", ("UVM RAL (SystemVerilog)", StubUvm))

    src.cli.main([
        "--input_excel", sample_excel,
        "--output_dir", str(tmp_path / "out"),
        "--format", "uvm",
        "--bus", "apb",
    ])

    assert generated == ["rtl", "uvm", "apb"]


def test_readme_examples_match_current_cli_contract():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    assert "python main.py --output_dir ./output --template_excel" in readme
    assert "auto-includes rtl" in readme
    assert "Required unless --template_excel is used" in readme
