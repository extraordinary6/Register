"""RTL Generator — produces synthesizable Verilog from a RegisterBank."""

from __future__ import annotations

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.models.register_bank import RegisterBank


class RtlGenerator:
    """Generate a generic register-file core Verilog module from a RegisterBank."""

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
        self.env.filters["ones"] = lambda w: str((1 << w) - 1)
        self.env.filters["hex_zero"] = lambda dw: "0" * (dw // 4)
        self.env.filters["hex_reset"] = lambda v: f"{v:0{self.bank.data_width // 4}X}"
        self.env.filters["wstrb_low"] = lambda field: field.lsb // 8
        self.env.filters["wstrb_high"] = lambda field: field.msb // 8

    def generate(self, output_dir: str) -> str:
        """Render the Verilog and write to <output_dir>/<module_name>_regfile_core.v.

        Returns the path of the generated file.
        """
        template = self.env.get_template("regfile_core.v.j2")

        dw = self.bank.data_width
        byte_width = dw // 8
        strb_width = byte_width
        num_words = self.bank.address_space // byte_width
        addr_width = max(1, (num_words - 1).bit_length()) if num_words > 0 else 1
        addr_msb = addr_width - 1
        dw_msb = dw - 1

        code = template.render(
            module_name=self.bank.name,
            registers=self.bank.registers,
            data_width=dw,
            byte_width=byte_width,
            strb_width=strb_width,
            addr_width=addr_width,
            addr_msb=addr_msb,
            dw_msb=dw_msb,
            interrupt_pairs=self.bank.interrupt_pairs,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        out_path = os.path.join(output_dir, f"{self.bank.name}_regfile_core.v")
        with open(out_path, "w") as fh:
            fh.write(code)
        return out_path
