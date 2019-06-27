

class JackTokenizer:

    def __init__(self, src_file_name):
        self._line_index = 0


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
            l = strip_line.replace('\n', '')  # Removing new line
            l = l.replace('\t', '') # Removing tabs
            l = l.split('/')[0] # Removing comments
            self._lines.append(l)

        f.close()

    def current_token(self):
        curr_line = self._lines[self._line_index]
        return ""

    def advance(self):
        self._line_index+=1

    def has_more_command(self):
        return len(self._lines) > self._line_index

    def token_type(self):
        pass
