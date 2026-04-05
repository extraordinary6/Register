"""Tests for the Excel parser."""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import pytest

from src.parser.excel_parser import ExcelParser


def test_parse_sample_excel(sample_excel):
    bank = ExcelParser(sample_excel, block_name="test").parse()
    assert bank.num_registers == 5
    assert len(bank.registers[0].fields) == 3  # CTRL


def test_parse_interrupt_column(sample_excel_with_irq):
    bank = ExcelParser(sample_excel_with_irq, block_name="test").parse()
    assert bank.interrupt_pairs
    assert len(bank.interrupt_pairs) == 1


def test_parse_missing_column(sample_excel):
    """Excel with a missing required column should raise ValueError."""
    bad_path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({"Name": ["A"], "Field": ["F"], "Bits": ["0"]})
    df.to_excel(bad_path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        ExcelParser(bad_path, block_name="test").parse()
    os.remove(bad_path) if os.path.exists(bad_path) else None


def test_parse_auto_increment():
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["A", "B", "C"],
        "Offset": ["0x00", "", ""],
        "Field": ["F", "F", "F"],
        "Bits": ["7:0", "7:0", "7:0"],
        "Access": ["RW", "RW", "RW"],
        "Reset": ["0", "0", "0"],
    })
    df.to_excel(path, index=False)
    bank = ExcelParser(path, block_name="test").parse()
    assert bank.registers[0].offset == 0x00
    assert bank.registers[1].offset == 0x04
    assert bank.registers[2].offset == 0x08
    os.remove(path) if os.path.exists(path) else None


def test_parse_hex_reset():
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["A"], "Offset": ["0x00"], "Field": ["F"],
        "Bits": ["7:0"], "Access": ["RW"], "Reset": ["0xFF"],
    })
    df.to_excel(path, index=False)
    bank = ExcelParser(path, block_name="test").parse()
    assert bank.registers[0].fields[0].reset_val == 0xFF
    os.remove(path) if os.path.exists(path) else None


def test_parse_invalid_access():
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["A"], "Offset": ["0x00"], "Field": ["F"],
        "Bits": ["0"], "Access": ["INVALID"], "Reset": ["0"],
    })
    df.to_excel(path, index=False)
    with pytest.raises(ValueError, match="Invalid access type"):
        ExcelParser(path, block_name="test").parse()
    os.remove(path) if os.path.exists(path) else None


@pytest.fixture
def sample_excel_with_irq(tmp_path):
    """Excel with Interrupt column for testing."""
    xlsx_path = tmp_path / "test_irq.xlsx"
    data = {
        "Name": ["INT_STS", "INT_EN"],
        "Offset": ["0x00", "0x04"],
        "Field": ["DONE", "DONE"],
        "Bits": ["0", "0"],
        "Access": ["W1C", "RW"],
        "Reset": ["0", "0"],
        "Hardware Trigger": ["input", "output"],
        "Side Effect": ["", ""],
        "Interrupt": ["source", "enable"],
    }
    df = pd.DataFrame(data)
    df.to_excel(xlsx_path, index=False)
    return str(xlsx_path)


def test_parse_float_numeric_strings():
    """Excel cells stored as float (e.g. '1.0', '3.0:1.0') should parse."""
    path = tempfile.mktemp(suffix=".xlsx")
    df = pd.DataFrame({
        "Name": ["A", "B"],
        "Offset": ["0.0", "0x4.0"],
        "Field": ["F", "G"],
        "Bits": ["7.0:0.0", "1.0"],
        "Access": ["RW", "RW"],
        "Reset": ["0xFF.0", "1.0"],
    })
    df.to_excel(path, index=False)
    bank = ExcelParser(path, block_name="test").parse()
    assert bank.registers[0].fields[0].msb == 7
    assert bank.registers[0].fields[0].lsb == 0
    assert bank.registers[0].fields[0].reset_val == 0xFF
    assert bank.registers[1].fields[0].width == 1
    assert bank.registers[1].fields[0].reset_val == 1
    os.remove(path) if os.path.exists(path) else None


def test_blank_row_is_skipped(tmp_path):
    path = tmp_path / "blank_row.xlsx"
    df = pd.DataFrame({
        "Name": ["CTRL", ""],
        "Offset": ["0x00", ""],
        "Field": ["EN", ""],
        "Bits": ["0", ""],
        "Access": ["RW", ""],
        "Reset": ["0", ""],
    })
    df.to_excel(path, index=False)
    bank = ExcelParser(str(path), block_name="test").parse()
    assert bank.num_registers == 1
    assert bank.registers[0].fields[0].name == "EN"


def test_blank_field_cell_raises_parse_error(tmp_path):
    path = tmp_path / "blank_field.xlsx"
    df = pd.DataFrame({
        "Name": ["CTRL"],
        "Offset": ["0x00"],
        "Field": [""],
        "Bits": ["0"],
        "Access": ["RW"],
        "Reset": ["0"],
    })
    df.to_excel(path, index=False)

    with pytest.raises(ValueError, match=r"Row 2: missing required cell\(s\): Field"):
        ExcelParser(str(path), block_name="test").parse()


def test_nan_field_cell_raises_parse_error(tmp_path):
    path = tmp_path / "nan_field.xlsx"
    df = pd.DataFrame({
        "Name": ["CTRL"],
        "Offset": ["0x00"],
        "Field": [float("nan")],
        "Bits": ["0"],
        "Access": ["RW"],
        "Reset": ["0"],
    })
    df.to_excel(path, index=False)

    with pytest.raises(ValueError, match=r"Row 2: missing required cell\(s\): Field"):
        ExcelParser(str(path), block_name="test").parse()
