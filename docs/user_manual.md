# Timeseries Intermediate Language (TSIL) User Manual

**TSIL** is a domain-specific language (DSL) designed for financial timeseries analytics. It provides a standardized and portable way to specify operations on timeseries (e.g., spot prices, implied/realized volatilities, Greeks, cost of carry) and test option trading strategies.

---

## 1. Syntax & Language Features

TSIL syntax is designed to be highly readable, similar to Python.

### Variables & Assignment
Variables are dynamically typed. Assign values using `=`:
```python
ticker_spx = t("SPX")
```

### Comments
Any text following `#` on a line is treated as a comment and ignored:
```python
# This is a comment
x = 10  # inline comment
```

### Statement Separators & Semicolons
Statements are separated by newlines or semicolons `;`. You can write multiple statements on one line:
```python
t1 = t("SPX"); e1 = e("3M"); k1 = k("100%")
```

### Multi-line Expressions
Expressions can span multiple lines. The lexer tracks parenthetical/bracket depth `()`, `[]` and ignores newlines when they are inside open parentheticals:
```python
iv_spread = IV(t("SX5E"), 
               e("2Y"), 
               k("100%")) - IV(t("SX5E"), 
                               e("1Y"), 
                               k("100%"))
```

---

## 2. Fundamental Data Types

| Type | Format / Value | Examples |
|---|---|---|
| **Boolean** | `True` or `False` (case-sensitive) | `True`, `False` |
| **String** | Text enclosed in double or single quotes | `"SPX"`, `'3M'`, `"100%"` |
| **Number** | Integers and floating-point values | `100`, `25.5`, `0.75` |
| **Date** | ISO 8601 calendar date (`YYYY-MM-DD`) | `2026-12-17`, `2025-06-01` |
| **Datetime** | ISO 8601 date and time (`YYYY-MM-DDTHH:mm:ss`) | `2026-12-17T01:00:00` |
| **List** | Ordered comma-separated collection in square brackets | `["SPX", "SX5E"]`, `[0.3, 0.7]` |

---

## 3. Domain Object Constructors

### Ticker: `t(ticker_list, [weights])`
Creates a Ticker object representing single ticker symbols or weighted baskets.
*   **`ticker_list`**: String or List of Strings.
*   **`weights`** (optional): A list of numeric weights, or a weighting scheme:
    *   `WGT_EQ` - Equal-weighted (default)
    *   `WGT_VOL` - Volatility-weighted
    *   `WGT_MOM` - Momentum-weighted
    *   `WGT_MCAP` - Market-cap weighted

```python
spx = t("SPX")
eq_basket = t(["SPX", "SX5E"], WGT_EQ)
weighted_basket = t(["SPX", "SX5E"], [0.3, 0.7])
```

### Expiry: `e(expiry, [duration])`
Creates an Expiry object specifying fixed dates or relative tenors.
*   **`expiry`**: String representing fixed calendar date or tenor.
    *   *ISO Date*: `"2026-12-17"`
    *   *Month-Year*: `"DEC2026"`, `"DEC26"`
    *   *Listed CME Month Code*: `"Z26"` (Z = December)
    *   *Tenor*: `"3M"`, `"1Y"`, `"1W"`, `"2D"` (Business Days)
*   **`duration`** (optional): String tenor representing forward duration for forward-rolling metrics.

```python
fixed_expiry = e("2026-12-17")
constant_tenor = e("3M")
fwd_tenor = e("1Y", "6M")  # 1-year expiry starting in 6 months
```

### Strike: `k(level, [strike_type])`
Creates a Strike object representing absolute or relative options strikes.
*   **`level`**: Numeric level (for absolute strikes) or String (implicitly containing strike types).
*   **`strike_type`** (optional): String representation of option moneyness/delta format.
    *   `%` or `%F` - Forward Moneyness (e.g. `100%` is ATM)
    *   `%S` - Spot Moneyness (e.g. `95%S`)
    *   `D` - Delta (positive for Call, negative for Put)
    *   `DP` - Put Delta
    *   `DC` - Call Delta
    *   `N` - Normalized Strike

```python
abs_strike = k(7500)
atm_moneyness = k("100%")
delta_put = k("-25D")
explicit_delta_call = k(25, "DC")
```

---

## 4. Timeseries Metrics

Metrics represent queries producing timeseries objects. In Python, these timeseries wrap a `pandas.Series` indexed by business days.

| Metric | Syntax | Description |
|---|---|---|
| **Implied Volatility (IV)** | `IV(ticker, expiry, strike, **kwargs)` | Timeseries of implied volatility |
| **Realized Volatility (RZ)** | `RZ(ticker, period, [model], **kwargs)` | Timeseries of historical realized volatility over `period` days |
| **Spot Price (SPOT)** | `SPOT(ticker)` | Closing spot timeseries of the underlying |
| **Forward Price (FWD)** | `FWD(ticker, expiry)` | Forward price timeseries of the underlying |
| **Gamma Carry (GC)** | `GC(ticker, expiry)` | Daily theta cost adjusted by vol roll for ATM straddles |
| **Vanna Carry (VC)** | `VC(ticker, expiry)` | Daily theta cost adjusted by vol roll for 25D straddles (flat gamma) |
| **Volga Carry (VGC)** | `VGC(ticker, expiry)` | Daily theta cost adjusted by vol roll for 10D strangles (flat gamma) |

---

## 5. Operations & Functions

### Arithmetic Operators
All arithmetic operators operate element-wise on `Timeseries` objects, aligning them automatically by date index.

*   `+` (Addition)
*   `-` (Subtraction)
*   `*` (Multiplication)
*   `/` (Division)
*   `**` (Power)

### Comparisons & Logical Operators
Comparisons on a timeseries return a **signal timeseries** consisting of `1.0` (condition met) and `0.0` (condition not met).
*   `<`, `>`, `<=`, `>=`, `==`, `!=`
*   `and`, `or`, `not`

```python
# Signal when 1-month IV is higher than 3-month IV
sig = IV(t1, e("1M"), k("100%")) > IV(t1, e("3M"), k("100%"))
```

### Indexing & Slicing
Lists and Timeseries objects support indexing and slicing using `[...]` syntax.

#### List Indexing & Slicing
- `lst[index]`: Retrieves the item at the specified integer index.
- `lst[start:end]`: Slices the list from `start` index to `end` index (non-inclusive).
- Omitted start or end values (e.g. `lst[:3]`, `lst[2:]`) are supported.

```python
lst = [10, 20, 30, 40]
val = lst[0]       # 10
sub = lst[1:3]     # [20, 30]
```

#### Timeseries Indexing & Slicing
- **Positional Slicing/Indexing**: Slice or retrieve elements chronologically by position (integer index):
  - `ts[index]`: Returns the single float value at that position.
  - `ts[start:end]`: Returns a new `Timeseries` containing elements within the range.
  - `ts[-10:]`: Returns a new `Timeseries` with the last 10 elements.
- **Date Label Slicing**: Slice by datetime range (string date labels):
  - `ts["2025-01-01":"2025-01-10"]`: Returns a new `Timeseries` containing values for the business days within that period.

```python
spx_spot = SPOT(t("SPX"))
first_val = spx_spot[0]                      # Retrieves first float element
top20 = spx_spot[0:20]                        # First 20 elements (Timeseries)
jan_slice = spx_spot["2025-01-01":"2025-01-10"] # Date-range slice (Timeseries)
```

### Mathematical & Statistical Functions

| Function | Description |
|---|---|
| `sqrt(ts)` | Element-wise square root |
| `diff(ts, [periods=1])` | Historical change in timeseries levels |
| `pct_change(ts, [periods=1])` | Historical percentage change in timeseries levels |
| `corr(ts1, ts2, window)` | Rolling correlation between two timeseries |
| `cov(ts1, ts2, window)` | Rolling covariance between two timeseries |
| `std(ts, window)` | Rolling standard deviation |
| `mean(ts, window)` | Rolling average (mean) |
| `ma(ts, window)` | Moving average (equivalent to rolling mean) |
| `sharpe(ts, window)` | Rolling Sharpe ratio (mean / std) |
| `sum(ts, window)` | Rolling summation |
| `min(ts, window)` | Rolling minimum |
| `max(ts, window)` | Rolling maximum |
| `mode(ts)` | Statistical mode over the entire series |
| `percentile(ts, q)` | Global quantile at percentile `q` (0 to 100 or 0 to 1) |
| `drawdown(ts, window)` | Rolling peak-to-trough drawdown |

---

## 6. Options Strategy Backtesting

TSIL supports defining option portfolios and backtesting their historical returns using the `bt(...)` engine.

### Instruments
Create option instruments using the constructors below:
*   `CALL(ticker, expiry, strike, size)`: Vanilla Call option
*   `PUT(ticker, expiry, strike, size)`: Vanilla Put option
*   `SD(ticker, expiry, size)`: ATM-forward straddle
*   `RR(ticker, expiry, strike, size)`: Risk Reversal (long put, short call)
*   `PS(ticker, expiry, delta, ratio, size)`: Put Spread
*   `CS(ticker, expiry, delta, ratio, size)`: Call Spread
*   `CCS(ticker, expiry, strike, size)`: Call Calendar Spread
*   `PCS(ticker, expiry, strike, size)`: Put Calendar Spread

### Sizing
Define strategy size using the `notional(amount, size_type)` helper.
*   **`size_type`**: `"notional"`, `"units"`, `"vega"`, `"gamma"`, `"theta"`

### Executing Backtests: `bt(portfolio, sizing, rebalancing)`
Executes the backtest. Returns a `BacktestResult` object containing historical performance.
*   **`portfolio`**: An instrument or a List of instruments.
*   **`sizing`**: Sizing configuration returned by `notional(...)`.
*   **`rebalancing`**: Rebalancing schedule string (e.g. `"weekly"`, `"daily"`, `"1W"`).

### Backtest Result Operations
The `BacktestResult` contains four property columns (each is a `Timeseries`):
*   `PL`: Total Profit/Loss
*   `PLVega`: Vega component of Profit/Loss
*   `PLCarry`: Carry (theta/roll) component of Profit/Loss
*   `PLOther`: Other/residual Profit/Loss

You can multiply a `BacktestResult` by a signal `Timeseries` to simulate active execution (scaling returns):
```python
# Backtest a straddle, active only when signal is 1
ptf = [SD(t("SPX"), e("3M"))]
sz = notional(5000000, "gamma")
res = bt(ptf, sz, "weekly") * sig
```

---

## 7. AST Serialization & Programmatic Execution

TSIL includes native support for compiling script source code to JSON ASTs, allowing scripts to be stored in databases, edited visually, and executed. For concrete representations of serialized AST structures, refer to [ast_examples.md](file:///c:/code/git/tsil2/docs/ast_examples.md).

### Parsing Script to Dictionary AST
```python
from tsil.interpreter import ast_to_dict

script = "x = SPOT(t('SPX')) * 2.0"
ast_json = ast_to_dict(script)
# ast_json is a JSON-serializable Python dictionary
```

### Executing Dictionary AST
```python
from tsil.interpreter import evaluate_ast

# Evaluate directly from the dictionary AST
res, env = evaluate_ast(ast_json)
print(env['x'])  # Outputs final Timeseries variable
```
