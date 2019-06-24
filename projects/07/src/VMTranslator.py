from CodeWriter import CodeWriter
from Parser import Parser


# Parsing and sanytizing args
asm_file = sys.argv[1]
if asm_file == None:
    raise Exception('missing .asm file')
file_name, file_type = os.path.splitext(asm_file)
if file_type.lower() != '.vm':
    raise Exception('File type is not supported - {}'.format(file_type))

# files
current_dir = os.path.dirname(os.path.realpath(__file__))
asm_full_file_path = os.path.realpath(asm_file)
dest_file = '/'.join([current_dir, file_name+'.asm'])

# RUN!
