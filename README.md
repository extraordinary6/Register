# RegPulse

RegPulse generates bus-agnostic register file cores, optional bus protocol wrappers, and UVM RAL models from Excel register specifications.

## Features

- Excel-driven workflow: define registers in `.xlsx`, then generate RTL and verification artifacts
- Bus-agnostic register core with generic `clk/rst_n/addr/wdata/wen/wstrb/ren/rdata/ready` interface
- Optional APB4, AHB-Lite, and AXI4-Lite wrappers
- Data-width aware generation for 8/16/32/64-bit register banks
- Byte-strobe masking for sub-word writes
- UVM RAL output with backdoor path mapping
- Verilog, SystemVerilog, C header, JSON, Markdown, and HTML outputs
- Structural validation plus optional advisory lint checks
- Access types: `RW`, `RO`, `WO`, `W1C`, `W1S`, `W0C`, `RC`, `RS`
- Hardware sideband ports and interrupt aggregation support

## Installation

### Install from a source checkout

```bash
pip install .
regpulse --help
```

This installs runtime dependencies from `pyproject.toml` and exposes the `regpulse` CLI.

### Editable install for development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Run the repo entrypoint directly

```bash
python main.py --help
```

`main.py` is a thin wrapper around the same CLI implementation used by `regpulse`.

## Quick Start

```bash
# Generate register core + all default formats
python main.py --input_excel spec.xlsx --output_dir ./output

# Generate with a bus wrapper
python main.py --input_excel spec.xlsx --output_dir ./output --bus apb
python main.py --input_excel spec.xlsx --output_dir ./output --bus ahb
python main.py --input_excel spec.xlsx --output_dir ./output --bus axi

# Generate selected formats only
python main.py --input_excel spec.xlsx --output_dir ./output --format rtl,uvm,c_header

# Wrapper generation auto-includes the RTL core even if --format omits it
python main.py --input_excel spec.xlsx --output_dir ./output --format uvm,json --bus apb

# Parse + validate only
python main.py --input_excel spec.xlsx --output_dir ./output --dry_run

# Run advisory lint checks
python main.py --input_excel spec.xlsx --output_dir ./output --lint

# Generate a blank Excel template
python main.py --output_dir ./output --template_excel
```

You can replace `python main.py` with `regpulse` after installation.
The output directory is user-chosen; `./output` in the examples is only a sample location for generated artifacts.

## Architecture

RegPulse separates register logic from bus protocol:

```text
chip_regs_{apb,ahb,axi}_wrapper  ->  bus protocol to generic interface bridge
chip_regs_regfile_core           ->  bus-agnostic register file
```

- `regfile_core`: generated whenever RTL output is requested, and auto-generated when `--bus` is used
- `bus_wrapper`: optional, maps the selected bus to the generic core interface

## Excel Specification Format

Required columns:

| Column | Description |
|--------|-------------|
| `Name` | Register name |
| `Offset` | Byte offset, for example `0x000` or `0x004` |
| `Field` | Field name within the register. Blank/NaN values are rejected. |
| `Bits` | Bit position, for example `"0"` or `"3:1"` |
| `Access` | `RW`, `RO`, `WO`, `W1C`, `W1S`, `W0C`, `RC`, `RS` |
| `Reset` | Reset value |

Optional columns:

- `Description`
- `Hardware Trigger` with values `input` or `output`
- `Side Effect`
- `Interrupt` with values `source` or `enable`

Fully blank rows are skipped.

## Output Files

| File | When generated | Description |
|------|----------------|-------------|
| `{name}_regfile_core.v` | `rtl` format or any `--bus` wrapper | Bus-agnostic register file core |
| `{name}_apb_wrapper.v` | `--bus apb` | APB4 wrapper |
| `{name}_ahb_wrapper.v` | `--bus ahb` | AHB-Lite wrapper |
| `{name}_axi_wrapper.v` | `--bus axi` | AXI4-Lite wrapper |
| `{name}_reg_block.sv` | `uvm` format | UVM RAL model |
| `{name}.h` | `c_header` format | C header |
| `{name}.json` | `json` format | Machine-readable register map |
| `{name}.md` | `markdown` format | Markdown documentation |
| `{name}.html` | `html` format | HTML documentation |

## CLI Reference

Use either form:

```text
python main.py --input_excel <file> --output_dir <dir> [options]
regpulse --input_excel <file> --output_dir <dir> [options]

Required:
  --output_dir DIR          Output directory
  --input_excel FILE        Input .xlsx register specification
                            Required unless --template_excel is used

Optional:
  --block_name NAME         Module/block name (default: reg_top)
  --base_address ADDR       Base address, e.g. 0x8000_0000 (default: 0x0)
  --block_size ADDR         Optional declared block size for lint checks
  --data_width N            Data width: 8, 16, 32, or 64 (default: 32)
  --bus {none,apb,ahb,axi}  Generate the selected wrapper; auto-includes rtl
  --format FMTS             Comma-separated formats: rtl,uvm,c_header,json,html,markdown
  --rtl_only                Shorthand for --format rtl
  --uvm_only                Shorthand for --format uvm
  --template_excel          Generate blank Excel template and exit
  --dry_run                 Parse and validate only
  --lint                    Run advisory lint checks and print findings
  --lint_strict             Treat warning-level lint findings as failures
  --verbose                 Enable debug logging
  --version                 Show version
```

## Project Structure

```text
Register/
├── src/
│   ├── models/          # Field, Register, RegisterBank data models
│   ├── parser/          # Excel parser
│   ├── validators/      # Structural validation
│   ├── generators/      # RTL, wrappers, UVM, C header, JSON, Markdown, HTML
│   ├── lint/            # Advisory lint rules and reporting
│   └── templates/       # Jinja2 templates packaged with the CLI
├── main.py              # Command-line entrypoint
├── tests/               # Pytest test suite
├── README.md
└── pyproject.toml
```

Generated artifacts are written to a user-specified directory such as `./output/`; treat that directory as build output rather than project source.

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
