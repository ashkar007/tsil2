import hashlib
import pandas as pd
import numpy as np

def get_seed(metric_name, ticker, expiry=None, strike=None):
    ticker_str = str(ticker) if ticker else ""
    expiry_str = str(expiry) if expiry else ""
    strike_str = str(strike) if strike else ""
    seed_str = f"{metric_name}:{ticker_str}:{expiry_str}:{strike_str}"
    h = hashlib.md5(seed_str.encode('utf-8')).hexdigest()
    return int(h[:8], 16)

def get_date_index(start="2025-01-01", end="2026-06-18"):
    return pd.bdate_range(start=start, end=end)

def generate_mock_ts(metric_name, ticker, expiry=None, strike=None):
    from .types import Timeseries
    
    seed = get_seed(metric_name, ticker, expiry, strike)
    rng = np.random.default_rng(seed)
    idx = get_date_index()
    n = len(idx)

    # Determine value type
    if metric_name in ('IV', 'RZ'):
        val_type = "vol"
    elif metric_name in ('GC', 'VC', 'VGC'):
        val_type = "pct"
    else:
        val_type = "price"

    # Default parameters for path generation
    base_val = 100.0
    vol = 0.01

    ticker_str = str(ticker).upper()

    if metric_name == "SPOT":
        if "SPX" in ticker_str:
            base_val = 5000.0
        elif "SX5E" in ticker_str:
            base_val = 4000.0
        vol = 0.007
        steps = rng.normal(0, vol, n)
        path = np.exp(np.cumsum(steps)) * base_val
        
    elif metric_name == "FWD":
        if "SPX" in ticker_str:
            base_val = 5050.0
        elif "SX5E" in ticker_str:
            base_val = 4040.0
        vol = 0.007
        steps = rng.normal(0, vol, n)
        path = np.exp(np.cumsum(steps)) * base_val
        
    elif metric_name == "IV":
        # Simulate OTM volatility skew / smile and tenor term structure
        # Baseline IV
        base_iv = 0.16
        if "SPX" in ticker_str:
            base_iv = 0.14
        elif "SX5E" in ticker_str:
            base_iv = 0.18
        
        # Expiry term structure adjustment
        expiry_str = str(expiry).upper()
        if "1M" in expiry_str:
            base_iv -= 0.02
        elif "1Y" in expiry_str or "DEC26" in expiry_str or "Z26" in expiry_str:
            base_iv += 0.02
        
        # Strike skew adjustment (OTM puts have higher vol, OTM calls lower, smile shape)
        strike_str = str(strike).upper()
        skew = 0.0
        if "90%" in strike_str or "-25D" in strike_str or "25DP" in strike_str:
            skew = 0.04  # Puts
        elif "110%" in strike_str or "25DC" in strike_str or "25D" in strike_str:
            skew = -0.02 # Calls
        elif "100%" in strike_str:
            skew = 0.0
            
        final_base = base_iv + skew
        steps = rng.normal(0, 0.01, n)
        # Random walk for volatility
        path = final_base + np.cumsum(steps) * 0.005
        path = np.clip(path, 0.05, 0.80)
        
    elif metric_name == "RZ":
        base_rz = 0.15
        if "SPX" in ticker_str:
            base_rz = 0.13
        steps = rng.normal(0, 0.015, n)
        path = base_rz + np.cumsum(steps) * 0.006
        path = np.clip(path, 0.04, 0.75)
        
    elif metric_name in ('GC', 'VC', 'VGC'):
        # Carry is around 0.005 (0.5%), fluctuating
        base_carry = 0.005 if metric_name == "GC" else 0.003
        steps = rng.normal(0, 0.02, n)
        path = base_carry + np.cumsum(steps) * 0.001
        
    else:
        # Default fallback
        steps = rng.normal(0, vol, n)
        path = np.exp(np.cumsum(steps)) * base_val

    series = pd.Series(path, index=idx)
    
    # Formulate name
    name_parts = [metric_name, ticker_str.replace(" ", "")]
    if expiry:
        name_parts.append(str(expiry).replace(" ", ""))
    if strike:
        name_parts.append(str(strike).replace(" ", ""))
    
    ts_name = "_".join(name_parts)
    return Timeseries(series, name=ts_name, value_type=val_type)
