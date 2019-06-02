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
        f_type = self._agent.cur # 'constructor' | 'function' | 'method' kw

        self._agent.advance() # 'void' | 'type' kw/identifier
        f_name = self._agent.advance() # 'subroutineName' identifier

        self._symbol_table.startSubRoutine()
        if f_type == 'method':
            self._symbol_table.define(['this', self._class_name, 'argument'])

        self._agent.advance() # '('
        self._agent.advance()

        if self._agent.cur != ')': # Extra validation for edge cases
            self.compileParameterList()

        self.compileSubroutineBody(f_type, f_name)

    # '{' varDec* statements '}'
    def compileSubroutineBody(self, f_type, f_name):
        self._agent.advance() # '{' symbol
        token = self._agent.advance() # Statements

        # Run through each of the subroutine variable declarations.
	    # Note that there could be zero or more of them
        if self._agent.cur == 'var':
            self.compileVarDec()

        local_variables = self._symbol_table.varCount('local')

        # VM Code preps
        self._agent.writeFunction(self._class_name, f_name, local_variables)
        # Handling Constructor
        if f_name == 'new':
            no_of_fields = self._symbol_table.varCount('field')
            self._agent.writePush('constant', no_of_fields)
            self._agent.writeCall('Memory', 'alloc', 1)
            self._agent.writePop('pointer', 0)
        # Handling instance Method
        if f_type == 'method':
            self._agent.writePush('argument', 0)
            self._agent.writePop('pointer', 0)

        if token != '}': # Extra validation for edge cases
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
            self._symbol_table.define([identifier, id_type, 'argument'])

            # Check if it's a comma, process if it is.
		    # If it's not, it's the last variable name, so skip it
            token = self._agent.advance()
            if token == ',':
                self._agent.advance()
                self.compileParameterList()

    # 'var' type varName (',' varName)* ';'
    def compileVarDec(self):

        # Loop to deal with all variable names, including the first one.
        while self._agent.cur == 'var':
            id_type = self._agent.advance() # 'int' | 'bool' | 'string' | 'type' kw/idenitfier
            identifier = self._agent.advance() # 'varName' identifier
            self._symbol_table.define([identifier, id_type, 'local'])
            self._agent.advance() # ',' symbol

            # Handling case of int var1, var2, var3; all vars should have the same type
            while self._agent.cur == ',':
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

        is_array = self._agent.advance() == '['

        if is_array:
            self._agent.advance()
            self.compileExpression()
            self._agent.writePush(segment, index)
            self._agent.writeArithmatic('add')
            self._agent.advance()

        self._agent.advance() # '=' symbol
        self.compileExpression()

        # Got a little help from github to crack it down...
        # https://github.com/havivha/Nand2Tetris/blob/master/11/JackAnalyzer/Parser.py (line 246)
        if is_array:
            self._agent.writePop('temp', 0)
            self._agent.writePop('pointer', 1)
            self._agent.writePush('temp', 0)
            self._agent.writePop('that', 0)
        else:
            self._agent.writePop(segment, index)

        self._agent.advance() # ';' symbol

    # 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
    def compileIf(self):
        self._dynamic_label_counter += 1 # for linear label names
        self._agent.advance() # '(' symbool
        self._agent.advance() # So curr will be ready

        self.compileExpression()

        self._agent.writeArithmatic('~')
        label = ".".join([self._class_name, 'if',  str(self._dynamic_label_counter), 'LABEL1'])
        self._agent.writeIfGoto(label)

        goto_label = ".".join([self._class_name, 'if', str(self._dynamic_label_counter), 'LABEL2'])

        self._agent.advance()
        if self._agent.advance() != '}': # Making sure
            self.compileStatements()

        self._agent.writeGoto(goto_label)
        self._agent.writeLabel(label)

        # Only process an else clause if it exists
        if self._agent.advance() == "else": # 'else' kw
            self._agent.advance() # '{' symbol
            if self._agent.advance() != '}':
                self.compileStatements()

            self._agent.advance() # '{' symbol

        self._agent.writeLabel(goto_label)

    # 'while' '(' expression ')' '{' statements '}'
    def compileWhile(self):
        self._dynamic_label_counter += 1 # for linear label names

        label = '.'.join([self._class_name, 'w', str(self._dynamic_label_counter), 'LABEL1'])
        self._agent.writeLabel(label)

        self._agent.advance() # '(' symbool
        self._agent.advance() # Preps fpr expression

        self.compileExpression()

        self._agent.writeArithmatic('~')

        if_label = '.'.join([self._class_name, 'w', str(self._dynamic_label_counter), 'LABEL2'])
        self._agent.writeIfGoto(if_label)

        self._agent.advance() # '{' symbol

        if self._agent.advance() != '}':
            self.compileStatements()

        self._agent.writeGoto(label)
        self._agent.writeLabel(if_label)

        self._agent.advance()

    # 'do' subroutineCall ';
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
        arg_count = 0
        id_type = None
        if token == ".":
            method_or_function = self._agent.advance()
            self._agent.advance() # '('
            id_type = self._symbol_table.typeOf(identifier)

        # Deal with '(' as the next token, i.e. with a regular subroutineCall
        # subroutineName '(' expressionList ')'
        if token == '(':
            class_name = self._class_name
            method_or_function = identifier
            arg_count += 1
            self._agent.writePush('pointer', '0')

        token = self._agent.advance()

        if id_type:
            segment = self._symbol_table.kindOf(identifier)
            index = self._symbol_table.indexOf(identifier)
            self._agent.writePush(segment, index)
            arg_count += 1
            class_name = id_type

        if token != ')':
            arg_count += self.compileExpressionList() # Returns the number of arguemnt we need to add


        self._agent.writeCall(class_name, method_or_function, arg_count)
        self._agent.advance()

        self._agent.writePop('temp', '0')
        self._agent.advance()

    # 'return' expression? ';'
    def compileReturn(self):

        if self._agent.advance() == ';':
            # Deal with end function
            self._agent.writePush('constant', '0')
        else:
            # Deal with an optional expression
            self.compileExpression()

        self._agent.writeReturn()
        self._agent.advance()

    # (expression (',' expression)* )?
    def compileExpressionList(self):

        # The next thing after an expression list is always a closing parantheses
	    # If we're not at a closing parantheses, then there's at least one expression here
	    # Otherwise, compile at least one expression
        args_to_add = 1
        self.compileExpression()

        # If there's a comma, there's at least two expresseions here, Parse all of them
        while self._agent.cur == ",":
            args_to_add += 1
            self._agent.advance() # ',' symbol
            self.compileExpression()

        return args_to_add

    # term (op term)*
    def compileExpression(self):

        # An expression is always, at the very least, a ter
        self.compileTerm()

        possible_operator = self._agent.cur
        # Deal with operators / entity operators (&;lt etc.)
        if possible_operator in opperators:
            # Process each operator and compile the term after it
            self._agent.advance()
            self.compileTerm()
            self._agent.writeArithmatic(possible_operator) # 'op' symbol

    # integerConstant | stringConstant | keywordConstant | varName |
    # varName '[' expression ']' | subroutineCall | '(' expression ')' | (unaryOp term)
    def compileTerm(self):
        token = self._agent.cur


        # Since this is the most complicated part in the compiler, it's broken
	    # into parts that often repeat themselves. Easier debugging and all

        # Deal with integer constants
        if isIntegerConstant(token):
            self._agent.writePush('constant', token)

        # Deal with keyword constants
        elif token == 'true':
            self._agent.writePush('constant', '1')
            self._agent.writeArithmatic('neg')
        elif token in ['false', 'null']:
            self._agent.writePush('constant', '0')
        elif token == 'this':
            self._agent.writePush('pointer', '0')

        # Dealing with Unary operators
        elif token == '-':
            self._agent.advance()
            self.compileTerm()
            self._agent.writeArithmatic('neg')
            return
        elif token == "~":
            if self._agent.advance() != '(':
                self.compileTerm()
            else:
                self._agent.advance()
                self.compileExpression()
                self._agent.advance()
            self._agent.writeArithmatic('not')
            return

        # Deal with '(' expression ')'
        elif token == "(":
            token = self._agent.advance()
            self.compileExpression()

       # Deal with '[' as the next token, i.e. with referencing an index in an array
	   # varName '[' expression ']'
        elif self._agent.peek() == "[":
            index = self._symbol_table.indexOf(token)
            segment = self._symbol_table.kindOf(token)
            self._agent.writePush(segment, index)

            self._agent.advance()

            token = self._agent.advance()
            self.compileExpression()

            self._agent.writeArithmatic('add')
            self._agent.writePop('pointer', '1')
            self._agent.writePush('that', '0')

       # Deal with '.' as the next token, i.e. with a dot-refernce subroutineCall
	   #  ( className | varName) '.' subroutineName '(' expressionList ')'
        elif self._agent.peek() == ".":
            identifier = token
            self._agent.advance()
            f_name = self._agent.advance()
            self._agent.advance()
            self._agent.advance()

            arg_count = 0

            class_name = identifier
            id_type = self._symbol_table.typeOf(identifier)

            if id_type:
                segment = self._symbol_table.kindOf(identifier)
                index = self._symbol_table.indexOf(identifier)
                self._agent.writePush(segment, index)
                arg_count += 1
                class_name = id_type

            if self._agent.cur != ")":
                arg_count += self.compileExpressionList() # Returns the number of arguemnt we need to add

            self._agent.writeCall(class_name, f_name, arg_count)

        # Deal with simple strings, i.e stringConstant | varName - more exact strings expressions
        elif '$' in token :
            # Clearing string $ indicators
            token = str.replace(token, '$', '')
            # as many chars as in the striped token constants
            self._agent.writePush('constant', len(token))
            # New String Class
            self._agent.writeCall('String', 'new', 1)
            for idx in range(0, len(token)):
                self._agent.writePush('constant', ord(token[idx])) # ord get the HASCII value of a character
                self._agent.writeCall('String', 'appendChar', 2)
        else:
            index = self._symbol_table.indexOf(token)
            segment = self._symbol_table.kindOf(token)
            if segment is None:
                print("fail to fetch segment from symble table for token - {}".format(token))
            if index is None:
                print("fail to fetch index from symble table for token - {}".format(token))
            self._agent.writePush(segment, index)

        self._agent.advance()

    # classVarDec: ('static' | 'field' ) type varName (' , ' varName)* ' ; '
    def compileClassVarDec(self):
        class_var = self._agent.cur # 'static' | 'field' kw

        type = self._agent.advance()
        identifier = self._agent.advance()
        self._symbol_table.define([identifier, type, class_var])

        self._agent.advance()

        # Check if it's a comma, process if it is.
		# If it's not, it's the last variable name, so skip it
        while self._agent.cur == ',':
            identifier =  self._agent.advance() # 'varName' identifier
            self._symbol_table.define([identifier, type, class_var])
            self._agent.advance()

        if self._agent.advance() in ['field', 'static']:
            self.compileClassVarDec()
