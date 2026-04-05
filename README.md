# RegPulse

EDA tool to generate APB Verilog register banks and UVM RAL models from Excel register specifications.

## Features

- **Excel-driven workflow** — define registers in `.xlsx`, get RTL and verification IP automatically
- **APB register bank** — synthesizable Verilog with full APB4 interface
- **UVM RAL model** — complete `uvm_reg_block` with backdoor path mapping
- **Multi-format output** — Verilog, SystemVerilog, C header, JSON, Markdown, HTML
- **Built-in validation** — 8 automated checks (address overlap, bit collision, name uniqueness, etc.)
- **Rich access types** — RW, RO, W1C, RC, RS with correct hardware semantics

## Quick Start

```bash
# Install dependencies
pip install pandas openpyxl jinja2

# Generate all outputs from an Excel spec
python -m src.cli --input_excel spec.xlsx --output_dir ./output

# Generate only RTL (Verilog + SystemVerilog)
python -m src.cli --input_excel spec.xlsx --output_dir ./output --rtl_only

# Select specific formats
python -m src.cli --input_excel spec.xlsx --output_dir ./output --format rtl,uvm,c_header

# Generate a blank template Excel
python -m src.cli --input_excel spec.xlsx --output_dir ./output --template_excel
```

## Excel Specification Format

Required columns:

| Column | Description |
|--------|-------------|
| Name | Register name |
| Offset | Byte offset (hex, e.g. `0x000`, `0x004`) |
| Field | Field name within the register |
| Bits | Bit position: `"0"` for single bit, `"3:1"` for range, integer for width from bit 0 |
| Access | `RW`, `RO`, `W1C`, `RC`, `RS` |
| Reset | Reset value |

Optional columns: `Hardware Trigger`, `Side Effect`

## Output Formats

| File | Format | Description |
|------|--------|-------------|
| `*_regs.v` | Verilog | APB register bank RTL |
| `*_regs_reg_block.sv` | SystemVerilog | UVM RAL model |
| `*_regs.h` | C header | Register definitions and access macros |
| `*_regs.json` | JSON | Machine-readable register map |
| `*_regs.md` | Markdown | Human-readable register documentation |
| `*_regs.html` | HTML | Styled register map with access type badges |

## Example Output

The `output/` directory contains a sample `chip_regs` register bank generated from `tests/sample_spec.xlsx`:

- **6 registers**: CTRL, STATUS, INT_EN, INT_STS, DMA_CTRL, ERR_STS
- **24 bytes** address space
- Demonstrates RW, RO, W1C, RC, RS access types
- Includes hardware interface ports (status inputs, control outputs)

## Project Structure

```
Register/
├── src/
│   ├── models/          # Field, Register, RegisterBank data models
│   ├── parser/          # Excel parser (xlsx → RegisterBank)
│   ├── validators/      # 8 validation checks
│   ├── generators/      # RTL, UVM, C header, JSON, Markdown, HTML generators
│   ├── templates/       # Jinja2 templates (.v.j2, .sv.j2)
│   └── cli.py           # Command-line interface
├── tests/               # Test suite (pytest)
├── prompt/              # Development prompts
└── output/              # Example generated output
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## License

MIT
