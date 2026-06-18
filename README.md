# Timeseries Intermediate Language (TSIL)

**TSIL** is a domain-specific language (DSL) designed for financial timeseries analytics. In derivatives trading, the timeseries may be implied volatility, realized volatility, spot prices, percentage changes, yields, borrows, etc. TSIL provides a standardized, portable specification for expressing complex operations on timeseries (e.g., `spx = SPOT(t("SPX")); annualized_vol = RZ(t("SPX"), 20) * sqrt(252)`), defining option portfolios, and backtesting active options strategies.

This repository contains the complete compiler toolchain and interpreter for TSIL written in Python, along with a deterministic mock market data provider and options backtesting engine.

---

## Key Features

- **Intuitive Python-Like Syntax**: Write complex financial calculations and options strategies in a highly readable format.
- **Timeseries Operator Overloading**: Perform element-wise arithmetic (`+`, `-`, `*`, `/`, `**`) and logical comparisons on timeseries with automatic calendar date-index alignment.
- **Flexible Indexing & Slicing**: Index and slice both list structures and timeseries objects using standard bracket syntax:
  - Position-based: `spx[0:20]` (first 20 elements) or `spx[-10:]` (last 10 elements).
  - Date-based: `spx["2025-01-01":"2025-01-10"]` (inclusive date range).
- **Abstract Syntax Tree (AST) Serialization**: Programmatically compile TSIL source code to a JSON-serializable dictionary format, allowing scripts to be stored, shared, and reloaded easily.
- **Integrated Options Backtesting (`bt`)**: Sized by Notional, Vega, Gamma, or Theta, rebalanced on custom tenors (e.g. weekly/daily), and scaled by active signal timeseries.

---

## Directory Structure

```text
tsil2/
├── tsil/                   # Core Interpreter Package
│   ├── lexer.py            # Tokenizer (handles date/datetime, strings, operators, etc.)
│   ├── parser.py           # AST Node definitions and Recursive Descent Parser
│   ├── interpreter.py      # AST Evaluation Engine
│   ├── types.py            # Custom classes (Ticker, Expiry, Strike, Timeseries, BacktestResult)
│   ├── functions.py        # Math/Timeseries built-ins and Options constructors
│   └── mock_provider.py    # Deterministic mock market data generator
├── tests/
│   └── test_interpreter.py # Complete unit test suite (pytest)
├── docs/                   # Documentation
│   ├── user_manual.md      # Detailed TSIL syntax, functions, and backtest guide
│   ├── agent_reference.md  # Reference sheet designed for LLM prompt context
│   └── ast_examples.md     # Reference examples of serialized JSON ASTs
├── requirements.txt        # Package dependencies (pandas, numpy, pytest)
└── README.md               # Project overview
```

---

## Getting Started

### 1. Installation

Set up a virtual environment and install dependencies:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1   # Windows PowerShell
source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Test Suite

Execute the tests to verify the interpreter functionality:

```powershell
python -m pytest
```

---

## Quick Usage & Examples

You can execute TSIL scripts directly in Python using the `evaluate` function.

### Example 1: Basic Math & Slicing
```python
from tsil.interpreter import evaluate

code = """
lst = [10, 20, 30, 40, 50]
x_sub = lst[1:4]      # [20, 30, 40]

spx = t("SPX")
spot_series = SPOT(spx)
top20 = spot_series[0:20]   # First 20 business days of spot prices
"""

res, env = evaluate(code)
print(env['x_sub'])  # [20, 30, 40]
print(env['top20'])  # Timeseries(name=SPOT_T(['SPX'])[0:20], len=20)
```

### Example 2: Volatility Term Structure Slope
```python
code = """
sx5e = t("SX5E")
vol_1m = IV(sx5e, e("1M"), k("100%"))  # 1-Month ATM Implied Vol
vol_1y = IV(sx5e, e("1Y"), k("100%"))  # 1-Year ATM Implied Vol
vol_slope = vol_1y - vol_1m
"""

res, env = evaluate(code)
print(env['vol_slope'])  # Timeseries representing the slope
```

### Example 3: Sized Straddle Options Backtest
```python
code = """
spx = t("SPX")
ptf = [SD(spx, e("3M"))]                 # 3-Month ATM Straddle
sz = notional(5000000, "vega")           # Vega risk-sized notional

# Generate a signal: active when 3M ATM IV exceeds its 20-day moving average
iv_3m = IV(spx, e("3M"), k("100%"))
sig = iv_3m > ma(iv_3m, 20)

# Run backtest scaled by signal
res = bt(ptf, sz, "weekly") * sig
final_pl = res.PL
"""

res, env = evaluate(code)
print(env['final_pl'])  # Timeseries representing total strategy P&L
```

---

## AST Serialization

You can also serialize and deserialize scripts programmatically:

```python
from tsil.interpreter import ast_to_dict, evaluate_ast

# 1. Compile script to JSON AST dictionary
script = "val = SPOT(t('SPX')) * 2.0"
ast_json = ast_to_dict(script)

# 2. Evaluate directly from AST JSON dictionary
res, env = evaluate_ast(ast_json)
print(env['val'])
```

---

## Documentation

For deep technical specifications, refer to:
- [Language Specification](file:///c:/code/git/tsil2/language_spec,.md) — Formal grammar details.
- [User Manual](file:///c:/code/git/tsil2/docs/user_manual.md) — Comprehensive guide to TSIL types, operations, and options strategies.
- [Agent Reference Card](file:///c:/code/git/tsil2/docs/agent_reference.md) — Reference card for prompt engineering when using LLMs to write TSIL.
- [AST Examples](file:///c:/code/git/tsil2/docs/ast_examples.md) — In-depth JSON serialization references.
