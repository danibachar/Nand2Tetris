'''
Tom Granot-Scalosub - 308020734
Daniel Bachar - 201242120
Compiler - Compilation Engine
'''

from SymbolTable import SymbolTable
from JackTokenizer import *

statments = ['let','if','while','do','return']
entityOp = ['&lt;', '&gt;', '&quot;', '&amp;']
opperators = ['+','-','*','/','&','|','<','>','='] + entityOp


class CompliationEngine(object):

    def __init__(self, agent):
        self._agent = agent
        self._symbol_table = SymbolTable()
        self._dynamic_label_counter = 0

        # pre processing
        if self._agent.advance() != 'class':# 'class' kw
            print("Warning - __init__")

        self._class_name = self._agent.advance() # 'class_name' identifier

        self._agent.advance() # '{' sym

    # class: 'class' className '{' classVarDec* subroutineDec* '}'
    def compileClass(self):

        self._agent.advance() #

        # Run throuth each of the class variable declarations.
	    # Note that there coule be zero or more of them
        while self._agent.cur in ['field', 'static']:
            self.compileClassVarDec()

        # Run through each of the class variable declarations.
	    # Note that there could be zero or more of them
        while self._agent.cur in ['function', 'method', 'constructor']:
            self.compileSubroutineDec()

        self._agent.close()

    # ('constructor' | 'function' | 'method') ('void' | type) subroutineName
    # '(' parameterList ')' subroutineBody
    def compileSubroutineDec(self):
        function_type = self._agent.cur # 'constructor' | 'function' | 'method' kw

        self._agent.advance() # 'void' | 'type' kw/identifier
        function_name = self._agent.advance() # 'subroutineName' identifier

        self._symbol_table.startSubRoutine()
        if function_type == 'method':
            self._symbol_table.define(['this', self._class_name, 'argument'])

        self._agent.advance() # '('
        self._agent.advance() # 'first argument'

        if self._agent.cur != ')':
            self.compileParameterList()

        self.compileSubroutineBody(function_type, function_name)

    # '{' varDec* statements '}'
    def compileSubroutineBody(self, function_type, function_name):
        self._agent.advance() # '{' symbol
        token = self._agent.advance() # Statements

        # Run through each of the subroutine variable declarations.
	    # Note that there could be zero or more of them
        if self._agent.cur == 'var':
            self.compileVarDec()

        local_variables = self._symbol_table.varCount('local')

        # VM Code preps
        self._agent.writeFunction(self._class_name, function_name, local_variables)
        if function_name == 'new':
            no_of_fields = self._symbol_table.varCount('field')
            self._agent.writePush('constant', no_of_fields)
            self._agent.writeCall('Memory', 'alloc', 1)
            self._agent.writePop('pointer', 0)
        if function_type == 'method':
            self._agent.writePush('argument', 0)
            self._agent.writePop('pointer', 0)

        if token != '}':
            self.compileStatements()

        self._agent.advance()  # '}' symbol

    def compileParameterList(self):
        # The parameter list could be empty, so basically while there
	    # are still variables in the listcharacter is not a closing bracket
	    # For each parameter in the list
        token = self._agent.cur
        while (token in ['int','char','boolean']) or isIdentifier(token):
            id_type = self._agent.cur # 'int' | 'bool' | 'string' | 'type' kw/identifier
            identifier = self._agent.advance() # 'varName' identifier
            identifier_details = [identifier, id_type, 'argument']
            self._symbol_table.define(identifier_details)

            # Check if it's a comma, process if it is.
		    # If it's not, it's the last variable name, so skip it
            token = self._agent.advance()
            if token == ',':
                self._agent.advance()
                self.compileParameterList()

    # 'var' type varName (',' varName)* ';'
    def compileVarDec(self):
        while self._agent.cur == 'var':
            id_type = self._agent.advance() # 'int' | 'bool' | 'string' | 'type' kw/idenitfier
            identifier = self._agent.advance() # 'varName' identifier
            self._symbol_table.define([identifier, id_type, 'local'])
            self._agent.advance() # ',' symbol

            while self._agent.cur == ',':
                identifier_details = []
                identifier = self._agent.advance() # 'varName' identifier
                self._symbol_table.define([identifier, id_type, 'local'])
                self._agent.advance()# ',' symbol

            self._agent.advance() # ';' closing symbol

    def compileStatements(self):

        # Compile all the statements - in begining of file
        while self._agent.cur in statments:
            if self._agent.cur == 'let':
                self.compileLet()
            elif self._agent.cur == 'if':
                self.compileIf()
            elif self._agent.cur == 'while':
                self.compileWhile()
            elif self._agent.cur == 'do':
                self.compileDo()
            elif self._agent.cur == 'return':
                self.compileReturn()
            else:
                print("ERROR IN COMPILING A STATEMENT, EXIT NOW. GIVEN CURSOR: ", token)

    # 'let' varName ('[' expression ']')? '=' expression ';'
    def compileLet(self):

        identifier = self._agent.advance() # 'varName' identifier
        segment = self._symbol_table.kindOf(identifier)
        index = str(self._symbol_table.indexOf(identifier))

        token = self._agent.advance()
        if_array = False
        # Hanlding Arrays
        if token == '[':
            if_array = True
            token = self._agent.advance()
            self.compileExpression() # ']'
            self._agent.writePush(segment, index)
            self._agent.writeArithmatic('+')
            self._agent.advance()

        self._agent.advance()
        self.compileExpression()

        # Got a little help from to crack it down...
        # https://github.com/havivha/Nand2Tetris/blob/master/11/JackAnalyzer/Parser.py (line 246)
        if if_array:
            self._agent.writePop('temp', 0)
            self._agent.writePop('pointer', 1)
            self._agent.writePush('temp', 0)
            self._agent.writePop('that', 0)
        else:
            self._agent.writePop(segment, index)

        self._agent.advance()

    def compileIf(self):
        self._dynamic_label_counter += 1 # for linear label names
        self._agent.advance() # '(' symbool
        self._agent.advance() # So curr will be ready

        self.compileExpression()

        self._agent.writeArithmatic('~')
        label = self._class_name + '.' + 'if.' + str(self._dynamic_label_counter) + '.LABEL1'
        self._agent.writeIfGoto(label)

        goto_label = self._class_name + '.' + 'if.' + str(self._dynamic_label_counter) + '.LABEL2'

        self._agent.advance()
        if self._agent.advance() != '}': # Making sure
            self.compileStatements()

        self._agent.writeGoto(goto_label)
        self._agent.writeLabel(label)

        # optional else Command
        if self._agent.advance() == "else": # 'else' kw
            self._agent.advance() # '{' symbol
            if self._agent.advance() != '}':
                self.compileStatements()

            self._agent.advance()

        self._agent.writeLabel(goto_label)

    # 'while' '(' expression ')' '{' statements '}'
    def compileWhile(self):
        self._dynamic_label_counter += 1 # for linear label names

        label = '.'.join([self._class_name, 'w', str(self._dynamic_label_counter), 'LABEL1'])
        self._agent.writeLabel(label)

        self._agent.advance() # '(' symbool
        self._agent.advance() # Preps fpr expression

        self.compileExpression()

        self._agent.writeArithmatic('~') # ~cond

        if_label = '.'.join([self._class_name, 'w', str(self._dynamic_label_counter), 'LABEL2'])
        self._agent.writeIfGoto(if_label)

        self._agent.advance() # '{' symbol

        if self._agent.advance() != '}':
            self.compileStatements()

        self._agent.writeGoto(label)
        self._agent.writeLabel(if_label)

        self._agent.advance()

    def compileDo(self):
        identifier = self._agent.advance()
        token = self._agent.advance() # like peek - '.' or '('

        # Deal with subroutine call ad-hoc. Might not be the correct way to go about it,
        # Since the documentation does not mention what to do with this.
        # Regardless, this is the same as in `compileTerm`, minus the return
        # Statements and the closing term tag


        # Deal with '.' as the next token, i.e. with a dot-refernce subroutineCall
        #  ( className | varName) '.' subroutineName '(' expressionList ')'
        class_name = identifier
        no_of_arguments = 0
        if token == ".":
            method_or_function = self._agent.advance()
            self._agent.advance() # '('
            id_type = self._symbol_table.typeOf(identifier)

        # Deal with '(' as the next token, i.e. with a regular subroutineCall
        # subroutineName '(' expressionList ')'
        if token == '(':
            class_name = self._class_name
            method_or_function = identifier
            no_of_arguments += 1
            self._agent.writePush('pointer', '0')
            id_type = None

        token = self._agent.advance()

        if id_type != None:
            segment = self._symbol_table.kindOf(identifier)
            index = self._symbol_table.indexOf(identifier)
            self._agent.writePush(segment, index)
            no_of_arguments += 1
            class_name = id_type

        no_arguments = 0
        if token != ')':
            no_of_arguments += self.compileExpressionList() # Returns the number of arguemnt we need to add


        self._agent.writeCall(class_name, method_or_function, no_of_arguments)
        self._agent.advance() # ';'

        # 'void functions will return constant 0 which should be discarded'
        self._agent.writePop('temp', '0')
        self._agent.advance()

    def compileReturn(self):

        if self._agent.advance() == ';':
            # Deal with end function
            self._agent.writePush('constant', '0')
        else:
            # Deal with expression
            self.compileExpression()

        self._agent.writeReturn()
        self._agent.advance()

    def compileExpressionList(self):

        args_to_add = 1
        self.compileExpression() # returns ','

        while self._agent.cur == ",":
            args_to_add += 1
            self._agent.advance()
            self.compileExpression()

        return args_to_add

    def compileExpression(self):
        # An expression is always, at the very least, a term
        self.compileTerm()

        possible_operator = self._agent.cur
        # Deal with operators / entity operators (&;lt etc.)
        if possible_operator in opperators:
            self._agent.advance()
            self.compileTerm()
            self._agent.writeArithmatic(possible_operator)

    def compileTerm(self):
        token = self._agent.cur

        if isIntegerConstant(token):
            self._agent.writePush('constant', token)
        elif token == 'true':
            self._agent.writePush('constant', '1')
            self._agent.writeArithmatic('-', 'NEG')
        elif token in ['false', 'null']:
            self._agent.writePush('constant', '0')
        elif token == 'this':
            self._agent.writePush('pointer', '0')
        elif token == '-':
            return self.compileNeg()
        elif token == "~":
            return self.compileNot()
        elif token == "(":
            token = self._agent.advance() # Term token
            self.compileExpression() # Returns ')'
        elif self._agent.peek() == "[":
            index = self._symbol_table.indexOf(token)
            segment = self._symbol_table.kindOf(token)
            self._agent.writePush(segment, index)

            self._agent.advance() # '['

            token = self._agent.advance()
            self.compileExpression() # return value is ']'

            self._agent.writeArithmatic('+')
            self._agent.writePop('pointer', '1')
            self._agent.writePush('that', '0')

        elif self._agent.peek() == ".":
            identifier = token
            self._agent.advance() # '.'
            method_or_function = self._agent.advance()

            self._agent.advance() # '('

            token = self._agent.advance()
            no_of_arguments = 0

            class_name = identifier
            id_type = self._symbol_table.typeOf(identifier)

            if id_type != None:
                segment = self._symbol_table.kindOf(identifier)
                index = self._symbol_table.indexOf(identifier)
                self._agent.writePush(segment, index)
                no_of_arguments += 1
                class_name = id_type

            if token != ")":
                no_of_arguments += self.compileExpressionList() # Returns the number of arguemnt we need to add

            self._agent.writeCall(class_name, method_or_function, no_of_arguments)
        elif '$' in token :
            token = str.replace(token, '$', '')
            self._agent.writePush('constant', len(token))
            self._agent.writeCall('String', 'new', 1)
            for idx in range(0, len(token)):
                self._agent.writePush('constant', ord(token[idx]))
                self._agent.writeCall('String', 'appendChar', 2)
        else:
            index = self._symbol_table.indexOf(token)
            segment = self._symbol_table.kindOf(token)
            if segment is None:
                print("fail to fetch segment from symble table for token - {}".format(token))
            if index is None:
                print("fail to fetch index from symble table for token - {}".format(token))
            self._agent.writePush(segment, index)

        token = self._agent.advance()
        return token

    def compileNeg(self):
        token = self._agent.advance()
        token = self.compileTerm()
        self._agent.writeArithmatic('-', 'NEG')
        return token

    def compileNot(self):
        token = self._agent.advance() # '('?
        if token != '(':
            token = self.compileTerm()
        else:
            token = self._agent.advance() #
            self.compileExpression() # returns inner ')' res
            token = self._agent.advance()  # outer ')'

        self._agent.writeArithmatic('~')
        return token

    def compileClassVarDec(self):
        class_var_modifer = self._agent.cur # 'field' or 'static'

        # primitive or user defined class
        class_var_type = self._agent.advance()
        identifier = self._agent.advance()
        self._symbol_table.define([identifier, class_var_type, class_var_modifer])

        token = self._agent.advance()

        while token == ',':
            identifier =  self._agent.advance()
            self._symbol_table.define([identifier, class_var_type, class_var_modifer])
            token = self._agent.advance()

        token = self._agent.advance()

        if token in ['field', 'static']:
            return self.compileClassVarDec()

        return token
