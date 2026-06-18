# TSIL Abstract Syntax Tree (AST) Examples

This reference document contains script examples in TSIL and their compiled Abstract Syntax Tree (AST) JSON representations. You can parse any TSIL script into these structures using `tsil.interpreter.ast_to_dict(script)` and evaluate them programmatically using `tsil.interpreter.evaluate_ast(ast_json)`.

---

## Example 1: Volatility Spread Analysis

This script demonstrates basic variable assignment, function calls, arithmetic operator precedence, and floating-point literals.

### TSIL Script
```python
iv_spread = IV(t('SX5E'), e('2Y'), k('100%')) - 1.5 * IV(t('SX5E'), e('1Y'), k('100%'))
```

### Generated JSON AST
```json
{
  "type": "ProgramNode",
  "statements": [
    {
      "type": "AssignNode",
      "name": "iv_spread",
      "value": {
        "type": "BinaryOpNode",
        "left": {
          "type": "CallNode",
          "func_name": "IV",
          "args": [
            {
              "type": "CallNode",
              "func_name": "t",
              "args": [
                {
                  "type": "LiteralNode",
                  "value": "SX5E",
                  "val_type": "STRING"
                }
              ],
              "kwargs": {}
            },
            {
              "type": "CallNode",
              "func_name": "e",
              "args": [
                {
                  "type": "LiteralNode",
                  "value": "2Y",
                  "val_type": "STRING"
                }
              ],
              "kwargs": {}
            },
            {
              "type": "CallNode",
              "func_name": "k",
              "args": [
                {
                  "type": "LiteralNode",
                  "value": "100%",
                  "val_type": "STRING"
                }
              ],
              "kwargs": {}
            }
          ],
          "kwargs": {}
        },
        "op": "-",
        "right": {
          "type": "BinaryOpNode",
          "left": {
            "type": "LiteralNode",
            "value": 1.5,
            "val_type": "NUMBER"
          },
          "op": "*",
          "right": {
            "type": "CallNode",
            "func_name": "IV",
            "args": [
              {
                "type": "CallNode",
                "func_name": "t",
                "args": [
                  {
                    "type": "LiteralNode",
                    "value": "SX5E",
                    "val_type": "STRING"
                  }
                ],
                "kwargs": {}
              },
              {
                "type": "CallNode",
                "func_name": "e",
                "args": [
                  {
                    "type": "LiteralNode",
                    "value": "1Y",
                    "val_type": "STRING"
                  }
                ],
                "kwargs": {}
              },
              {
                "type": "CallNode",
                "func_name": "k",
                "args": [
                  {
                    "type": "LiteralNode",
                    "value": "100%",
                    "val_type": "STRING"
                  }
                ],
                "kwargs": {}
              }
            ],
            "kwargs": {}
          }
        }
      }
    }
  ]
}
```

---

## Example 2: Multi-Asset Spot Ratio

This script demonstrates operations combined on three timeseries: adding spot prices of two assets (`SPX` and `SX5E`) and dividing the sum by a scaled third timeseries (`NDX`).

### TSIL Script
```python
ratio = (SPOT(t('SPX')) + SPOT(t('SX5E'))) / (2.0 * SPOT(t('NDX')))
```

### Generated JSON AST
```json
{
  "type": "ProgramNode",
  "statements": [
    {
      "type": "AssignNode",
      "name": "ratio",
      "value": {
        "type": "BinaryOpNode",
        "left": {
          "type": "BinaryOpNode",
          "left": {
            "type": "CallNode",
            "func_name": "SPOT",
            "args": [
              {
                "type": "CallNode",
                "func_name": "t",
                "args": [
                  {
                    "type": "LiteralNode",
                    "value": "SPX",
                    "val_type": "STRING"
                  }
                ],
                "kwargs": {}
              }
            ],
            "kwargs": {}
          },
          "op": "+",
          "right": {
            "type": "CallNode",
            "func_name": "SPOT",
            "args": [
              {
                "type": "CallNode",
                "func_name": "t",
                "args": [
                  {
                    "type": "LiteralNode",
                    "value": "SX5E",
                    "val_type": "STRING"
                  }
                ],
                "kwargs": {}
              }
            ],
            "kwargs": {}
          }
        },
        "op": "/",
        "right": {
          "type": "BinaryOpNode",
          "left": {
            "type": "LiteralNode",
            "value": 2.0,
            "val_type": "NUMBER"
          },
          "op": "*",
          "right": {
            "type": "CallNode",
            "func_name": "SPOT",
            "args": [
              {
                "type": "CallNode",
                "func_name": "t",
                "args": [
                  {
                    "type": "LiteralNode",
                    "value": "NDX",
                    "val_type": "STRING"
                  }
                ],
                "kwargs": {}
              }
            ],
            "kwargs": {}
          }
        }
      }
    }
  ]
}
```

---

## Example 3: Straddle Backtest with Moving Average Signal

This program shows multiple statements separated by semicolons, references to previously assigned variable names (`t1` and `sig`), a list expression `[...]` for the portfolio, and comparison operator `>` between a spot query and a rolling moving average indicator.

### TSIL Script
```python
t1 = t('SPX'); ptf = [SD(t1, e('3M'))]; sz = notional(5000000, 'vega'); sig = SPOT(t1) > ma(SPOT(t1), 20); res = bt(ptf, sz, 'weekly') * sig
```

### Generated JSON AST
```json
{
  "type": "ProgramNode",
  "statements": [
    {
      "type": "AssignNode",
      "name": "t1",
      "value": {
        "type": "CallNode",
        "func_name": "t",
        "args": [
          {
            "type": "LiteralNode",
            "value": "SPX",
            "val_type": "STRING"
          }
        ],
        "kwargs": {}
      }
    },
    {
      "type": "AssignNode",
      "name": "ptf",
      "value": {
        "type": "ListNode",
        "elements": [
          {
            "type": "CallNode",
            "func_name": "SD",
            "args": [
              {
                "type": "NameNode",
                "name": "t1"
              },
              {
                "type": "CallNode",
                "func_name": "e",
                "args": [
                  {
                    "type": "LiteralNode",
                    "value": "3M",
                    "val_type": "STRING"
                  }
                ],
                "kwargs": {}
              }
            ],
            "kwargs": {}
          }
        ]
      }
    },
    {
      "type": "AssignNode",
      "name": "sz",
      "value": {
        "type": "CallNode",
        "func_name": "notional",
        "args": [
          {
            "type": "LiteralNode",
            "value": 5000000,
            "val_type": "NUMBER"
          },
          {
            "type": "LiteralNode",
            "value": "vega",
            "val_type": "STRING"
          }
        ],
        "kwargs": {}
      }
    },
    {
      "type": "AssignNode",
      "name": "sig",
      "value": {
        "type": "BinaryOpNode",
        "left": {
          "type": "CallNode",
          "func_name": "SPOT",
          "args": [
            {
              "type": "NameNode",
              "name": "t1"
            }
          ],
          "kwargs": {}
        },
        "op": ">",
        "right": {
          "type": "CallNode",
          "func_name": "ma",
          "args": [
            {
              "type": "CallNode",
              "func_name": "SPOT",
              "args": [
                {
                  "type": "NameNode",
                  "name": "t1"
                }
              ],
              "kwargs": {}
            },
            {
              "type": "LiteralNode",
              "value": 20,
              "val_type": "NUMBER"
            }
          ],
          "kwargs": {}
        }
      }
    },
    {
      "type": "AssignNode",
      "name": "res",
      "value": {
        "type": "BinaryOpNode",
        "left": {
          "type": "CallNode",
          "func_name": "bt",
          "args": [
            {
              "type": "NameNode",
              "name": "ptf"
            },
            {
              "type": "NameNode",
              "name": "sz"
            },
            {
              "type": "LiteralNode",
              "value": "weekly",
              "val_type": "STRING"
            }
          ],
          "kwargs": {}
        },
        "op": "*",
        "right": {
          "type": "NameNode",
          "name": "sig"
        }
      }
    }
  ]
}
```
