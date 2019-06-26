from CodeWriter import CodeWriter
from Parser import Parser
from Lex import Lex, ARITHMETIC_COMMANDS, PUSH_OR_POP_COMMANDS
import os, sys


# Parsing and sanytizing args
my_input = sys.argv[1]
# Parsing if directory or file name
if my_input == None:
    raise Exception('missing .vm file or base directory')

# files
current_dir = os.path.dirname(os.path.realpath(__file__))

files_names = []
dest_file = None

if my_input.endswith('.vm'):
    # We have a single vm file
    print('Input single .vm file - processing file - {}'.format(my_input))
    dest_file = '/'.join([current_dir, my_input.replace('.vm', '.asm')])
    files_names = [os.path.realpath(my_input)]
else:
    # We have directory
    print('Input directory - processing directoy - {}'.format(my_input))
    full_dir_name = os.path.realpath(my_input)
    file_name = full_dir_name.split('/')[-1]
    dest_file = '/'.join([full_dir_name, file_name + '.asm', ])
    dir_content_filtered = list(sorted(filter(lambda x: x.endswith('.vm'), os.listdir(full_dir_name)), reverse=True))
    for vm_file in dir_content_filtered:
        files_names.append('/'.join([full_dir_name, vm_file, ]))


print('dest_file - {}'.format(dest_file))
print('.vm files to process - {}'.format(files_names))

cw = CodeWriter(dest_file)

# RUN!
for file in files_names:
    p = Parser(file)
    cw.update_file_name(file)

    while p.has_more_command():

        c_type = p.command_type()

        if c_type == Lex.C_ARITMETIC:
            cw.write_aritmethic(p.current_command())
        elif c_type == Lex.C_PUSH_OR_POP:
            cw.write_push_pop(p.current_command(), p.arg1(), p.arg2())
        elif c_type == Lex.C_IF:
            cw.write_if_goto(p.current_command(), p.arg1())
        elif c_type == Lex.C_GOTO:
            cw.write_goto(p.current_command(), p.arg1())
        elif c_type == Lex.C_LABEL:
            cw.write_label(p.current_command(), p.arg1())
        elif c_type == Lex.C_FUNCTION:
            cw.write_function(p.current_command(), p.arg1(), p.arg2())
        elif c_type == Lex.C_RETURN:
            cw.write_return()
        elif c_type == Lex.C_CALL:
            cw.write_call(p.current_command(), p.arg1(), p.arg2())

        else:
            raise Exception("VMTranslator unknow command")


        p.advance()

cw.close()
