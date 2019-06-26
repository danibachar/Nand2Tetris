from Lex import Lex, ARITHMETIC_COMMANDS, PUSH_OR_POP_COMMANDS

class Parser:
    def __init__(self, src_file_name):
        self._line_index = 0


        self._line_index = 0
        self._lines = []
        self.contains_sysinit_call = False
        f = open(src_file_name)
        # First assesment of the Assembler
        for line in f.readlines():
            strip_line = line.lstrip()
            # Skipping none relevant
            if len(strip_line) == 0 or strip_line[0:2] == '//':
                continue
            #l = strip_line.replace(' ', '') # Removing whitespace
            l = strip_line.replace('\n', '')  # Removing new line
            l = l.replace('\t', '') # Removing tabs
            l = l.split('/')[0] # Removing comments
            if 'Sys.init' in l:
                self.contains_sysinit_call = True
            self._lines.append(l)

    def contains_sysinit_call(self):
        return self.contains_sysinit_call

    def current_command(self):
        curr_line = self._lines[self._line_index]
        return curr_line.split(" ")[0]

    def advance(self):
        self._line_index+=1

    def has_more_command(self):
        return len(self._lines) > self._line_index

    def command_type(self):
        command = self.current_command()
        if command in PUSH_OR_POP_COMMANDS:
            return Lex.C_PUSH_OR_POP
        elif command in ARITHMETIC_COMMANDS:
            return Lex.C_ARITMETIC
        elif command == Lex.C_IF:
            return Lex.C_IF
        elif command == Lex.C_LABEL:
            return Lex.C_LABEL
        elif command == Lex.C_GOTO:
            return Lex.C_GOTO
        elif command == Lex.C_FUNCTION:
            return Lex.C_FUNCTION
        elif command == Lex.C_RETURN:
            return Lex.C_RETURN
        elif command == Lex.C_CALL:
            return Lex.C_CALL
        raise Exception("Command Type not found in line = {}".format(command))


    def arg1(self):
        curr_line = self._lines[self._line_index]
        return curr_line.split(" ")[1]

    def arg2(self):
        curr_line = self._lines[self._line_index]
        return curr_line.split(" ")[2]
