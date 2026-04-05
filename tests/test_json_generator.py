"""Tests for the JSON generator."""

from __future__ import annotations

import json
import tempfile

from src.generators.json_generator import JsonGenerator


def test_json_structure(sample_bank):
    gen = JsonGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            data = json.load(f)

    assert data["block_name"] == "test_top"
    assert data["num_registers"] == 5
    assert "registers" in data


def test_side_effect_included(sample_bank):
    gen = JsonGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            data = json.load(f)

    status_reg = next(r for r in data["registers"] if r["name"] == "STATUS")
    pend_field = next(f for f in status_reg["fields"] if f["name"] == "PEND")
    assert pend_field["side_effect"] == "Set on read"


def test_interrupt_role_included():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("irq_json")
    reg = Register("INT_STS", 0x00)
    field = Field("DONE", "0", "W1C", 0, hardware_interface="input")
    field.interrupt_role = "source"
    reg.add_field(field)
    bank.add_register(reg)

    gen = JsonGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            data = json.load(f)

    out_field = data["registers"][0]["fields"][0]
    assert out_field["interrupt_role"] == "source"


def test_base_address_and_data_width(sample_bank):
    sample_bank.base_address = 0x1000
    sample_bank.data_width = 32
    gen = JsonGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            data = json.load(f)

    assert data["base_address"] == "0x00001000"
    assert data["data_width"] == 32


def test_field_attributes(sample_bank):
    gen = JsonGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            data = json.load(f)

    ctrl = next(r for r in data["registers"] if r["name"] == "CTRL")
    en_field = next(f for f in ctrl["fields"] if f["name"] == "EN")
    assert en_field["access"] == "RW"
    assert en_field["msb"] == 0
    assert en_field["lsb"] == 0
    assert en_field["width"] == 1
    assert en_field["hw_interface"] == "output"
    assert en_field["is_bus_writable"] is True
    assert en_field["has_read_side_effect"] is False
