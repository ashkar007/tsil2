# TSIL (Timeseries Intermediate Language) Agent Reference Card

Inject this document into the LLM system prompt or context window when asking an agent to generate TSIL scripts.

---

## Language Syntax & Grammar
*   **Style**: Python-like expressions.
*   **Variable Assignment**: `var = expression`
*   **Statement Separation**: Statements must end with a newline or semicolon `;` (e.g. `t1 = t("SPX"); e1 = e("3M")`).
*   **Comments**: Starts with `#`.
*   **Multi-line expressions**: Allowed; newlines are ignored inside open parentheses `()` or brackets `[]`.
*   **DO NOT IMPORT**: No Python libraries (e.g. `import math` or `import pandas`) are allowed. Only use native TSIL functions.

---

## Core Constructors & Syntax
| Object | Factory Syntax | Examples |
|---|---|---|
| **Ticker** | `t(symbol_or_list, [weighting_scheme_or_weights])` | `t("SPX")`<br>`t(["SPX", "SX5E"], WGT_EQ)`<br>`t(["SPX", "SX5E"], [0.3, 0.7])`<br>`t(["SPX", "SX5E"], WGT_VOL)` |
| **Expiry** | `e(expiry_str, [duration_str])` | `e("3M")` (Tenor)<br>`e("2026-12-17")` (ISO Date)<br>`e("DEC26")` (Month-Year)<br>`e("Z26")` (CME code)<br>`e("1Y", "6M")` (Forward) |
| **Strike** | `k(level, [strike_type])` | `k(7500)` (Absolute)<br>`k("100%")` (Forward Moneyness)<br>`k("95%S")` (Spot Moneyness)<br>`k("-25D")` (Delta)<br>`k(25, "dc")` (Call Delta) |

*Weighting Schemes*: `WGT_EQ` (equal), `WGT_VOL` (inverse volatility), `WGT_MOM` (momentum), `WGT_MCAP` (market capitalization).

---

## Metric Queries (Returns Timeseries)
Use the following functions to query financial timeseries data:
*   `SPOT(ticker)`: Closing spot price.
*   `FWD(ticker, expiry)`: Forward price.
*   `IV(ticker, expiry, strike, **kwargs)`: Implied Volatility.
*   `RZ(ticker, period_days, [model], **kwargs)`: Realized Volatility. Models: `"C2C"` (close-to-close), `"GK"` (Garman-Klass).
*   `GC(ticker, expiry)`: Gamma Carry (ATM Straddle theta cost).
*   `VC(ticker, expiry)`: Vanna Carry (25D Straddle theta cost).
*   `VGC(ticker, expiry)`: Volga Carry (10D Strangle theta cost).

---

## Math & Statistical Operations
Operations align element-wise by date index.
*   **Arithmetic**: `+`, `-`, `*`, `/`, `**`
*   **Comparisons (Returns 1.0 or 0.0 signals)**: `>`, `<`, `>=`, `<=`, `==`, `!=`
*   **Logical**: `and`, `or`, `not`
*   **Indexing & Slicing**:
    *   Lists: `lst[0]` (index), `lst[1:3]` (slice).
    *   Timeseries: `ts[0]` (returns float value at position 0), `ts[0:20]` (returns new Timeseries of first 20 elements), `ts[-10:]` (returns new Timeseries of last 10 elements).
    *   Timeseries Date Range: `ts["2025-01-01":"2025-01-10"]` (returns new Timeseries for the date range).
*   **Math Functions**:
    *   `sqrt(ts)`
    *   `diff(ts, periods)`
    *   `pct_change(ts, periods)`
    *   `corr(ts1, ts2, window)`
    *   `cov(ts1, ts2, window)`
    *   `std(ts, window)`
    *   `mean(ts, window)` / `ma(ts, window)` (moving average)
    *   `sharpe(ts, window)` (rolling Sharpe ratio)
    *   `sum(ts, window)`
    *   `min(ts, window)`
    *   `max(ts, window)`
    *   `drawdown(ts, window)` (rolling peak-to-trough drawdown)
    *   `mode(ts)` (global mode, returns scalar)
    *   `percentile(ts, q)` (global quantile for percentile `q` (0-100), returns scalar)

---

## Option Strategy Backtesting (`bt`)
*   **Sizing**: `notional(amount, type)`. Sizing types: `"notional"`, `"units"`, `"vega"`, `"gamma"`, `"theta"`.
*   **Instruments**:
    *   `CALL(ticker, expiry, strike, size)`
    *   `PUT(ticker, expiry, strike, size)`
    *   `SD(ticker, expiry, size)` (ATM Straddle)
    *   `RR(ticker, expiry, strike, size)` (Risk Reversal: Long Put / Short Call)
    *   `PS(ticker, expiry, delta, ratio, size)` (Put Spread)
    *   `CS(ticker, expiry, delta, ratio, size)` (Call Spread)
    *   `CCS(ticker, expiry, strike, size)` / `PCS(ticker, expiry, strike, size)` (Calendar spreads)
*   **Running Backtest**: `bt(instruments_or_list, sizing_obj, rebalancing_schedule)` (Schedules: `"weekly"`, `"daily"`, `"1W"`, etc.)
*   **Result Properties**: Returns a result object containing columns `PL`, `PLVega`, `PLCarry`, `PLOther`.
*   **Signal Application**: Multiply result by a boolean/signal timeseries: `res = bt(ptf, sz, "weekly") * sig`

---

## Reference Examples

### Example 1: Volatility Term Structure Slope
```python
sx5e = t("SX5E")
vol_1m = IV(sx5e, e("1M"), k("100%"))
vol_1y = IV(sx5e, e("1Y"), k("100%"))
term_structure_slope = vol_1y - vol_1m
```

### Example 2: Active Backtest Sized by Vega
```python
# 1. Underlying and portfolio definition
spx = t("SPX")
ptf = [SD(spx, e("3M"))]

# 2. Risk Sizing
sz = notional(500000, "vega")

# 3. Generate Trading Signal (Long ATM 3M straddle when 3M IV is above its 20-day moving average)
iv_3m = IV(spx, e("3M"), k("100%"))
sig = iv_3m > ma(iv_3m, 20)

# 4. Run active strategy backtest
res = bt(ptf, sz, "weekly") * sig
final_pl = res.PL
```
