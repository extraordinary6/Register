"""Tests for the AXI4-Lite wrapper generator."""

from __future__ import annotations

import tempfile

from src.generators.axi_wrapper_generator import AxiWrapperGenerator


def test_wrapper_instantiates_regfile_core(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "test_top_regfile_core" in code
    assert "u_regfile_core" in code


def test_axi_channels_declared(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "awvalid" in code
    assert "awready" in code
    assert "input  wire [4:0] awaddr," in code
    assert "wvalid" in code
    assert "wready" in code
    assert "wdata" in code
    assert "wstrb" in code
    assert "bvalid" in code
    assert "bready" in code
    assert "bresp" in code
    assert "arvalid" in code
    assert "arready" in code
    assert "input  wire [4:0] araddr," in code
    assert "rvalid" in code
    assert "rready" in code
    assert "rdata" in code
    assert "rresp" in code


def test_axi_resp_ok(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "assign bresp  = 2'b00" in code
    assert "assign rresp  = 2'b00" in code


def test_axi_handshake_logic(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "awaddr_sel" in code
    assert "awaddr_reg" in code
    assert "wdata_sel" in code
    assert "bvalid_reg" in code
    assert "ar_sel" in code
    assert "araddr_reg" in code
    assert "rvalid_reg" in code


def test_hw_port_passthrough(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "output wire [0:0] ctrl_en_q" in code
    assert "input  wire [0:0] status_done_st" in code
    assert ".ctrl_en_q (ctrl_en_q)" in code
    assert ".status_done_st (status_done_st)" in code


def test_irq_passthrough():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_top")
    int_sts = Register("INT_STS", 0x04)
    src_field = Field("DONE", "0", "W1C", 0, hardware_interface="input")
    src_field.interrupt_role = "source"
    int_sts.add_field(src_field)
    bank.add_register(int_sts)

    int_en = Register("INT_EN", 0x08)
    en_field = Field("DONE", "0", "RW", 0, hardware_interface="output")
    en_field.interrupt_role = "enable"
    int_en.add_field(en_field)
    bank.add_register(int_en)

    gen = AxiWrapperGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "output wire        irq_o" in code
    assert ".irq_o      (irq_o)" in code


def test_no_irq_when_no_pairs(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "irq_o" not in code


def test_module_name(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        assert path.endswith("test_top_axi_wrapper.v")
        with open(path) as f:
            code = f.read()

    assert "module test_top_axi_wrapper" in code


def test_read_uses_araddr(sample_bank):
    gen = AxiWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "araddr_reg" in code
    assert "awaddr_reg" in code
    assert "core_wen ? awaddr_reg" in code


def test_axi_data_width_64():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_top", data_width=64)
    reg = Register("CTRL", 0x00, data_width=64)
    reg.add_field(Field("F", "7:0", "RW", 0))
    bank.add_register(reg)

    gen = AxiWrapperGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "input  wire [63:0] wdata," in code
    assert "input  wire [7:0] wstrb," in code
    assert "output wire [63:0] rdata," in code


def test_axi_external_address_width_tracks_bank_span():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("addr_top")
    reg0 = Register("REG0", 0x00)
    reg0.add_field(Field("F0", "0", "RW", 0))
    bank.add_register(reg0)
    reg1 = Register("REG1", 0x10)
    reg1.add_field(Field("F1", "0", "RW", 0))
    bank.add_register(reg1)

    gen = AxiWrapperGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "input  wire [4:0] awaddr," in code
    assert "input  wire [4:0] araddr," in code
