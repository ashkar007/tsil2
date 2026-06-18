import pytest
import pandas as pd
import numpy as np

from tsil.lexer import tokenize
from tsil.parser import Parser, ASTNode
from tsil.interpreter import evaluate, ast_to_dict, evaluate_ast
from tsil.types import Ticker, Expiry, Strike, Timeseries, BacktestResult, WGT_EQ, WGT_VOL

def test_lexer():
    # Test dates, datetimes, numbers, names, strings, symbols, semicolons
    code = 't1 = t("SPX"); e1 = e("3M"); k1 = k(100.5, "DP")\nx = 2026-12-17\ny = 2026-12-17T01:00:00'
    tokens = tokenize(code)
    
    assert tokens[0].type == 'NAME'
    assert tokens[0].value == 't1'
    assert tokens[1].type == 'ASSIGN'
    assert tokens[2].type == 'NAME'
    assert tokens[2].value == 't'
    assert tokens[3].type == 'LPAREN'
    assert tokens[4].type == 'STRING'
    assert tokens[4].value == 'SPX'
    assert tokens[5].type == 'RPAREN'
    
    # Check semicolon
    assert tokens[6].type == 'SEMICOLON'
    
    # Check date
    date_toks = [t for t in tokens if t.type == 'DATE']
    assert len(date_toks) == 1
    assert date_toks[0].value == '2026-12-17'
    
    # Check datetime
    dt_toks = [t for t in tokens if t.type == 'DATETIME']
    assert len(dt_toks) == 1
    assert dt_toks[0].value == '2026-12-17T01:00:00'


def test_lexer_multiline():
    # Newlines inside parenthesis should be ignored
    code = 'res = IV(\n  t("SPX"),\n  e("3M"),\n  k("100%")\n)'
    tokens = tokenize(code)
    # Check that there are no NEWLINE tokens inside the CallNode arguments list
    newline_types = [t.type for t in tokens]
    # The final newline will be added at EOF
    assert newline_types.count('NEWLINE') == 1
    # Check shape
    assert tokens[-4].type == 'STRING'
    assert tokens[-4].value == '100%'


def test_parser_and_serialization():
    code = 'spx = t(["SPX", "SX5E"], [0.3, 0.7]); iv = IV(spx, e("3M"), k("100%"))'
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Check ProgramNode structure
    assert len(ast.statements) == 2
    assert ast.statements[0].name == 'spx'
    assert ast.statements[1].name == 'iv'
    
    # Check CallNode keyword and positional arguments
    t_call = ast.statements[0].value
    assert t_call.func_name == 't'
    assert len(t_call.args) == 2
    assert t_call.args[0].elements[0].value == 'SPX'
    
    # Test serialization to dict
    ast_dict = ast.to_dict()
    assert ast_dict['type'] == 'ProgramNode'
    assert len(ast_dict['statements']) == 2
    
    # Test deserialization from dict
    ast_reconstructed = ASTNode.from_dict(ast_dict)
    assert repr(ast) == repr(ast_reconstructed)


def test_interpreter_basics():
    # Simple arithmetic and variable binding
    code = 'x = 10\ny = x * 2.5 + 5\nz = y > 20'
    res, env = evaluate(code)
    
    assert env['x'] == 10
    assert env['y'] == 30.0
    assert env['z'] is True


def test_custom_types():
    # Ticker
    t1 = Ticker("SPX")
    assert t1.symbols == ["SPX"]
    assert t1.weights == WGT_EQ
    
    t2 = Ticker(["SPX", "SX5E"], WGT_VOL)
    assert t2.symbols == ["SPX", "SX5E"]
    assert t2.weights == WGT_VOL
    
    t3 = Ticker(["SPX", "SX5E"], [0.3, 0.7])
    assert t3.weights == [0.3, 0.7]
    
    # Expiry
    e1 = Expiry("3M")
    assert e1.expiry == "3M"
    assert e1.duration is None
    
    e2 = Expiry("1Y", "6M")
    assert e2.expiry == "1Y"
    assert e2.duration == "6M"
    
    # Strike
    k1 = Strike(7500)
    assert k1.level == 7500
    assert k1.strike_type is None
    
    k2 = Strike("25DP")
    assert k2.strike_type == "DP"
    
    k3 = Strike(25, "DP")
    assert k3.level == 25
    assert k3.strike_type == "DP"


def test_timeseries_operations():
    # Create two custom Timeseries
    idx = pd.bdate_range(start="2025-01-01", end="2025-01-05") # 3 business days: Jan 1, Jan 2, Jan 3
    # Wait, Jan 1, 2025 is a Wednesday. Jan 2 is Thu, Jan 3 is Fri.
    s1 = pd.Series([10.0, 20.0, 30.0], index=idx[:3])
    s2 = pd.Series([2.0, 4.0, 6.0], index=idx[:3])
    
    ts1 = Timeseries(s1, name="ts1", value_type="price")
    ts2 = Timeseries(s2, name="ts2", value_type="price")
    
    # Add
    ts_add = ts1 + ts2
    assert ts_add.value_type == "price"
    assert list(ts_add.series.values) == [12.0, 24.0, 36.0]
    
    # Multiply by constant
    ts_mul = ts1 * 2
    assert list(ts_mul.series.values) == [20.0, 40.0, 60.0]
    
    # Right multiplication
    ts_rmul = 2.5 * ts2
    assert list(ts_rmul.series.values) == [5.0, 10.0, 15.0]
    
    # Subtraction and Division
    ts_sub = ts1 - ts2
    assert list(ts_sub.series.values) == [8.0, 16.0, 24.0]
    
    ts_div = ts1 / ts2
    assert list(ts_div.series.values) == [5.0, 5.0, 5.0]
    
    # Power
    ts_pow = ts2 ** 2
    assert list(ts_pow.series.values) == [4.0, 16.0, 36.0]
    
    # Comparisons (Generates Signals as 1.0 or 0.0)
    ts_gt = ts1 > 15.0
    assert ts_gt.value_type == "signal"
    assert list(ts_gt.series.values) == [0.0, 1.0, 1.0]


def test_metrics_and_functions():
    code = """
    spx = t("SPX")
    iv_atm = IV(spx, e("3M"), k("100%"))
    spot_val = SPOT(spx)
    
    # Math functions
    sq = sqrt(spot_val)
    ma_val = ma(spot_val, 5)
    r_sharpe = sharpe(iv_atm, 10)
    r_drawdown = drawdown(spot_val, 10)
    """
    
    res, env = evaluate(code)
    
    assert isinstance(env['iv_atm'], Timeseries)
    assert isinstance(env['spot_val'], Timeseries)
    assert isinstance(env['sq'], Timeseries)
    assert isinstance(env['ma_val'], Timeseries)
    assert isinstance(env['r_sharpe'], Timeseries)
    assert isinstance(env['r_drawdown'], Timeseries)
    
    # Verify values are populated and matching lengths
    assert len(env['iv_atm'].series) > 0
    assert env['iv_atm'].value_type == 'vol'
    assert env['r_drawdown'].value_type == 'pct'


def test_backtesting():
    code = """
    t1 = t("SPX")
    e1 = e("3M")
    e2 = e("1Y")
    ptf = [SD(t1, e1), SD(t1, e2)]
    sz = notional(100000, "vega")
    sig = IV(t1, e2, k("100%")) > ma(IV(t1, e1, k("100%")), 20)
    res = bt(ptf, sz, "weekly") * sig
    """
    res, env = evaluate(code)
    
    # Check that res is a BacktestResult
    bt_res = env['res']
    assert isinstance(bt_res, BacktestResult)
    
    # PL columns should be Timeseries objects
    assert isinstance(bt_res.PL, Timeseries)
    assert isinstance(bt_res.PLVega, Timeseries)
    assert isinstance(bt_res.PLCarry, Timeseries)
    assert isinstance(bt_res.PLOther, Timeseries)
    
    # Validate PL balance: PL = PLVega + PLCarry + PLOther
    # Fill NaN values for addition to pass
    pl_calc = bt_res.PLVega.series.fillna(0) + bt_res.PLCarry.series.fillna(0) + bt_res.PLOther.series.fillna(0)
    np.testing.assert_allclose(bt_res.PL.series.fillna(0).values, pl_calc.values)


def test_ast_evaluation_helpers():
    code = "val = 2.0 ** 3.0"
    
    # Serialize AST to dictionary
    ast_dict = ast_to_dict(code)
    assert isinstance(ast_dict, dict)
    assert ast_dict['type'] == 'ProgramNode'
    
    # Evaluate directly from AST dictionary
    res, env = evaluate_ast(ast_dict)
    assert env['val'] == 8.0


def test_indexing_and_slicing():
    # 1. Test basic list indexing and slicing
    code_list = "lst = [10, 20, 30, 40, 50]; x1 = lst[0]; x2 = lst[1:4]; x3 = lst[:2]; x4 = lst[3:]; x5 = lst[:]; nested = [[1, 2], [3, 4]][1][0]"
    res, env = evaluate(code_list)
    assert env['x1'] == 10
    assert env['x2'] == [20, 30, 40]
    assert env['x3'] == [10, 20]
    assert env['x4'] == [40, 50]
    assert env['x5'] == [10, 20, 30, 40, 50]
    assert env['nested'] == 3

    # 2. Test timeseries indexing and slicing
    code_ts = """
    spx = t("SPX")
    spot_val = SPOT(spx)
    
    # Slicing top 20 elements
    top20 = spot_val[0:20]
    
    # Slicing with omit start/stop
    first5 = spot_val[:5]
    last10 = spot_val[-10:]
    
    # Indexing single elements
    first_item = spot_val[0]
    second_item = spot_val[1]
    
    # Date label slicing
    date_slice = spot_val["2025-01-02":"2025-01-06"]
    """
    res, env = evaluate(code_ts)
    
    assert isinstance(env['top20'], Timeseries)
    assert len(env['top20'].series) == 20
    assert env['top20'].name == "SPOT_T(['SPX'])[0:20]"
    
    assert len(env['first5'].series) == 5
    assert env['first5'].name == "SPOT_T(['SPX'])[:5]"
    
    assert len(env['last10'].series) == 10
    assert env['last10'].name == "SPOT_T(['SPX'])[-10:]"
    
    assert isinstance(env['first_item'], float)
    assert env['first_item'] == env['spot_val'].series.iloc[0]
    assert env['second_item'] == env['spot_val'].series.iloc[1]
    
    assert isinstance(env['date_slice'], Timeseries)
    expected_len = len(env['spot_val'].series.loc["2025-01-02":"2025-01-06"])
    assert len(env['date_slice'].series) == expected_len
    assert env['date_slice'].name == "SPOT_T(['SPX'])[2025-01-02:2025-01-06]"

