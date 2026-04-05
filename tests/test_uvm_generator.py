"""Tests for the UVM RAL generator."""

from __future__ import annotations

import tempfile

from src.generators.uvm_generator import UvmGenerator


def test_hdl_path_input_uses_st_signal(sample_bank):
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert '"status_done_st"' in code
    assert '"status_busy_st"' in code
    assert '"int_sts_overrun_st"' in code
    assert '"err_sts_parity_st"' in code


def test_hdl_path_output_uses_reg_bits(sample_bank):
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert '"ctrl[0:0]"' in code
    assert '"ctrl[3:1]"' in code


def test_ro_register_not_rand(sample_bank):
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "rand test_top_STATUS_reg STATUS" not in code
    assert "rand test_top_ERR_STS_reg ERR_STS" not in code
    assert "rand test_top_CTRL_reg CTRL" in code


def test_volatile_set_for_special_access(sample_bank):
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert ".volatile(1)" in code


def test_effective_access_mapping(sample_bank):
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert 'add_reg(STATUS, 5\'h04, "RO")' in code
    assert 'add_reg(CTRL, 5\'h00, "RW")' in code


def test_uvm_uses_data_width_not_hardcoded_32():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    for dw in (8, 16, 64):
        bank = RegisterBank("dw_test", data_width=dw)
        reg = Register("REG_A", 0x00, data_width=dw)
        reg.add_field(Field("F", "0", "RW", 0))
        bank.add_register(reg)

        gen = UvmGenerator(bank)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(tmpdir)
            with open(path) as f:
                code = f.read()

        assert f"super.new(name, {dw}, UVM_NO_COVERAGE)" in code
        assert f"{dw}'h000" not in code
        assert "add_reg(REG_A, " in code


def test_uvm_high_offset_uses_address_width_not_data_width():
    from src.models.field import Field
    from src.models.register import Register
    from src.models.register_bank import RegisterBank

    bank = RegisterBank("addr_test", data_width=8)
    reg0 = Register("REG0", 0x00, data_width=8)
    reg0.add_field(Field("F0", "0", "RW", 0))
    bank.add_register(reg0)

    reg1 = Register("REG1", 0x100, data_width=8)
    reg1.add_field(Field("F1", "0", "RW", 0))
    bank.add_register(reg1)

    gen = UvmGenerator(bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert 'add_reg(REG1, 9\'h100, "RW")' in code
    assert '8\'h100' not in code


def test_uvm_include_guard(sample_bank):
    gen = UvmGenerator(sample_bank)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(tmpdir)
        with open(path) as f:
            code = f.read()

    assert "`ifndef TEST_TOP_REG_BLOCK_SV" in code
    assert "`endif // TEST_TOP_REG_BLOCK_SV" in code
