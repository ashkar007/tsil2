import uuid
import pandas as pd
import numpy as np

# Weighting schemes constants
WGT_EQ = "WGT_EQ"
WGT_VOL = "WGT_VOL"
WGT_MOM = "WGT_MOM"
WGT_MCAP = "WGT_MCAP"

class Ticker:
    def __init__(self, symbols, weights=None):
        if isinstance(symbols, str):
            self.symbols = [symbols]
        elif isinstance(symbols, list):
            self.symbols = list(symbols)
        else:
            raise TypeError("Symbols must be a string or list of strings")
            
        if weights is None:
            self.weights = WGT_EQ
        elif isinstance(weights, str):
            if weights not in (WGT_EQ, WGT_VOL, WGT_MOM, WGT_MCAP):
                raise ValueError(f"Unknown weighting scheme: {weights}")
            self.weights = weights
        elif isinstance(weights, list):
            self.weights = [float(w) for w in weights]
            if len(self.weights) != len(self.symbols):
                raise ValueError("Length of weights must match length of symbols")
        else:
            raise TypeError("Weights must be a string (weighting scheme) or a list of numbers")

    def __repr__(self):
        if self.weights == WGT_EQ:
            return f"t({self.symbols})"
        else:
            return f"t({self.symbols}, {self.weights})"

    def __str__(self):
        return repr(self)


class Expiry:
    def __init__(self, expiry, duration=None):
        if not isinstance(expiry, str):
            raise TypeError("Expiry must be a string")
        self.expiry = expiry
        
        if duration is not None and not isinstance(duration, str):
            raise TypeError("Duration must be a string")
        self.duration = duration

    def __repr__(self):
        if self.duration is None:
            return f"e({repr(self.expiry)})"
        else:
            return f"e({repr(self.expiry)}, {repr(self.duration)})"

    def __str__(self):
        return repr(self)


class Strike:
    def __init__(self, level, strike_type=None):
        if not isinstance(level, (int, float, str)):
            raise TypeError("Strike level must be a number or a string")
        self.level = level
        
        if strike_type is not None:
            if not isinstance(strike_type, str):
                raise TypeError("Strike type must be a string")
            self.strike_type = strike_type.upper()
        else:
            # Infer strike type from level string if possible
            if isinstance(level, str):
                level_upper = level.upper()
                if level_upper.endswith("%S"):
                    self.strike_type = "%S"
                elif level_upper.endswith("%F") or level_upper.endswith("%"):
                    self.strike_type = "%"
                elif level_upper.endswith("DP"):
                    self.strike_type = "DP"
                elif level_upper.endswith("DC"):
                    self.strike_type = "DC"
                elif level_upper.endswith("D"):
                    self.strike_type = "D"
                elif level_upper.endswith("N"):
                    self.strike_type = "N"
                else:
                    self.strike_type = None
            else:
                self.strike_type = None

    def __repr__(self):
        if self.strike_type is None:
            return f"k({repr(self.level)})"
        else:
            return f"k({repr(self.level)}, {repr(self.strike_type)})"

    def __str__(self):
        return repr(self)


class Timeseries:
    def __init__(self, series, name=None, value_type=None, id=None):
        if not isinstance(series, pd.Series):
            raise TypeError("Timeseries must wrap a pandas.Series")
        self.series = series
        self.id = id or str(uuid.uuid4())
        self.name = name or series.name or "Timeseries"
        self.value_type = value_type or "price"

    def __repr__(self):
        return f"Timeseries(id={self.id}, name={self.name}, value_type={self.value_type}, len={len(self.series)})"

    def _op(self, other, op_func, op_name, reverse=False):
        if isinstance(other, Timeseries):
            other_series = other.series
            new_name = f"({self.name} {op_name} {other.name})" if not reverse else f"({other.name} {op_name} {self.name})"
            # Align value_type: if they are the same, keep it. Otherwise, defaults to "price"
            new_val_type = self.value_type if self.value_type == other.value_type else "price"
        else:
            other_series = other
            new_name = f"({self.name} {op_name} {other})" if not reverse else f"({other} {op_name} {self.name})"
            new_val_type = self.value_type
            
        res_series = op_func(self.series, other_series) if not reverse else op_func(other_series, self.series)
        return Timeseries(res_series, name=new_name, value_type=new_val_type)

    def _comp(self, other, op_func, op_name):
        if isinstance(other, Timeseries):
            other_series = other.series
            new_name = f"({self.name} {op_name} {other.name})"
        else:
            other_series = other
            new_name = f"({self.name} {op_name} {other})"
        
        # Convert boolean output to floats (1.0 or 0.0) as signal timeseries
        res_series = op_func(self.series, other_series).astype(float)
        return Timeseries(res_series, name=new_name, value_type="signal")

    def __add__(self, other): return self._op(other, lambda x, y: x + y, "+")
    def __radd__(self, other): return self._op(other, lambda x, y: x + y, "+", reverse=True)
    
    def __sub__(self, other): return self._op(other, lambda x, y: x - y, "-")
    def __rsub__(self, other): return self._op(other, lambda x, y: x - y, "-", reverse=True)
    
    def __mul__(self, other): return self._op(other, lambda x, y: x * y, "*")
    def __rmul__(self, other): return self._op(other, lambda x, y: x * y, "*", reverse=True)
    
    def __truediv__(self, other): return self._op(other, lambda x, y: x / y, "/")
    def __rtruediv__(self, other): return self._op(other, lambda x, y: x / y, "/", reverse=True)
    
    def __pow__(self, other): return self._op(other, lambda x, y: x ** y, "**")
    def __rpow__(self, other): return self._op(other, lambda x, y: x ** y, "**", reverse=True)

    def __gt__(self, other): return self._comp(other, lambda x, y: x > y, ">")
    def __lt__(self, other): return self._comp(other, lambda x, y: x < y, "<")
    def __ge__(self, other): return self._comp(other, lambda x, y: x >= y, ">=")
    def __le__(self, other): return self._comp(other, lambda x, y: x <= y, "<=")
    def __eq__(self, other): return self._comp(other, lambda x, y: x == y, "==")
    def __ne__(self, other): return self._comp(other, lambda x, y: x != y, "!=")

    def __neg__(self):
        return Timeseries(-self.series, name=f"-{self.name}", value_type=self.value_type)

    def __getitem__(self, key):
        if isinstance(key, slice):
            use_loc = False
            if key.start is not None and not isinstance(key.start, int):
                use_loc = True
            if key.stop is not None and not isinstance(key.stop, int):
                use_loc = True
            
            if use_loc:
                sliced_series = self.series.loc[key.start:key.stop]
            else:
                sliced_series = self.series.iloc[key.start:key.stop]
            
            start_str = str(key.start) if key.start is not None else ""
            stop_str = str(key.stop) if key.stop is not None else ""
            return Timeseries(sliced_series, name=f"{self.name}[{start_str}:{stop_str}]", value_type=self.value_type)
        else:
            if isinstance(key, int):
                return self.series.iloc[key]
            else:
                return self.series.loc[key]



class BacktestResult:
    def __init__(self, data):
        """
        data: dict of Timeseries objects or a pandas DataFrame where index is datetime and columns are metrics
        """
        if isinstance(data, dict):
            # Check keys
            for k in ["PL", "PLVega", "PLCarry", "PLOther"]:
                if k not in data:
                    # Initialize default empty timeseries or similar if missing
                    data[k] = Timeseries(pd.Series(dtype=float), name=k)
            self.data = data
        elif isinstance(data, pd.DataFrame):
            self.data = {}
            for col in ["PL", "PLVega", "PLCarry", "PLOther"]:
                if col in data.columns:
                    self.data[col] = Timeseries(data[col], name=col)
                else:
                    self.data[col] = Timeseries(pd.Series(0.0, index=data.index), name=col)
        else:
            raise TypeError("Data must be a dict of Timeseries or a pandas DataFrame")

    @property
    def PL(self): return self.data["PL"]
    @property
    def PLVega(self): return self.data["PLVega"]
    @property
    def PLCarry(self): return self.data["PLCarry"]
    @property
    def PLOther(self): return self.data["PLOther"]

    def __mul__(self, other):
        """
        Multiplication by a signal timeseries: res = bt(...) * sig
        """
        if isinstance(other, Timeseries):
            new_data = {}
            for col, ts in self.data.items():
                # Align using pandas series multiplication
                new_data[col] = ts * other
            return BacktestResult(new_data)
        elif isinstance(other, (int, float)):
            new_data = {}
            for col, ts in self.data.items():
                new_data[col] = ts * other
            return BacktestResult(new_data)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __repr__(self):
        return f"BacktestResult(PL={len(self.PL.series)} points)"
