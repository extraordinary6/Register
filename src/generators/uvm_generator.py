"""UVM RAL Generator — produces SystemVerilog register model from a RegisterBank."""

from __future__ import annotations

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.models.register_bank import RegisterBank


class UvmGenerator:
    """Generate a UVM RAL block (.sv) from a RegisterBank."""

    def __init__(self, bank: RegisterBank, template_dir: str | None = None):
        self.bank = bank
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        template_dir = os.path.abspath(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, output_dir: str) -> str:
        """Render the SystemVerilog and write to <output_dir>/<block_name>_reg_block.sv.

        Returns the path of the generated file.
        """
        template = self.env.get_template("uvm_reg_block.sv.j2")

        address_literal_width = (
            max(1, (self.bank.address_space - 1).bit_length())
            if self.bank.address_space > 0 else 1
        )
        address_hex_digits = max(1, (address_literal_width + 3) // 4)

        code = template.render(
            block_name=self.bank.name,
            registers=self.bank.registers,
            data_width=self.bank.data_width,
            address_literal_width=address_literal_width,
            address_hex_format=f"%0{address_hex_digits}X",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        out_path = os.path.join(output_dir, f"{self.bank.name}_reg_block.sv")
        with open(out_path, "w") as fh:
            fh.write(code)
        return out_path
