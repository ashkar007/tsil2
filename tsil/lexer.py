import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


TOKEN_SPEC = [
    # Datetime (ISO 8601) - check before Date
    ('DATETIME', r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'),
    # Date (ISO 8601) - check before minus signs / subtraction
    ('DATE', r'\d{4}-\d{2}-\d{2}'),
    # Number (Float/Int)
    ('NUMBER', r'\d+(?:\.\d+)?'),
    # String literals (double and single quotes)
    ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\''),
    # Identifier (Name)
    ('NAME', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    # Multi-character operators
    ('POW', r'\*\*'),
    ('EQ', r'=='),
    ('NE', r'!='),
    ('GE', r'>='),
    ('LE', r'<='),
    # Single-character operators
    ('GT', r'>'),
    ('LT', r'<'),
    ('ASSIGN', r'='),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MUL', r'\*'),
    ('DIV', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('COLON', r':'),
    # Newline
    ('NEWLINE', r'\n'),
    # Line continuation
    ('CONTINUATION', r'\\\n'),
    # Comments (starts with #)
    ('COMMENT', r'#[^\n]*'),
    # Skippable whitespace
    ('SKIP', r'[ \t\r]+'),
    # Mismatch catch-all
    ('MISMATCH', r'.'),
]

# Create compiled master regex
MASTER_RE = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC))

def tokenize(code):
    tokens = []
    line_number = 1
    line_start = 0
    bracket_depth = 0

    # Ensure code ends with newline to flush any final expressions if needed,
    # but we can also just handle it at EOF.
    for mo in MASTER_RE.finditer(code):
        kind = mo.lastgroup
        value = mo.group(kind)
        column = mo.start() - line_start + 1

        if kind == 'SKIP':
            continue
        elif kind == 'COMMENT':
            continue
        elif kind == 'CONTINUATION':
            line_number += 1
            line_start = mo.end()
            continue
        elif kind == 'NEWLINE':
            line_number += 1
            line_start = mo.end()
            # If inside parentheses or brackets, ignore newline
            if bracket_depth > 0:
                continue
            # Avoid duplicate NEWLINE tokens and leading newlines
            if tokens and tokens[-1].type not in ('NEWLINE', 'SEMICOLON'):
                tokens.append(Token('NEWLINE', '\n', line_number - 1, column))
            continue
        elif kind == 'SEMICOLON':
            # Semicolon acts as a statement separator
            if tokens and tokens[-1].type not in ('NEWLINE', 'SEMICOLON'):
                tokens.append(Token('SEMICOLON', ';', line_number, column))
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character {repr(value)} on line {line_number}, column {column}")
        
        # Strip quotes from string literals
        if kind == 'STRING':
            value = value[1:-1].encode().decode('unicode_escape')

        # Bracket tracking
        if kind in ('LPAREN', 'LBRACKET'):
            bracket_depth += 1
        elif kind in ('RPAREN', 'RBRACKET'):
            bracket_depth -= 1
            if bracket_depth < 0:
                raise SyntaxError(f"Unmatched closing parenthesis/bracket on line {line_number}, column {column}")

        # Map boolean/none keywords to specific token types for easier parsing
        if kind == 'NAME':
            if value == 'True':
                kind = 'TRUE'
            elif value == 'False':
                kind = 'FALSE'
            elif value == 'None':
                kind = 'NONE'
            elif value == 'and':
                kind = 'AND'
            elif value == 'or':
                kind = 'OR'
            elif value == 'not':
                kind = 'NOT'

        tokens.append(Token(kind, value, line_number, column))

    # Append a final NEWLINE if the last token isn't a separator (to help parser terminate)
    if tokens and tokens[-1].type not in ('NEWLINE', 'SEMICOLON'):
        tokens.append(Token('NEWLINE', '\n', line_number, len(code) - line_start + 1))
        
    return tokens
