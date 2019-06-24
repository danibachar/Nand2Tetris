

class Parser:
    def __init__(self, src_file_name):
        self._line_index = 0

        # init Commad Types
        self.C_ARITMETIC = "C_ARITMETIC"
        self.C_PUSH = "push"
        self.C_POP = "pop"
        self.C_LABEL = "C_LABEL"
        self.C_GOTO = "C_GOTO"
        self.C_IF = "C_IF"
        self.C_FUNCTION = "funcction"
        self.C_RETURN = "return"
        self.C_CALL = "call"

        self._line_index = 0
        self._lines = []

        f = open(src_file_name)
        # First assesment of the Assembler
        for line in f.readlines():
            strip_line = line.lstrip()
            # Skipping none relevant
            if len(strip_line) == 0 or strip_line[0:2] == '//':
                continue
            #l = strip_line.replace(' ', '') # Removing whitespace
            l = l.replace('\n', '')  # Removing new line
            l = l.replace('\t', '') # Removing tabs
            l = l.split('/')[0] # Removing comments

            self._lines.append(l)

    def current_command(self):
        curr_line = self._lines[self._line_index]
        return curr_line.split(" ")

    def advance(self):
        self._line_index+=1

    def has_more_command(self):
        return len(self._lines) > self._line_index

    def command_type(self):
        curr_line = self._lines[self._line_index]

    def arg1(self):
        pass

    def arg2(self):
        pass
