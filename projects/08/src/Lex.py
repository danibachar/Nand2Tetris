
ARITHMETIC_COMMANDS = ["add", "sub", "neg", 'lt', 'eq', 'gt', 'and', 'or', 'not']
PUSH_OR_POP_COMMANDS = ["push", "pop"]

MEMORY_SEGMENTS_MAP = { "local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
MEMORY_SEGMENTS = list(MEMORY_SEGMENTS_MAP.keys())

class Lex:
    C_ARITMETIC = "C_ARITMETIC"
    C_PUSH_OR_POP = 'C_PUSH_OR_POP'

    C_LABEL = "label"
    C_GOTO = "goto"
    C_IF = "if-goto"

    C_FUNCTION = "function"
    C_RETURN = "return"
    C_CALL = "call"
