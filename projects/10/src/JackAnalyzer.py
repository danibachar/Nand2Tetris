from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
from Constants import *
import os, sys


# Parsing and sanytizing args
my_input = sys.argv[1]
# Parsing if directory or file name
if my_input == None:
    raise Exception('missing .jack file or base directory')

# files
current_dir = os.path.dirname(os.path.realpath(__file__))

files_names = []
dest_file = None

if my_input.endswith('.jack'):
    # We have a single vm file
    print('Input single .vm file - processing file - {}'.format(my_input))
    dest_file = '/'.join([current_dir, my_input.replace('.vm', '.xml')])
    files_names = [os.path.realpath(my_input)]
else:
    # We have directory
    print('Input directory - processing directoy - {}'.format(my_input))
    full_dir_name = os.path.realpath(my_input)
    file_name = full_dir_name.split('/')[-1]
    dest_file = '/'.join([full_dir_name, file_name + '.xml', ])
    dir_content_filtered = list(sorted(filter(lambda x: x.endswith('.jack'), os.listdir(full_dir_name)), reverse=True))
    for vm_file in dir_content_filtered:
        files_names.append('/'.join([full_dir_name, vm_file, ]))


print('dest_file - {}'.format(dest_file))
print('.vm files to process - {}'.format(files_names))



for file in files_names:
    jt = JackTokenizer(file)

    while jt.has_more_command():

        t_type = jt.token_type()

        if t_type == TOKEN_TYPE_KEYWORD:
            pass
        elif t_type == TOKEN_TYPE_SYMBOL:
            pass
        elif t_type == TOKEN_TYPE_INT_CONST:
            pass
        elif t_type == TOKEN_TYPE_STR_CONST:
            pass
        elif t_type == TOKEN_TYPE_IDENTIFIER:
            pass
        else:
            raise Exception("Unsupported Token Type = {}".format(t_type))

        jt.advance()
