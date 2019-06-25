from Lex import Lex, \
ARITHMETIC_COMMANDS, \
PUSH_OR_POP_COMMANDS, \
MEMORY_SEGMENTS_MAP, \
MEMORY_SEGMENTS \

class CodeWriter:

    def __init__(self, dst_file_name):
        self.f = open(dst_file_name, 'w')
        self.file_prefix = dst_file_name.split('/')[-1].split(".")[0]
        self.label_counter = 0

    # Public
    def write_aritmethic(self, command):
        self._write_comment(command)
        if command == 'add':
            self._write_add()
        elif command == 'sub':
            self._write_sub()
        elif command == 'neg':
            self._write_neg()
        elif command == 'eq':
            self._write_eq()
        elif command == 'lt':
            self._write_lt()
        elif command == 'gt':
            self._write_gt()
        elif command == 'and':
            self._write_and()
        elif command == 'or':
            self._write_or()
        elif command == 'not':
            self._write_not()
        else:
            raise Exception("write_aritmethic with unsupported command = {}".format(command))

    def write_push_pop(self, command, segment, index):
        self._write_comment("{} {} {}".format(command, segment, index))
        if command == 'push':
            self._write_push(segment, index)
        elif command == "pop":
            self._write_pop(segment, index)
        else:
            raise Exception("write_push_pop with unsupported command = {}".format(command))

    def close(self):
        self.f.close()

    # Private

    # Writers
    def _write_raw_asm_code(self, code):
        self.f.write(code + "\n")
    def _write_comment(self, comment):
        self.f.write("// " + comment + "\n")

    # Helpers
    def _new_label(self):
        self.label_counter += 1
        return 'LABEL'+str(self.label_counter)

    def _write_label(self, label):
        self._write_raw_asm_code("({})".format(label))

    def _get_pointer_by_index(self, index):
        if index == '0':
            return "THIS"
        elif index == '1':
            return "THAT"
        else:
            raise Exception("_write_push pointer segment, unsupported pointer - {}".format(index))

    # Basic Universal Operations
    def _write_stack_pointer_inc(self):
        self._write_raw_asm_code("@SP")
        self._write_raw_asm_code("M=M+1")

    def _write_stack_pointer_dec(self):
        self._write_raw_asm_code("@SP")
        self._write_raw_asm_code("M=M-1")

    def _write_load_from_mem(self, var):
        self._write_raw_asm_code("@{}".format(var))
        self._write_raw_asm_code("A=M")

    def _write_load_from_stack(self):
        self._write_load_from_mem('SP')

    def _write_register_to_stack(self, reg):
        self._write_load_from_stack()
        self._write_raw_asm_code("M={}".format(reg))

    def _write_stack_to_register(self, reg):
        self._write_load_from_stack()
        self._write_raw_asm_code("{}=M".format(reg))

    # Used by push constant only
    def _write_index_to_d_register(self, index):
        self._write_raw_asm_code("@{}".format(index))
        self._write_raw_asm_code("D=A")

    # Basic Stack Commands + Segment Handling ,
    def _write_push(self, segment: str, index: int):
        if segment in MEMORY_SEGMENTS:
            self._write_raw_asm_code("@{}".format(index))
            self._write_raw_asm_code("D=A")
            self._write_raw_asm_code("@{}".format(MEMORY_SEGMENTS_MAP[segment]))
            self._write_raw_asm_code("A=D+M")
            self._write_raw_asm_code("D=M")
            self._write_register_to_stack("D")
        elif segment == 'constant':
            self._write_index_to_d_register(index)
            self._write_register_to_stack('D')

        elif segment == 'temp':
            self._write_raw_asm_code("@R{}".format(5+int(index)))
            self._write_raw_asm_code("D=M")
            self._write_register_to_stack("D")
        elif segment == 'static':
            self._write_raw_asm_code("@"+".".join([self.file_prefix, str(index)]))
            self._write_raw_asm_code("D=M")
            self._write_register_to_stack("D")
        elif segment == 'pointer':
            # Load from this/that to register D
            p = self._get_pointer_by_index(index)
            self._write_raw_asm_code("@{}".format(p)) # A = THIS/THAT
            self._write_raw_asm_code("D=M")
            #Commit from register D to stack
            self._write_register_to_stack('D')
        else:
            raise Exception("_write_push unsupported segment - {}".format(segment))

        # Increasing the stack pointer after every push!
        self._write_stack_pointer_inc()


    def _write_pop(self, segment: str, index: int):

        if segment in MEMORY_SEGMENTS:

            self._write_raw_asm_code("@{}".format(index))
            self._write_raw_asm_code("D=A")
            self._write_raw_asm_code("@{}".format(MEMORY_SEGMENTS_MAP[segment]))
            self._write_raw_asm_code("D=D+M")
            self._write_raw_asm_code("@R13")
            self._write_raw_asm_code("M=D")

            self._write_raw_asm_code("@SP")
            self._write_raw_asm_code("AM=M-1")
            self._write_raw_asm_code("D=M")

            self._write_raw_asm_code("@R13")
            self._write_raw_asm_code("A=M")
            self._write_raw_asm_code("M=D")

        elif segment == 'temp':
            self._write_stack_pointer_dec()
            self._write_stack_to_register("D")
            self._write_raw_asm_code("@R{}".format(5+int(index)))
            self._write_raw_asm_code("M=D")

        elif segment == 'static':
            self._write_stack_pointer_dec()
            self._write_stack_to_register("D")
            self._write_raw_asm_code("@"+".".join([self.file_prefix, str(index)]))
            self._write_raw_asm_code("M=D")

        elif segment == 'pointer':
            self._write_stack_pointer_dec()
            # Load from stack to D register
            self._write_stack_to_register("D")
            # Get relevant pointer
            p = self._get_pointer_by_index(index)
            # Write value from D to pointer
            self._write_raw_asm_code("@{}".format(p))
            self._write_raw_asm_code("M=D")
        else:
            raise Exception("_write_pop unsupported segment - {}".format(segment))


    # Basic Arithmetic Commands
    def _write_binary_operation(self, op):
        # First arg to D
        self._write_stack_pointer_dec()
        self._write_stack_to_register("D")
        # Second arg to mem
        self._write_stack_pointer_dec()
        self._write_stack_to_register("A")
        # OP
        self._write_raw_asm_code(op)
        # writing result back to stack
        self._write_register_to_stack("D")
        # update stack pointer
        self._write_stack_pointer_inc()

    def _write_unary_operation(self, op):
        # First arg to D
        self._write_stack_pointer_dec()
        self._write_stack_to_register("D")
        # OP
        self._write_raw_asm_code(op)
        # writing result back to stack
        self._write_register_to_stack("D")
        # update stack pointer
        self._write_stack_pointer_inc()

    def _write_compare_operation(self, op):
        # Subtracting to compare
        self._write_sub()
        # Decreasing to point to the subtraction value in the stack`
        self._write_stack_pointer_dec()
        # Load this value to D register for comperison
        self._write_stack_to_register("D")

        label1 = self._new_label()
        self._write_raw_asm_code("@{}".format(label1))
        self._write_raw_asm_code("D;{}".format(op))

        self._write_register_to_stack("0")

        label2 = self._new_label()
        self._write_raw_asm_code("@{}".format(label2))
        self._write_raw_asm_code("0;{}".format('JMP'))

        self._write_label(label1)
        self._write_register_to_stack("-1")
        self._write_label(label2)
        # update stack pointer
        self._write_stack_pointer_inc()

    def _write_add(self):
        self._write_binary_operation("D=D+A")
    def _write_sub(self):
        self._write_binary_operation("D=A-D")
    def _write_neg(self):
        self._write_unary_operation("D=-D")
    # Compare Commands
    def _write_eq(self):
        self._write_compare_operation('JEQ')
    def _write_gt(self):
        self._write_compare_operation('JGT')
    def _write_lt(self):
        self._write_compare_operation('JLT')
    # Logic Commands
    def _write_and(self):
        self._write_binary_operation("D=D&A")
    def _write_or(self):
        self._write_binary_operation("D=D|A")
    def _write_not(self):
        self._write_unary_operation("D=!D")
