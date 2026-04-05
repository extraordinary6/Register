# RegPulse

EDA tool to generate bus-agnostic register file cores, optional bus protocol wrappers, and UVM RAL models from Excel register specifications.

## Features

- **Excel-driven workflow** — define registers in `.xlsx`, get RTL and verification IP automatically
- **Bus-agnostic register core** — synthesizable Verilog with generic `clk/rst_n/addr/wdata/wen/wstrb/ren/rdata/ready` interface
- **3 bus protocol wrappers** — APB4, AHB-Lite, AXI4-Lite bridges that instantiate the core
- **Parameterized width** — `AW` (address width) and `DW` (data width) as Verilog parameters, supports 8/16/32/64-bit
- **Byte-strobe masking** — per-field `wstrb` gating for sub-word writes
- **UVM RAL model** — complete `uvm_reg_block` with backdoor path mapping, data-width aware
- **Multi-format output** — Verilog, SystemVerilog, C header, JSON, Markdown, HTML
- **Built-in validation** — 9 automated checks (address overlap, bit collision, name uniqueness, etc.)
- **8 access types** — RW, RO, WO, W1C, W1S, W0C, RC, RS with correct hardware semantics
- **Hardware sideband interface** — `input` (hw → reg) and `output` (reg → hw) port generation
- **Interrupt aggregation** — automatic source/enable pair matching with `irq_o` output
- **Numeric cell tolerance** — handles Excel float-formatted numeric cells (e.g. `1.0` → `1`)

## Quick Start

```bash
# Install dependencies
pip install pandas openpyxl jinja2

# Generate register core + all formats
python main.py --input_excel spec.xlsx --output_dir ./output

# Generate with APB4 bus wrapper
python main.py --input_excel spec.xlsx --output_dir ./output --bus apb

# Generate with AHB-Lite bus wrapper
python main.py --input_excel spec.xlsx --output_dir ./output --bus ahb

# Generate with AXI4-Lite bus wrapper
python main.py --input_excel spec.xlsx --output_dir ./output --bus axi

# Generate only RTL
python main.py --input_excel spec.xlsx --output_dir ./output --rtl_only

# Select specific formats
python main.py --input_excel spec.xlsx --output_dir ./output --format rtl,uvm,c_header

# Parse and validate only (no file output)
python main.py --input_excel spec.xlsx --output_dir ./output --dry_run

# Generate a blank template Excel
python main.py --input_excel template.xlsx --output_dir ./output --template_excel
```

## Architecture (v0.6.0)

RegPulse decouples register logic from bus protocol into two layers:

```
┌──────────────────────────────────┐
│   chip_regs_{apb,ahb,axi}_wrapper│  ← Bus protocol → generic interface bridge
│  (bus-specific: pclk/hclk/aclk…) │
├──────────────────────────────────┤
│      chip_regs_regfile_core      │  ← Bus-agnostic register file
│  (clk, rst_n, addr, wdata, wen,  │
│   wstrb, ren, rdata, ready)      │
└──────────────────────────────────┘
```

- **regfile_core** — always generated, contains all register logic, HW sideband, interrupts
- **bus_wrapper** — optional (`--bus apb|ahb|axi`), translates bus protocol to the generic core interface

### Supported Bus Protocols

| Bus | Option | Interface |
|-----|--------|-----------|
| APB4 | `--bus apb` | `pclk, presetn, paddr, psel, penable, pwrite, pwdata, pstrb, prdata, pready, pslverr` |
| AHB-Lite | `--bus ahb` | `hclk, hresetn, haddr, hsel, htrans, hwrite, hwdata, hwstrb, hrdata, hready, hreadyout, hresp` |
| AXI4-Lite | `--bus axi` | `aclk, aresetn, awaddr/awvalid/awready, wdata/wstrb/wvalid/wready, bvalid/bready/bresp, araddr/arvalid/arready, rdata/rvalid/rready/rresp` |

### Register Core Interface Timing

| Operation | Cycle N | Cycle N+1 |
|-----------|---------|-----------|
| Read | `ren=1`, `addr` valid | `ready=1`, `rdata` valid |
| Write | `wen=1`, `wdata`+`wstrb`+`addr` valid | Complete (single cycle) |
| Simultaneous R/W | Supported (pseudo dual-port) | Read returns pre-write value |

## Excel Specification Format

Required columns:

| Column | Description |
|--------|-------------|
| Name | Register name |
| Offset | Byte offset (hex, e.g. `0x000`, `0x004`) |
| Field | Field name within the register |
| Bits | Bit position: `"0"` for single bit, `"3:1"` for range, integer for width from bit 0 |
| Access | `RW`, `RO`, `WO`, `W1C`, `W1S`, `W0C`, `RC`, `RS` |
| Reset | Reset value |

Optional columns: `Hardware Trigger` (`input`/`output`), `Side Effect`, `Interrupt` (`source`/`enable`)

## Output Formats

| File | Format | Description |
|------|--------|-------------|
| `{name}_regfile_core.v` | Verilog | Bus-agnostic register file core (always generated) |
| `{name}_apb_wrapper.v` | Verilog | APB4 protocol wrapper (`--bus apb`) |
| `{name}_ahb_wrapper.v` | Verilog | AHB-Lite protocol wrapper (`--bus ahb`) |
| `{name}_axi_wrapper.v` | Verilog | AXI4-Lite protocol wrapper (`--bus axi`) |
| `{name}_reg_block.sv` | SystemVerilog | UVM RAL model |
| `{name}.h` | C header | Register definitions and access macros |
| `{name}.json` | JSON | Machine-readable register map |
| `{name}.md` | Markdown | Human-readable register documentation |
| `{name}.html` | HTML | Styled register map with access type badges |

## Example Output

The `output/` directory contains a sample `chip_regs` register bank generated from `tests/sample_spec.xlsx`:

- **6 registers**: CTRL, STATUS, INT_EN, INT_STS, DMA_CTRL, ERR_STS
- **24 bytes** address space (32-bit data width)
- Demonstrates RW, RO, W1C, RC, RS access types
- Includes hardware interface ports (status inputs, control outputs)
- Includes interrupt source/enable pair (INT_STS.OVERRUN / INT_EN.DONE, TIMER) with `irq_o`

## CLI Reference

```
python main.py --input_excel <file> --output_dir <dir> [options]

Required:
  --input_excel FILE     Input .xlsx register specification
  --output_dir DIR       Output directory

Optional:
  --block_name NAME      Module/block name (default: reg_top)
  --base_address ADDR    Base address, e.g. 0x8000_0000 (default: 0x0)
  --data_width N         Data width: 8, 16, 32, or 64 (default: 32)
  --bus {none,apb,ahb,axi}  Bus protocol wrapper (default: none)
  --format FMTS          Comma-separated formats: rtl,uvm,c_header,json,html,markdown
  --rtl_only             Shorthand for --format rtl
  --uvm_only             Shorthand for --format uvm
  --template_excel       Generate blank Excel template and exit
  --dry_run              Parse and validate only; no file output
  --verbose              Enable debug logging
  --version              Show version
```

## Project Structure

```
Register/
├── src/
│   ├── models/          # Field, Register, RegisterBank data models
│   ├── parser/          # Excel parser (xlsx → RegisterBank)
│   ├── validators/      # 9 validation checks
│   ├── generators/      # RTL, APB/AHB/AXI wrappers, UVM, C header, JSON, Markdown, HTML
│   ├── templates/       # Jinja2 templates (regfile_core.v.j2, apb_wrapper.v.j2, etc.)
├── main.py              # Command-line interface
├── tests/               # Test suite (pytest, 90 tests)
├── output/              # Example generated output (chip_regs)
└── pyproject.toml
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## License

MIT
