import mypl_token as token
import mypl_error as error

class Lexer(object):
    
    def __init__(self, input_stream):
        self.line = 1
        self.column = 0
        self.input_stream = input_stream
    def __peek(self):
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol
        
    def __read(self):
        return self.input_stream.read(1)
        
    def next_token(self):        
        while self.__peek().isspace():
            if self.__peek() == '\n':
                self.line +=1
                self.column = 0
            self.__read()
            self.column +=1
            
        symbol = self.__read()
        self.column +=1
        
        if symbol == '#':
            while not self.__peek() == '\n':
                self.__read()
            self.line +=1
            self.__read()
            return self.next_token()
        
        if symbol == '':
            return token.Token(token.EOS, '', self.line, self.column - 1)
            
        elif symbol == '=':
            if self.__peek() == '=':
                symbol += self.__read()
                col = self.column
                self.column +=1
                return token.Token(token.EQUAL, symbol, self.line, col)
            else:
                return token.Token(token.ASSIGN, symbol, self.line, self.column)
        
        elif symbol == ',':
            return token.Token(token.COMMA, symbol, self.line, self.column)
            
        elif symbol == ':':
            return token.Token(token.COLON, symbol, self.line, self.column)
            
        elif symbol == '/':
            return token.Token(token.DIVIDE, symbol, self.line, self.column)
            
        elif symbol == '.':
            return token.Token(token.DOT, symbol, self.line, self.column)
            
        elif symbol == '>':
            if self.__peek() == '=':
                symbol += self.__read()
                col = self.column
                self.column +=1
                return token.Token(token.GREATER_THAN_EQUAL, symbol, self.line, col)
            else: 
                return token.Token(token.GREATER_THAN, symbol, self.line, self.column)
            
        elif symbol == '<':
            if self.__peek() == '=':
                symbol += self.__read()
                col = self.column
                self.column +=1
                return token.Token(token.LESS_THAN_EQUAL, symbol, self.line, col)
            else:
                return token.Token(token.LESS_THAN, symbol, self.line, self.column)
            
        elif symbol == '!':
            if self.__peek() == '=':
                symbol += self.__read()
                col = self.column
                self.column +=1
                return token.Token(token.NOT_EQUAL, symbol, self.line, col)
            
        elif symbol == '(':
            return token.Token(token.LPAREN, symbol, self.line, self.column)
            
        elif symbol == ')':
            return token.Token(token.RPAREN, symbol, self.line, self.column)
            
        elif symbol == '-':
            return token.Token(token.MINUS, symbol, self.line, self.column)
            
        elif symbol == '%':
            return token.Token(token.MODULO, symbol, self.line, self.column)
            
        elif symbol == '*':
            return token.Token(token.MULTIPLY, symbol, self.line, self.column)
            
        elif symbol == '+':
            return token.Token(token.PLUS, symbol, self.line, self.column)
            
        elif symbol == ';':
            return token.Token(token.SEMICOLON, symbol, self.line, self.column)
        
        elif symbol.isdigit():
            flt = False
            col = self.column - 1
            
            if symbol == '0' and self.__peek().isdigit():
                print(error.MyPLError('unexpected number', self.line, self.column))
                exit()
            
            while self.__peek().isdigit() or self.__peek() == ".":
                symbol += self.__read()
                self.column +=1
                if symbol[-1] == ".":
                    if flt:
                        print(error.MyPLError('invalid number', self.line, col))
                        exit()
                    elif not self.__peek().isdigit():
                        print(error.MyPLError('missing digit in float value', self.line, self.column))
                        exit()
                    else:
                        symbol += self.__read()
                        self.column +=1
                        flt = True
                        
            if self.__peek().isalpha():
                print (error.MyPLError('unexpected symbol', self.line, self.column)) 
                exit()
             
            if flt:
                return token.Token(token.FLOATVAL, symbol, self.line, col)
            else:
                return token.Token(token.INTVAL, symbol, self.line, col)
                
        elif symbol == '"':
            col = self.column -1
            if self.__peek() == '"':
                symbol += self.__read()
                self.column +=1
                return token.Token(token.STRINGVAL, '', self.line, col)
            symbol = self.__read()
            while not self.__peek() == '"':
                symbol += self.__read()
                self.column +=1
                if self.__peek() == '':
                    print("Improper string")
                    break
            self.__read()
            self.column +=1
            return token.Token(token.STRINGVAL, symbol, self.line, col)
        
        elif symbol.isalpha():
            col = self.column -1
            while self.__peek().isalpha() or self.__peek().isdigit() or self.__peek() == '_':
                symbol += self.__read()
                self.column +=1
            
            if symbol == 'and':
                return token.Token(token.AND, symbol, self.line, col)
            elif symbol == 'or':
                return token.Token(token.OR, symbol, self.line, col)
            elif symbol == 'not':
                return token.Token(token.NOT, symbol, self.line, col)
            elif symbol == 'bool':
                return token.Token(token.BOOLTYPE, symbol, self.line, col)
            elif symbol == 'int':
                return token.Token(token.INTTYPE, symbol, self.line, col)
            elif symbol == 'float':
                return token.Token(token.FLOATTYPE, symbol, self.line, col)
            elif symbol == 'string':
                return token.Token(token.STRINGTYPE, symbol, self.line, col)
            elif symbol == 'struct':
                return token.Token(token.STRUCTTYPE, symbol, self.line, col)
            elif symbol == 'while':
                return token.Token(token.WHILE, symbol, self.line, col)
            elif symbol == 'do':
                return token.Token(token.DO, symbol, self.line, col)
            elif symbol == 'if':
                return token.Token(token.IF, symbol, self.line, col)
            elif symbol == 'then':
                return token.Token(token.THEN, symbol, self.line, col)
            elif symbol == 'else':
                return token.Token(token.ELSE, symbol, self.line, col)
            elif symbol == 'elif':
                return token.Token(token.ELIF, symbol, self.line, col)
            elif symbol == 'end':
                return token.Token(token.END, symbol, self.line, col)
            elif symbol == 'fun':
                return token.Token(token.FUN, symbol, self.line, col)
            elif symbol == 'var':
                return token.Token(token.VAR, symbol, self.line, col)
            elif symbol == 'set':
                return token.Token(token.SET, symbol, self.line, col)
            elif symbol == 'return':
                return token.Token(token.RETURN, symbol, self.line, col)
            elif symbol == 'new':
                return token.Token(token.NEW, symbol, self.line, col)
            elif symbol == 'nil':
                return token.Token(token.NIL, symbol, self.line, col)
            elif symbol == 'true':
                return token.Token(token.BOOLVAL, symbol, self.line, col)
            elif symbol == 'false':
                return token.Token(token.BOOLVAL, symbol, self.line, col)
            else:
                return token.Token(token.ID, symbol, self.line, col)
                
        