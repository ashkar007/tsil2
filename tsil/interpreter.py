from .lexer import tokenize
from .parser import Parser, ASTNode

class Interpreter:
    def __init__(self, env=None):
        self.env = env if env is not None else {}
        
        # Inject built-in functions & weighting scheme constants into env
        from .functions import FUNCTION_MAP
        for k, v in FUNCTION_MAP.items():
            if k not in self.env:
                self.env[k] = v

    def evaluate(self, node):
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f"No evaluation method for node type: {type(node).__name__}")
        return method(node)

    def eval_ProgramNode(self, node):
        res = None
        for stmt in node.statements:
            res = self.evaluate(stmt)
        return res

    def eval_AssignNode(self, node):
        val = self.evaluate(node.value)
        self.env[node.name] = val
        return val

    def eval_BinaryOpNode(self, node):
        left_val = self.evaluate(node.left)
        right_val = self.evaluate(node.right)
        op = node.op

        if op == '+': return left_val + right_val
        elif op == '-': return left_val - right_val
        elif op == '*': return left_val * right_val
        elif op == '/': return left_val / right_val
        elif op == '**': return left_val ** right_val
        elif op == 'and': return left_val and right_val
        elif op == 'or': return left_val or right_val
        elif op == '==': return left_val == right_val
        elif op == '!=': return left_val != right_val
        elif op == '<': return left_val < right_val
        elif op == '>': return left_val > right_val
        elif op == '<=': return left_val <= right_val
        elif op == '>=': return left_val >= right_val
        else:
            raise ValueError(f"Unknown binary operator: {op}")

    def eval_UnaryOpNode(self, node):
        expr_val = self.evaluate(node.expr)
        op = node.op

        if op == '+': return +expr_val
        elif op == '-': return -expr_val
        elif op == 'not': return not expr_val
        else:
            raise ValueError(f"Unknown unary operator: {op}")

    def eval_CallNode(self, node):
        func = self.env.get(node.func_name)
        if func is None:
            raise NameError(f"Function/constructor '{node.func_name}' is not defined")
            
        args_vals = [self.evaluate(a) for a in node.args]
        kwargs_vals = {k: self.evaluate(v) for k, v in node.kwargs.items()}
        return func(*args_vals, **kwargs_vals)

    def eval_ListNode(self, node):
        return [self.evaluate(e) for e in node.elements]

    def eval_LiteralNode(self, node):
        return node.value

    def eval_NameNode(self, node):
        if node.name not in self.env:
            raise NameError(f"Variable '{node.name}' is not defined")
        return self.env[node.name]

    def eval_SubscriptNode(self, node):
        val = self.evaluate(node.value)
        idx = self.evaluate(node.index)
        return val[idx]

    def eval_SliceNode(self, node):
        val = self.evaluate(node.value)
        start = self.evaluate(node.start) if node.start else None
        end = self.evaluate(node.end) if node.end else None
        return val[start:end]



def evaluate(script_str, env=None):
    """
    Parses and evaluates a TSIL script.
    Returns a tuple: (last_expr_result, final_environment_dict)
    """
    tokens = tokenize(script_str)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter(env)
    res = interpreter.evaluate(ast)
    return res, interpreter.env


def ast_to_dict(script_str):
    """
    Parses a script and returns its serialized AST dictionary.
    """
    tokens = tokenize(script_str)
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.to_dict()


def evaluate_ast(ast_dict_or_node, env=None):
    """
    Evaluates a serialized AST dictionary or AST node.
    Returns a tuple: (last_expr_result, final_environment_dict)
    """
    if isinstance(ast_dict_or_node, dict):
        node = ASTNode.from_dict(ast_dict_or_node)
    else:
        node = ast_dict_or_node
    interpreter = Interpreter(env)
    res = interpreter.evaluate(node)
    return res, interpreter.env
