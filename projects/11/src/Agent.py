class Agent:

    def __init__(self, tokens, base_filename):
        self.tokens = list(tokens)
        self.cur_idx = 0
        self.cur = self.tokens[self.cur_idx]
        self.fname = base_filename + ".vm"
        self.f = open(self.fname, "w")

    def peek(self):
        if self.cur_idx < len(self.tokens):
            return self.tokens[self.cur_idx]
        else:
            return 'NO_MORE_TOKENS'

    def advance(self):
        if self.cur_idx < len(self.tokens):
           token = self.tokens[self.cur_idx]
           self.cur = token
           self.cur_idx += 1
           return token
        else:
            raise Exception("No more Tokens")

    def writeFunction(self, class_name, sub_name, local_var_count):
        tmp = ".".join([class_name, sub_name])
        tmp = " ".join(['function', tmp, str(local_var_count)])
        self.write_new_line(tmp)

    def writeCall(self, class_name, sub_name, argument_count):
        tmp = ".".join([class_name, sub_name])
        tmp = " ".join(['call', tmp, str(argument_count)])
        self.write_new_line(tmp)

    def writeIfGoto(self, label):
        tmp = " ".join(['if-goto', label])
        self.write_new_line(tmp)

    def writeGoto(self, label):
        tmp = " ".join(['goto', label])
        self.write_new_line(tmp)

    def writeLabel(self, label):
        tmp = " ".join(['label', label])
        self.write_new_line(tmp)

    def writePush(self, segment, index):
        tmp = " ".join(['push', segment, str(index)])
        self.write_new_line(tmp)

    def writePop(self, segment, index):
        tmp = " ".join(['pop', segment, str(index)])
        self.write_new_line(tmp)

    def writeArithmatic(self, operator, helper=None):
        tmp = ""
        if operator == '+':
            tmp = 'add'
        if operator == '-' and helper == None: # Distinguish between subtraction and - negtive number
            tmp = 'sub'
        if operator == '-' and helper == 'NEG': # Distinguish between subtraction and -negtive number
            tmp = 'neg'
        if operator == '~':
            tmp = "not"
        if operator == '<':
            tmp = "lt"
        if operator == '>':
            tmp = "gt"
        if operator == '&':
            tmp = "and"
        if operator == '|':
            tmp = "or"
        if operator == '=':
            tmp = "eq"
        if operator == '/':
            tmp = "call Math.divide 2"
        if operator == '*':
            tmp = 'call Math.multiply 2'
        self.write_new_line(tmp)

    def writeReturn(self):
        self.write_new_line('return')

    def write_new_line(self, new_line):
        self.f.write(new_line + '\n')

    def close(self):
        self.f.close()
