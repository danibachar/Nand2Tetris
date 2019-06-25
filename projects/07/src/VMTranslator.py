from CodeWriter import CodeWriter
from Parser import Parser
from Lex import Lex, ARITHMETIC_COMMANDS, PUSH_OR_POP_COMMANDS
import os, sys


# Parsing and sanytizing args
asm_file = sys.argv[1]
if asm_file == None:
    raise Exception('missing .asm file')
file_name, file_type = os.path.splitext(asm_file)
if file_type.lower() != '.vm':
    raise Exception('File type is not supported - {}'.format(file_type))

# files
current_dir = os.path.dirname(os.path.realpath(__file__))
src_file = os.path.realpath(asm_file)
dest_file = src_file.replace(".vm", ".asm")

# RUN!
p = Parser(src_file)
cw = CodeWriter(dest_file)

while p.has_more_command():

    c_type = p.command_type()

    if c_type == Lex.C_ARITMETIC:
        cw.write_aritmethic(p.current_command())
    if c_type == Lex.C_PUSH_OR_POP:
        cw.write_push_pop(p.current_command(), p.arg1(), p.arg2())


    p.advance()
    
cw.close()
