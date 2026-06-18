class ASTNode:
    def to_dict(self):
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict) or "type" not in d:
            raise ValueError("Invalid serialization dictionary for ASTNode")
        node_type = d["type"]
        node_cls = globals().get(node_type)
        if node_cls is None or not issubclass(node_cls, ASTNode):
            raise ValueError(f"Unknown ASTNode class: {node_type}")
        return node_cls._from_dict(d)

    @classmethod
    def _from_dict(cls, d):
        raise NotImplementedError()


class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = list(statements)

    def to_dict(self):
        return {
            "type": "ProgramNode",
            "statements": [stmt.to_dict() for stmt in self.statements]
        }

    @classmethod
    def _from_dict(cls, d):
        return cls([ASTNode.from_dict(s) for s in d["statements"]])

    def __repr__(self):
        return f"ProgramNode({self.statements})"


class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_dict(self):
        return {
            "type": "AssignNode",
            "name": self.name,
            "value": self.value.to_dict()
        }

    @classmethod
    def _from_dict(cls, d):
        return cls(d["name"], ASTNode.from_dict(d["value"]))

    def __repr__(self):
        return f"AssignNode({self.name} = {self.value})"


class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def to_dict(self):
        return {
            "type": "BinaryOpNode",
            "left": self.left.to_dict(),
            "op": self.op,
            "right": self.right.to_dict()
        }

    @classmethod
    def _from_dict(cls, d):
        return cls(
            ASTNode.from_dict(d["left"]),
            d["op"],
            ASTNode.from_dict(d["right"])
        )

    def __repr__(self):
        return f"BinaryOpNode({self.left} {self.op} {self.right})"


class UnaryOpNode(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def to_dict(self):
        return {
            "type": "UnaryOpNode",
            "op": self.op,
            "expr": self.expr.to_dict()
        }

    @classmethod
    def _from_dict(cls, d):
        return cls(d["op"], ASTNode.from_dict(d["expr"]))

    def __repr__(self):
        return f"UnaryOpNode({self.op} {self.expr})"


class CallNode(ASTNode):
    def __init__(self, func_name, args, kwargs):
        self.func_name = func_name
        self.args = list(args)
        self.kwargs = dict(kwargs)

    def to_dict(self):
        return {
            "type": "CallNode",
            "func_name": self.func_name,
            "args": [a.to_dict() for a in self.args],
            "kwargs": {k: v.to_dict() for k, v in self.kwargs.items()}
        }

    @classmethod
    def _from_dict(cls, d):
        args = [ASTNode.from_dict(a) for a in d["args"]]
        kwargs = {k: ASTNode.from_dict(v) for k, v in d["kwargs"].items()}
        return cls(d["func_name"], args, kwargs)

    def __repr__(self):
        args_str = ", ".join(repr(a) for a in self.args)
        kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in self.kwargs.items())
        sep = ", " if args_str and kwargs_str else ""
        return f"CallNode({self.func_name}({args_str}{sep}{kwargs_str}))"


class ListNode(ASTNode):
    def __init__(self, elements):
        self.elements = list(elements)

    def to_dict(self):
        return {
            "type": "ListNode",
            "elements": [e.to_dict() for e in self.elements]
        }

    @classmethod
    def _from_dict(cls, d):
        return cls([ASTNode.from_dict(e) for e in d["elements"]])

    def __repr__(self):
        return f"ListNode({self.elements})"


class LiteralNode(ASTNode):
    def __init__(self, value, val_type):
        self.value = value
        self.val_type = val_type

    def to_dict(self):
        return {
            "type": "LiteralNode",
            "value": self.value,
            "val_type": self.val_type
        }

    @classmethod
    def _from_dict(cls, d):
        return cls(d["value"], d["val_type"])

    def __repr__(self):
        if self.val_type == 'STRING':
            return f"'{self.value}'"
        return f"LiteralNode({self.value}, type={self.val_type})"


class NameNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            "type": "NameNode",
            "name": self.name
        }

    @classmethod
    def _from_dict(cls, d):
        return cls(d["name"])

    def __repr__(self):
        return f"NameNode({self.name})"


class SubscriptNode(ASTNode):
    def __init__(self, value, index):
        self.value = value
        self.index = index

    def to_dict(self):
        return {
            "type": "SubscriptNode",
            "value": self.value.to_dict(),
            "index": self.index.to_dict()
        }

    @classmethod
    def _from_dict(cls, d):
        return cls(ASTNode.from_dict(d["value"]), ASTNode.from_dict(d["index"]))

    def __repr__(self):
        return f"SubscriptNode({self.value}[{self.index}])"


class SliceNode(ASTNode):
    def __init__(self, value, start, end):
        self.value = value
        self.start = start
        self.end = end

    def to_dict(self):
        return {
            "type": "SliceNode",
            "value": self.value.to_dict(),
            "start": self.start.to_dict() if self.start else None,
            "end": self.end.to_dict() if self.end else None
        }

    @classmethod
    def _from_dict(cls, d):
        start = ASTNode.from_dict(d["start"]) if d["start"] else None
        end = ASTNode.from_dict(d["end"]) if d["end"] else None
        return cls(ASTNode.from_dict(d["value"]), start, end)

    def __repr__(self):
        start_repr = repr(self.start) if self.start else ""
        end_repr = repr(self.end) if self.end else ""
        return f"SliceNode({self.value}[{start_repr}:{end_repr}])"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx].type
        return None

    def get_token(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consume(self, expected_type=None):
        if self.pos >= len(self.tokens):
            raise SyntaxError("Unexpected End Of File")
        tok = self.tokens[self.pos]
        if expected_type and tok.type != expected_type:
            raise SyntaxError(f"Expected token {expected_type} but got {tok.type} at line {tok.line}, column {tok.column}")
        self.pos += 1
        return tok

    def match(self, expected_type):
        if self.peek() == expected_type:
            self.consume()
            return True
        return False

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.pos < len(self.tokens):
            if self.peek() in ('NEWLINE', 'SEMICOLON'):
                self.consume()
                continue
            stmt = self.parse_statement()
            statements.append(stmt)
            
            # Expect statement separator
            if self.pos < len(self.tokens):
                next_tok = self.peek()
                if next_tok in ('NEWLINE', 'SEMICOLON'):
                    self.consume()
                else:
                    tok = self.tokens[self.pos]
                    raise SyntaxError(f"Expected newline or semicolon to separate statements, but got {next_tok} at line {tok.line}, column {tok.column}")
        return ProgramNode(statements)

    def parse_statement(self):
        if self.peek() == 'NAME' and self.peek(1) == 'ASSIGN':
            name_tok = self.consume('NAME')
            self.consume('ASSIGN')
            expr = self.parse_expression()
            return AssignNode(name_tok.value, expr)
        else:
            return self.parse_expression()

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.match('OR'):
            right = self.parse_and()
            node = BinaryOpNode(node, 'or', right)
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.match('AND'):
            right = self.parse_not()
            node = BinaryOpNode(node, 'and', right)
        return node

    def parse_not(self):
        if self.match('NOT'):
            expr = self.parse_not()
            return UnaryOpNode('not', expr)
        return self.parse_comparison()

    def parse_comparison(self):
        node = self.parse_arithmetic()
        comp_ops = ('EQ', 'NE', 'LT', 'GT', 'LE', 'GE')
        if self.peek() in comp_ops:
            op_tok = self.consume()
            op_map = {
                'EQ': '==', 'NE': '!=',
                'LT': '<', 'GT': '>',
                'LE': '<=', 'GE': '>='
            }
            right = self.parse_arithmetic()
            node = BinaryOpNode(node, op_map[op_tok.type], right)
        return node

    def parse_arithmetic(self):
        node = self.parse_term()
        while self.peek() in ('PLUS', 'MINUS'):
            op_tok = self.consume()
            op = '+' if op_tok.type == 'PLUS' else '-'
            right = self.parse_term()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek() in ('MUL', 'DIV'):
            op_tok = self.consume()
            op = '*' if op_tok.type == 'MUL' else '/'
            right = self.parse_factor()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_factor(self):
        if self.peek() in ('PLUS', 'MINUS'):
            op_tok = self.consume()
            op = '+' if op_tok.type == 'PLUS' else '-'
            factor = self.parse_factor()
            return UnaryOpNode(op, factor)
        return self.parse_power()

    def parse_power(self):
        node = self.parse_primary()
        if self.match('POW'):
            right = self.parse_factor()
            node = BinaryOpNode(node, '**', right)
        return node

    def parse_primary(self):
        tok_type = self.peek()
        if tok_type == 'NUMBER':
            tok = self.consume()
            val = float(tok.value) if '.' in tok.value else int(tok.value)
            node = LiteralNode(val, 'NUMBER')
        elif tok_type == 'STRING':
            tok = self.consume()
            node = LiteralNode(tok.value, 'STRING')
        elif tok_type == 'DATE':
            tok = self.consume()
            node = LiteralNode(tok.value, 'DATE')
        elif tok_type == 'DATETIME':
            tok = self.consume()
            node = LiteralNode(tok.value, 'DATETIME')
        elif tok_type == 'TRUE':
            self.consume()
            node = LiteralNode(True, 'BOOL')
        elif tok_type == 'FALSE':
            self.consume()
            node = LiteralNode(False, 'BOOL')
        elif tok_type == 'NONE':
            self.consume()
            node = LiteralNode(None, 'NONE')
        elif tok_type == 'LBRACKET':
            self.consume('LBRACKET')
            elements = []
            if self.peek() != 'RBRACKET':
                elements.append(self.parse_expression())
                while self.match('COMMA'):
                    if self.peek() == 'RBRACKET':
                        break
                    elements.append(self.parse_expression())
            self.consume('RBRACKET')
            node = ListNode(elements)
        elif tok_type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            node = expr
        elif tok_type == 'NAME':
            name_tok = self.consume('NAME')
            if self.peek() == 'LPAREN':
                self.consume('LPAREN')
                args = []
                kwargs = {}
                if self.peek() != 'RPAREN':
                    while True:
                        if self.peek() == 'NAME' and self.peek(1) == 'ASSIGN':
                            kw_name = self.consume('NAME').value
                            self.consume('ASSIGN')
                            kw_val = self.parse_expression()
                            kwargs[kw_name] = kw_val
                        else:
                            if kwargs:
                                tok = self.get_token()
                                raise SyntaxError(f"Positional argument follows keyword argument at line {tok.line}, column {tok.column}")
                            args.append(self.parse_expression())
                        if not self.match('COMMA'):
                            break
                        if self.peek() == 'RPAREN':
                            break
                self.consume('RPAREN')
                node = CallNode(name_tok.value, args, kwargs)
            else:
                node = NameNode(name_tok.value)
        else:
            tok = self.get_token()
            tok_desc = f"{tok.type}({tok.value})" if tok else "EOF"
            line = tok.line if tok else "unknown"
            col = tok.column if tok else "unknown"
            raise SyntaxError(f"Unexpected token {tok_desc} at line {line}, column {col} while parsing primary expression")

        # Parse postfix subscript/slice operations
        while self.peek() == 'LBRACKET':
            self.consume('LBRACKET')
            if self.match('COLON'):
                # Slice: [:end] or [:]
                if self.peek() == 'RBRACKET':
                    end_val = None
                else:
                    end_val = self.parse_expression()
                self.consume('RBRACKET')
                node = SliceNode(node, None, end_val)
            else:
                first = self.parse_expression()
                if self.match('COLON'):
                    # Slice: [start:end] or [start:]
                    if self.peek() == 'RBRACKET':
                        end_val = None
                    else:
                        end_val = self.parse_expression()
                    self.consume('RBRACKET')
                    node = SliceNode(node, first, end_val)
                else:
                    # Indexing: [index]
                    self.consume('RBRACKET')
                    node = SubscriptNode(node, first)
                    
        return node
