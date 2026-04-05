"""Tests for the RTL Verilog generator."""

from __future__ import annotations

import tempfile

from src.generators.rtl_generator import RtlGenerator


def test_hw_input_synchronization(sample_bank):
    """HW input fields must be continuously latched every clock."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "STATUS[0:0] <= status_done_st" in code
    assert "STATUS[1:1] <= status_busy_st" in code
    assert "STATUS[2:2] <= STATUS[2:2] | status_pend_st" in code
    assert "INT_STS[0:0] <= INT_STS[0:0] | int_sts_overrun_st" in code
    assert "ERR_STS[0:0] <= ERR_STS[0:0] | err_sts_parity_st" in code


def test_w1s_w0c_hw_input_synchronization():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("sticky_top")
    reg = Register("STICKY", 0x00)
    reg.add_field(Field("SETF", "0", "W1S", 0, hardware_interface="input"))
    reg.add_field(Field("CLRF", "1:1", "W0C", 0, hardware_interface="input"))
    bank.add_register(reg)

    gen = RtlGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "STICKY[0:0] <= STICKY[0:0] | sticky_setf_st" in code
    assert "STICKY[1:1] <= STICKY[1:1] | sticky_clrf_st" in code


def test_rc_rs_merged_into_read_block(sample_bank):
    """RC/RS must be in the read always block, not separate blocks."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "Read-Clear (RC) logic" not in code
    assert "Read-Set (RS) logic" not in code
    assert "Read (with merged Read-Clear / Read-Set)" in code
    assert "ERR_STS[0:0] <= 1'd0" in code
    assert "ERR_STS[1:1] <= 1'd0" in code
    assert "STATUS[2:2] <= 1'd1" in code


def test_w1c_write_no_hw_or(sample_bank):
    """W1C write path should not consume the HW input directly."""
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    write_section = code.split("Write (with byte-strobe")[1].split("Read (with merged")[0]
    assert "| int_sts_overrun_st" not in write_section


def test_rdata_reset(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "rdata_reg <= 32'h0" in code


def test_hw_output_assignments(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "assign ctrl_en_q = CTRL[0:0]" in code
    assert "assign ctrl_mode_q = CTRL[3:1]" in code


def test_interrupt_aggregation():
    """irq_o should be generated when interrupt pairs exist."""
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_top")
    int_sts = Register("INT_STS", 0x04)
    src_field = Field("DONE", "0", "W1C", 0, hardware_interface="input")
    src_field.interrupt_role = "source"
    int_sts.add_field(src_field)
    int_sts.add_field(Field("PAD", "7:1", "RO", 0))
    bank.add_register(int_sts)

    int_en = Register("INT_EN", 0x08)
    en_field = Field("DONE", "0", "RW", 0, hardware_interface="output")
    en_field.interrupt_role = "enable"
    int_en.add_field(en_field)
    int_en.add_field(Field("PAD", "7:1", "RO", 0))
    bank.add_register(int_en)

    gen = RtlGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "irq_o" in code
    assert "assign irq_o" in code
    assert "INT_STS[0:0] & INT_EN[0:0]" in code


def test_no_interrupt_when_no_pairs(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "irq_o" not in code


def test_wo_w1s_w0c_access_types():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("test_wo")
    reg = Register("WO_REG", 0x00)
    reg.add_field(Field("CMD", "0", "WO", 0, hardware_interface="output"))
    reg.add_field(Field("SET", "1:1", "W1S", 0))
    reg.add_field(Field("CLR", "2:2", "W0C", 0))
    reg.add_field(Field("PAD", "7:3", "RO", 0))
    bank.add_register(reg)

    gen = RtlGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    write_section = code.split("Write (with byte-strobe")[1].split("Read (with merged")[0]
    assert "WO_REG[0:0] <= wdata[0:0]" in write_section
    assert "WO_REG[1:1] <= WO_REG[1:1] | wdata[1:1]" in write_section
    assert "WO_REG[2:2] <= WO_REG[2:2] & wdata[2:2]" in write_section
    read_section = code.split("Read (with merged")[1]
    assert "rdata_reg[0:0] <= 1'd0" in read_section


def test_module_name_has_regfile_core(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "module test_top_regfile_core" in code


def test_generic_interface_signals(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "input  wire             clk," in code
    assert "input  wire             rst_n," in code
    assert "input  wire             wen," in code
    assert "input  wire             ren," in code
    assert "output wire             ready" in code
    assert "output wire [DW-1:0]    rdata," in code
    assert "pclk" not in code
    assert "psel" not in code
    assert "penable" not in code
    assert "pwrite" not in code
    assert "prdata" not in code
    assert "pready" not in code


def test_wstrb_masking(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    write_section = code.split("Write (with byte-strobe")[1].split("Read (with merged")[0]
    assert "wstrb[0:0] != 1'd0" in write_section


def test_generation_does_not_mutate_fields(sample_bank):
    field = sample_bank.registers[0].fields[0]
    assert not hasattr(field, "wstrb_low")
    assert not hasattr(field, "wstrb_high")

    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        gen.generate(tmpdir)

    assert not hasattr(field, "wstrb_low")
    assert not hasattr(field, "wstrb_high")


def test_read_ready_timing(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "ready_reg <= 1'b1" in code
    assert "ready_reg <= 1'b0" in code
    assert "rdata = rdata_reg" in code
    assert "ready = ready_reg" in code


def test_addr_is_word_address(sample_bank):
    gen = RtlGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "case (addr[" in code
    assert "paddr" not in code
