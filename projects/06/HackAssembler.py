import os, sys

class Parser:
    def __init__(self, src_file_name):
        self._symbol_table = SymbolTable()
        self.A_COMMAND = "A_COMMAND"
        self.C_COMMAND = "C_COMMAND"
        self.L_COMMAND = "L_COMMAND"

        self._line_index = 0
        self._lines = []
        f = open(src_file_name)
        # First assesment of the Assembler
        for line in f.readlines():
            strip_line = line.lstrip()
            # Skipping none relevant
            if len(strip_line) == 0 or strip_line[0:2] == '//':
                continue
            l = strip_line.replace(' ', '') # Removing whitespace
            l = l.replace('\n', '')  # Removing new line
            l = l.replace('\t', '') # Removing tabs
            l = l.split('/')[0] # Removing comments

            # Here we need to decide what to do with the line!
            if "(" == l[0] and ")" == l[-1]:
                # we have LABEL
                l = l.replace(")", "").replace("(", "")
                self._symbol_table.add_entry(l, self._line_index)
            else:
                self._lines.append(l)
                self._line_index+=1

        # Zeroing line index after first pass
        self._line_index = 0
        # closing file as no need - all in RAM already
        f.close()

    def advance(self):
        self._line_index+=1

    def has_more_command(self):
        return len(self._lines) > self._line_index

    def command_type(self):
        curr_line = self._lines[self._line_index]
        if "@" == curr_line[0]:
            return self.A_COMMAND
        elif "(" == curr_line[0] and ")" == curr_line[-1]:
            return self.L_COMMAND
        else:
            return self.C_COMMAND

    def dest(self):
        self._validate_c_command()
        curr_line = self._lines[self._line_index]
        dest = curr_line.split("=")
        if len(dest) > 1:
            return dest[0]
        return ""

    def comp(self):
        self._validate_c_command()
        curr_line = self._lines[self._line_index]
        comp = curr_line.split(";")[0].split("=")
        if len(comp) > 1:
            return comp[1]
        return comp[0]

    def jump(self):
        self._validate_c_command()
        curr_line = self._lines[self._line_index]
        jump = curr_line.split(";")
        if len(jump) > 1:
            return jump[1]
        return ""

    def symbol(self):
        self._validate_not_c_command()
        curr_line = self._lines[self._line_index]
        symbol = curr_line.replace("@", "")
        try:
            val = int(symbol)
            return val
        except Exception as e:
            # We have a symbol, we need to consult the table
            if self._symbol_table.contains(symbol):
                symbol = self._symbol_table.get_address(symbol)
                return symbol
            else:
                self._symbol_table.add_entry(symbol)
                symbol = self._symbol_table.get_address(symbol)
                return symbol


    def _validate_c_command(self):
        if self.command_type() != self.C_COMMAND:
            raise Exception(".dest called when current command is NOT c")

    def _validate_not_c_command(self):
        if self.command_type() == self.C_COMMAND:
            raise Exception(".symbol called when current command is c")

class CodeMap:
    def __init__(self):

        self.comp_commands = {
            # a=0
            "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100", "A": "0110000", "!D": "0001101",
            "!A": "0110001", "-D": "0001111", "-A": "0110011", "D+1": "0011111", "D-1": "0001110", "A-1": "0110010",
            "D+A": "0000010", "D-A": "0010011", "A-D": "0000111", "D&A": "0000000", "D|A": "0010101", "A+1": "0110111",
            # a=1
            "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111", "M-1": "1110010",
            "D+M": "1000010", "D-M": "1010011", "M-D": "1000111", "D&M": "1000000", "D|M": "1010101",
        }
        self.dest_commands = {
            "": "000", "M": "001", "D": "010", "MD": "011",
            "A": "100", "AM": "101", "AD": "110", "AMD": "111",
        }
        self.jmp_commands = {
            "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
            "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
        }

    def comp(self, value=None):
        if value is None:
            return
        return self.comp_commands.get(value, "WRONG_COMP_"+value)


    def dest(self, value=None):
        if value is None:
            return
        return self.dest_commands.get(value, "WRONG_DEST_"+value)

    def jump(self, value=None):
        if value is None:
            return
        return self.jmp_commands.get(value, "WRONG_JUMP_"+value)


class SymbolTable:
    def __init__(self):
        self._table = {
            # Predefined Registers
            "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7,
            "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
            # Pointers
            "SP": 0, "LCL": 1, "ARG": 2, "THIS":3, "THAT": 4,
            # Constant Pointers
            "SCREEN": 16384, "KBD": 24576
        }
        self.counter = 16


    def add_entry(self, symbol, address=None):
        if address == None:
            address = self.counter
            self.counter+=1
        self._table[symbol] = address

    def contains(self, symbol: str):
        return self._table.get(symbol, None) != None

    def get_address(self, symbol: str):
        return self._table.get(symbol, None)

class Assembler:
    def __init__(self, src_file_name, dst_file_name):
        self._parser = Parser(src_file_name)
        self._codeMap = CodeMap()

        self.f = open(dst_file_name, 'w')

        # Run Loop - Main Logic
        while self._parser.has_more_command():
            binary_to_commit = None

            command_type = self._parser.command_type()
            if command_type == self._parser.C_COMMAND:
                c = self._codeMap.comp(self._parser.comp())
                d = self._codeMap.dest(self._parser.dest())
                j = self._codeMap.jump(self._parser.jump())
                binary_to_commit = "".join(['111', c, d, j])
            else:
                s = self._parser.symbol()
                binary_to_commit = "".join(['0', self.decimal_to_binary_with_padding(s)])

            self.f.write(binary_to_commit + '\n')
            self._parser.advance()

        self.f.flush()
        self.f.close()

    def decimal_to_binary_with_padding(self, n):
        raw_bin = bin(n).replace("0b", "")
        zeros_to_add = 15 - len(raw_bin)
        if zeros_to_add <= 0:
            return raw_bin
        res = ''
        for _ in range(zeros_to_add):
            res+= '0'
        res+=raw_bin
        return res

# Parsing and sanytizing args
asm_file = sys.argv[1]
if asm_file == None:
    raise Exception('missing .asm file')
file_name, file_type = os.path.splitext(asm_file)
if file_type.lower() != '.asm':
    raise Exception('File type is not supported - {}'.format(file_type))

# files
current_dir = os.path.dirname(os.path.realpath(__file__))
asm_full_file_path = os.path.realpath(asm_file)
dest_file = '/'.join([current_dir, file_name+'.hack'])

# RUN!
Assembler(asm_full_file_path, dest_file)
