import math
import hashlib
import numpy as np
import pandas as pd

from .types import Timeseries, BacktestResult, Ticker, Expiry, Strike, WGT_EQ
from .mock_provider import generate_mock_ts, get_date_index

# Ticker, Expiry, Strike Factories
def t(ticker_list, weights=None):
    return Ticker(ticker_list, weights)

def e(expiry, duration=None):
    return Expiry(expiry, duration)

def k(level, strike_type=None):
    return Strike(level, strike_type)

# Metrics
def IV(ticker, expiry, strike, **kwargs):
    return generate_mock_ts("IV", ticker, expiry, strike)

def RZ(ticker, period, model=None, **kwargs):
    # Map period to a pseudo strike representation for the mock provider
    s_period = Strike(period)
    e_model = Expiry(model) if model else None
    return generate_mock_ts("RZ", ticker, e_model, s_period)

def SPOT(ticker):
    return generate_mock_ts("SPOT", ticker)

def FWD(ticker, expiry):
    return generate_mock_ts("FWD", ticker, expiry)

def GC(ticker, expiry):
    return generate_mock_ts("GC", ticker, expiry)

def VC(ticker, expiry):
    return generate_mock_ts("VC", ticker, expiry)

def VGC(ticker, expiry):
    return generate_mock_ts("VGC", ticker, expiry)

# Math & Timeseries Operations
def sqrt(ts):
    if isinstance(ts, Timeseries):
        return Timeseries(np.sqrt(ts.series), name=f"sqrt({ts.name})", value_type=ts.value_type)
    return math.sqrt(ts)

def diff(ts, periods=1):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.diff(periods), name=f"diff({ts.name}, {periods})", value_type=ts.value_type)
    raise TypeError("diff operates on a Timeseries")

def pct_change(ts, periods=1):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.pct_change(periods), name=f"pct_change({ts.name}, {periods})", value_type="pct")
    raise TypeError("pct_change operates on a Timeseries")

def corr(ts, ts2, window):
    if isinstance(ts, Timeseries) and isinstance(ts2, Timeseries):
        res = ts.series.rolling(window).corr(ts2.series)
        return Timeseries(res, name=f"corr({ts.name}, {ts2.name}, {window})", value_type="pct")
    raise TypeError("corr operates on two Timeseries")

def cov(ts, ts2, window):
    if isinstance(ts, Timeseries) and isinstance(ts2, Timeseries):
        res = ts.series.rolling(window).cov(ts2.series)
        return Timeseries(res, name=f"cov({ts.name}, {ts2.name}, {window})", value_type="price")
    raise TypeError("cov operates on two Timeseries")

def std(ts, window):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.rolling(window).std(), name=f"std({ts.name}, {window})", value_type=ts.value_type)
    raise TypeError("std operates on a Timeseries")

def mean(ts, window):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.rolling(window).mean(), name=f"mean({ts.name}, {window})", value_type=ts.value_type)
    raise TypeError("mean operates on a Timeseries")

def ma(ts, window):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.rolling(window).mean(), name=f"ma({ts.name}, {window})", value_type=ts.value_type)
    raise TypeError("ma operates on a Timeseries")

def sharpe(ts, window):
    if isinstance(ts, Timeseries):
        r_mean = ts.series.rolling(window).mean()
        r_std = ts.series.rolling(window).std()
        # Handle zero std division safely
        res = r_mean / r_std.replace(0, np.nan)
        return Timeseries(res, name=f"sharpe({ts.name}, {window})", value_type="ratio")
    raise TypeError("sharpe operates on a Timeseries")

def sum_ts(ts, window):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.rolling(window).sum(), name=f"sum({ts.name}, {window})", value_type=ts.value_type)
    raise TypeError("sum operates on a Timeseries")

def min_ts(ts, window):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.rolling(window).min(), name=f"min({ts.name}, {window})", value_type=ts.value_type)
    raise TypeError("min operates on a Timeseries")

def max_ts(ts, window):
    if isinstance(ts, Timeseries):
        return Timeseries(ts.series.rolling(window).max(), name=f"max({ts.name}, {window})", value_type=ts.value_type)
    raise TypeError("max operates on a Timeseries")

def mode(ts):
    if isinstance(ts, Timeseries):
        m = ts.series.mode()
        return m.iloc[0] if not m.empty else np.nan
    raise TypeError("mode operates on a Timeseries")

def percentile(ts, q):
    if isinstance(ts, Timeseries):
        val = q / 100.0 if q > 1.0 else q
        return ts.series.quantile(val)
    raise TypeError("percentile operates on a Timeseries")

def drawdown(ts, window):
    if isinstance(ts, Timeseries):
        peaks = ts.series.rolling(window, min_periods=1).max()
        dd = (ts.series - peaks) / peaks
        return Timeseries(dd, name=f"drawdown({ts.name}, {window})", value_type="pct")
    raise TypeError("drawdown operates on a Timeseries")

# Backtesting Instruments
def CALL(ticker, expiry, strike, size=1.0):
    return {"type": "CALL", "ticker": ticker, "expiry": expiry, "strike": strike, "size": size}

def PUT(ticker, expiry, strike, size=1.0):
    return {"type": "PUT", "ticker": ticker, "expiry": expiry, "strike": strike, "size": size}

def SD(ticker, expiry, size=1.0):
    return {"type": "SD", "ticker": ticker, "expiry": expiry, "size": size}

def RR(ticker, expiry, strike, size=1.0):
    return {"type": "RR", "ticker": ticker, "expiry": expiry, "strike": strike, "size": size}

def PS(ticker, expiry, delta, ratio, size=1.0):
    return {"type": "PS", "ticker": ticker, "expiry": expiry, "delta": delta, "ratio": ratio, "size": size}

def CS(ticker, expiry, delta, ratio, size=1.0):
    return {"type": "CS", "ticker": ticker, "expiry": expiry, "delta": delta, "ratio": ratio, "size": size}

def CCS(ticker, expiry, strike, size=1.0):
    return {"type": "CCS", "ticker": ticker, "expiry": expiry, "strike": strike, "size": size}

def PCS(ticker, expiry, strike, size=1.0):
    return {"type": "PCS", "ticker": ticker, "expiry": expiry, "strike": strike, "size": size}

def notional(amount, size_type):
    return {"amount": amount, "type": size_type}

# Backtesting Engine
def bt(ptf, sz, rebalancing):
    # Handle single instrument vs list of instruments
    if not isinstance(ptf, list):
        portfolio_list = [ptf]
    else:
        portfolio_list = ptf
        
    ptf_repr = str(portfolio_list)
    sz_repr = str(sz)
    rebal_repr = str(rebalancing)
    
    seed_str = f"bt:{ptf_repr}:{sz_repr}:{rebal_repr}"
    h = hashlib.md5(seed_str.encode('utf-8')).hexdigest()
    seed = int(h[:8], 16)
    
    rng = np.random.default_rng(seed)
    idx = get_date_index()
    n = len(idx)
    
    # Scale based on sizing amount
    size_amt = 1000000.0  # default baseline
    if isinstance(sz, dict) and "amount" in sz:
        size_amt = float(sz["amount"])
    
    # Generate PL components
    # Positive drift random walk
    steps = rng.normal(0.0004, 0.012, n)
    pl_path = np.cumsum(steps) * size_amt
    
    # Vega PL: drifts but has noise
    steps_vega = rng.normal(-0.0001, 0.007, n)
    pl_vega = np.cumsum(steps_vega) * size_amt
    
    # Carry PL: steady positive theta capture
    pl_carry = np.linspace(0, 0.08 * size_amt, n) + np.cumsum(rng.normal(0, 0.0005 * size_amt, n))
    
    # Other PL: residual
    pl_other = pl_path - pl_vega - pl_carry
    
    pl_ts = Timeseries(pd.Series(pl_path, index=idx), name="PL", value_type="price")
    pl_vega_ts = Timeseries(pd.Series(pl_vega, index=idx), name="PLVega", value_type="price")
    pl_carry_ts = Timeseries(pd.Series(pl_carry, index=idx), name="PLCarry", value_type="price")
    pl_other_ts = Timeseries(pd.Series(pl_other, index=idx), name="PLOther", value_type="price")
    
    return BacktestResult({
        "PL": pl_ts,
        "PLVega": pl_vega_ts,
        "PLCarry": pl_carry_ts,
        "PLOther": pl_other_ts
    })

# Expose standard mapping for interpreter
FUNCTION_MAP = {
    't': t,
    'e': e,
    'k': k,
    'IV': IV,
    'RZ': RZ,
    'SPOT': SPOT,
    'FWD': FWD,
    'GC': GC,
    'VC': VC,
    'VGC': VGC,
    'sqrt': sqrt,
    'diff': diff,
    'pct_change': pct_change,
    'corr': corr,
    'cov': cov,
    'std': std,
    'mean': mean,
    'ma': ma,
    'sharpe': sharpe,
    'sum': sum_ts,
    'min': min_ts,
    'max': max_ts,
    'mode': mode,
    'percentile': percentile,
    'drawdown': drawdown,
    'CALL': CALL,
    'PUT': PUT,
    'SD': SD,
    'RR': RR,
    'PS': PS,
    'CS': CS,
    'CCS': CCS,
    'PCS': PCS,
    'notional': notional,
    'bt': bt,
    # Expose weighting schemes as values in env
    'WGT_EQ': WGT_EQ,
    'WGT_VOL': "WGT_VOL",
    'WGT_MOM': "WGT_MOM",
    'WGT_MCAP': "WGT_MCAP",
}
