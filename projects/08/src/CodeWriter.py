from Lex import Lex, \
ARITHMETIC_COMMANDS, \
PUSH_OR_POP_COMMANDS, \
MEMORY_SEGMENTS_MAP, \
MEMORY_SEGMENTS \

class CodeWriter:

    def __init__(self, dst_file_name):
        self.f = open(dst_file_name, 'w')
        self.update_file_name(dst_file_name)
        self.label_counter = 0
        self.current_func_name = ""

    # Public
    def update_file_name(self, file_name):
        self.file_prefix = file_name.split('/')[-1].split(".")[0]

    def bootstrap(self):
        # SP=256 // address = 0
        self._write_raw_asm_code("@256") # A=256
        self._write_raw_asm_code("D=A") # D=256
        self._write_raw_asm_code("@SP") # A=256
        self._write_raw_asm_code("M=D") # D=256
        # update the value from D onto SP which is in stack place 0
        # call Sys.init // address = 1
        self.write_call('call', 'Sys.init', '0')

    def close(self):
        self.f.close()

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

    def write_if_goto(self, command, label):
        self._write_comment("{} {}".format(command, label))
        # pop from stackt to D
        self._write_stack_pointer_dec()
        self._write_stack_to_register("D")
        # print a command
        # label = self._new_custom_label(label)
        self._write_raw_asm_code("@{}".format(label))
        # check if D is 1/0 and jump!
        self._write_raw_asm_code("D;JNE")

    def write_goto(self, command, label):
        self._write_comment("{} {}".format(command, label))
        # Uncoditional JUMP
        # label = self._new_custom_label(label)
        self._write_raw_asm_code("@{}".format(label))
        self._write_raw_asm_code("0;JMP")

    def write_label(self, command, label):
        self._write_comment("{} {}".format(command, label))
        # Simple Label write (LABEL)
        # label = self._new_custom_label(label)
        self._write_label(label)

    def write_function(self, command, func_name, local_var_count):
        self._write_comment("{}: name {}, with {} local vars".format(command, func_name, local_var_count))
        self.func_name = func_name
        # All local vars init with 0
        # Our working stack is empty
        # We must push a value on the stack before return

        #########
        # 1) self._write_label(func_name)
        # 2) for i in local_var_count:
        #       push constant 0
        #########
        # label = self._new_custom_label(func_name)
        self._write_label(func_name)
        for _ in range(int(local_var_count)):
            self.write_push_pop('push', 'constant', '0')

    def write_return(self):
        self._write_comment("Return")
        # Return to the caller -  the value that was computed by the call function
        # It is required that the callee always pushes a value before we Return
        # We need to remove the argument that was passed to the callee - pop according to arg count
        # We need to push the calculation onto the stack

        # When we are seeing return, we know that the value that we need to return is in the top of the stack
        # We need to move (copy) it to the place that argument 0 of the function was saved
        # We want to restore the segment pointers of the  caller
        # clear the stack - the callee will be returned
        # update the SP for the caller
        # we need to jump to the return address within the caller's code


        #########
        bck_const = "FRAME_BCK"
        return_address_const = "@RET_"+self._new_label()#"@RETURN_ADDRESS"
        # 1) create temp var - endFrame = LCL // assgin LCL value to it
        self._write_raw_asm_code("@LCL")
        self._write_raw_asm_code("D=M")
        self._write_raw_asm_code("@"+bck_const)
        self._write_raw_asm_code("M=D")
        # 2) returnAddress = *(endFrame - 5)
        self._write_raw_asm_code("@5")
        self._write_raw_asm_code("A=D-A")
        self._write_raw_asm_code("D=M")
        self._write_raw_asm_code(return_address_const)
        self._write_raw_asm_code("M=D")
        # 3) *ARG = pop() ?// reposition the return value for the caller - pop_to_arg_zero
        self._write_pop("argument", '0')
        # 4) SP = ARG + 1 //
        self._write_raw_asm_code("@ARG")
        self._write_raw_asm_code("D=M")
        self._write_raw_asm_code("@SP")
        self._write_raw_asm_code("M=D+1")
        # 5) THAT = *(endFrame -1)
        self._write_copy_between_mem_offset_one(bck_const, "THAT")
        # 6) THIS = *(endFrame -2)
        self._write_copy_between_mem_offset_one(bck_const, "THIS")
        # 7) ARG = *(endFrame -3)
        self._write_copy_between_mem_offset_one(bck_const, "ARG")
        # 8) LCL = *(endFrame -4)
        self._write_copy_between_mem_offset_one(bck_const, "LCL")
        # 9) goto returnAddress
        self._write_raw_asm_code(return_address_const)
        self._write_raw_asm_code("A=M")
        self._write_raw_asm_code("0;JMP")
        #########

    def write_call(self, command, func_name, arg_count):
        self._write_comment("{} function: {} with {} arguments".format(command, func_name, arg_count))
        # Save the state of the caller
        # 1) The working stack of the caller must be saved for later use
        # 2) The working segments of the caller must be saved too
        # 3) save the return address within the caller `call`
        # All of these 3 stuff are called the caller Frame
        # How do we save it? push them all onto the stack!
        # push return address
        # push LCL, push RAG, push THIS, push THAT - memory segments!

        #########

        # 1) push returnAddress -  push a label onto the stack
        return_address = self._new_label()
        self._write_push('constant', return_address)
        # 2) push LCL -
        self._write_mem_value_to_d_register('LCL')
        self._write_register_to_stack('D')
        self._write_stack_pointer_inc()
        # 3) push ARG
        self._write_mem_value_to_d_register('ARG')
        self._write_register_to_stack('D')
        self._write_stack_pointer_inc()
        # 4) push THIS
        self._write_mem_value_to_d_register('THIS')
        self._write_register_to_stack('D')
        self._write_stack_pointer_inc()
        # 5) push THAT
        self._write_mem_value_to_d_register('THAT')
        self._write_register_to_stack('D')
        self._write_stack_pointer_inc()
        # 6) ARG = SP - 5 - arg_count (5 = returnAddress + LCL + ARG + THIS + THAT)
        self._write_raw_asm_code("@SP")
        # self._write_raw_asm_code("A=M")
        self._write_raw_asm_code("D=M")
        self._write_raw_asm_code("@5")
        self._write_raw_asm_code("D=D-A")
        self._write_raw_asm_code("@{}".format(arg_count))
        self._write_raw_asm_code("D=D-A")

        self._write_raw_asm_code("@ARG")
        self._write_raw_asm_code("M=D")
        # 7) LCL = SP - reposition of LCL
        self._write_copy_between_mem('SP', 'LCL')
        # 8) goto func_name
        self._write_raw_asm_code("@{}".format(func_name))
        self._write_raw_asm_code("0;JMP")
        # 9) self._write_label(returnAddress)
        self._write_label(return_address)
        #########

    # Private

    # Writers
    def _write_raw_asm_code(self, code):
        self.f.write(code + "\n")
    def _write_comment(self, comment):
        self.f.write("// " + comment + "\n")
    def _write_label(self, label):
        self._write_raw_asm_code("({})".format(label))

    # Helpers
    def _new_custom_label(self, base_label):
        return "{}.{}${}".format(self.file_prefix, self.current_func_name, base_label)

    def _new_label(self):
        self.label_counter += 1
        return 'LABEL'+str(self.label_counter)

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

    def _write_mem_value_to_d_register(self, index):
        self._write_raw_asm_code("@{}".format(index))
        self._write_raw_asm_code("D=M")

    def _write_d_register_to_mem(self, var):
        self._write_raw_asm_code("@{}".format(var))
        self._write_raw_asm_code("M=D")
    ##
    def _write_copy_between_mem(self, src, dest):
        self._write_raw_asm_code("@{}".format(src))
        self._write_raw_asm_code("D=M")
        self._write_raw_asm_code("@{}".format(dest))
        self._write_raw_asm_code("M=D")

    def _write_copy_between_mem_offset_one(self, src, dest):
        self._write_raw_asm_code("@{}".format(src))
        self._write_raw_asm_code("AM=M-1")
        self._write_raw_asm_code("D=M")
        self._write_raw_asm_code("@{}".format(dest))
        self._write_raw_asm_code("M=D")

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
        # decreasing the stack pointer before every pop!
        self._write_stack_pointer_dec()

        if segment in MEMORY_SEGMENTS:
            self._write_raw_asm_code("@{}".format(index))
            self._write_raw_asm_code("D=A")
            self._write_raw_asm_code("@{}".format(MEMORY_SEGMENTS_MAP[segment]))
            self._write_raw_asm_code("D=D+M")
            self._write_raw_asm_code("@R13")
            self._write_raw_asm_code("M=D")

            self._write_stack_to_register('D')

            self._write_raw_asm_code("@R13")
            self._write_raw_asm_code("A=M")
            self._write_raw_asm_code("M=D")
        elif segment == 'temp':
            self._write_stack_to_register("D")
            self._write_raw_asm_code("@R{}".format(5+int(index)))
            self._write_raw_asm_code("M=D")
        elif segment == 'static':
            self._write_stack_to_register("D")
            self._write_raw_asm_code("@"+".".join([self.file_prefix, str(index)]))
            self._write_raw_asm_code("M=D")
        elif segment == 'pointer':
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
    def _write_two_args_operation(self, op):
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

    def _write_single_arg_operation(self, op):
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
        self._write_two_args_operation("D=D+A")
    def _write_sub(self):
        self._write_two_args_operation("D=A-D")
    def _write_neg(self):
        self._write_single_arg_operation("D=-D")
    # Compare Commands
    def _write_eq(self):
        self._write_compare_operation('JEQ')
    def _write_gt(self):
        self._write_compare_operation('JGT')
    def _write_lt(self):
        self._write_compare_operation('JLT')
    # Logic Commands
    def _write_and(self):
        self._write_two_args_operation("D=D&A")
    def _write_or(self):
        self._write_two_args_operation("D=D|A")
    def _write_not(self):
        self._write_single_arg_operation("D=!D")
