"""Tests for the AHB-Lite wrapper generator."""

import tempfile

from src.generators.ahb_wrapper_generator import AhbWrapperGenerator


def test_wrapper_instantiates_regfile_core(sample_bank):
    gen = AhbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "test_top_regfile_core" in code
    assert "u_regfile_core" in code


def test_ahb_signals_declared(sample_bank):
    gen = AhbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "input  wire                        hclk," in code
    assert "input  wire                        hresetn," in code
    assert "input  wire [31:0]                 haddr," in code
    assert "input  wire [31:0] hwdata," in code
    assert "output wire [31:0] hrdata," in code
    assert "input  wire                        hwrite," in code
    assert "input  wire                        hsel," in code
    assert "input  wire [1:0]                  htrans," in code
    assert "input  wire [2:0]                  hburst," in code
    assert "input  wire [2:0]                  hsize," in code
    assert "input  wire [3:0] hwstrb," in code
    assert "input  wire                        hready," in code
    assert "output wire                        hreadyout," in code
    assert "output wire [1:0]                  hresp" in code


def test_ahb_hresp_ok(sample_bank):
    gen = AhbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "assign hresp      = 2'b00" in code


def test_ahb_txn_decode(sample_bank):
    gen = AhbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "htrans == 2'b10 || htrans == 2'b11" in code
    assert "read_pending" in code


def test_hw_port_passthrough(sample_bank):
    gen = AhbWrapperGenerator(sample_bank)
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

    gen = AhbWrapperGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "output wire        irq_o" in code
    assert ".irq_o      (irq_o)" in code


def test_no_irq_when_no_pairs(sample_bank):
    gen = AhbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "irq_o" not in code


def test_module_name(sample_bank):
    gen = AhbWrapperGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        assert path.endswith("test_top_ahb_wrapper.v")
        with open(path) as f:
            code = f.read()

    assert "module test_top_ahb_wrapper" in code


def test_ahb_data_width_64():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_top", data_width=64)
    reg = Register("CTRL", 0x00, data_width=64)
    reg.add_field(Field("F", "7:0", "RW", 0))
    bank.add_register(reg)

    gen = AhbWrapperGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "input  wire [63:0] hwdata," in code
    assert "input  wire [7:0] hwstrb," in code
    assert "output wire [63:0] hrdata," in code
    assert ":3]" in code
