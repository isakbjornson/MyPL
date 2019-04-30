#!/usr/bin/python3
# Author: Isak Bjornson
# Course: CPSC 326, Spring 2019
# Assignment: 4
# mypl_parser.py
# Description: 
#   Checks grammatical correctness and builds an AST
#----------------------------------------------------------------------

import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast as ast


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        
    def parse(self):
        stmt_list_node = ast.StmtList()
        self.__advance()
        self.__stmts(stmt_list_node)
        self.__eat(token.EOS, 'expecting end of file')
        return stmt_list_node
        
    def __advance(self):
        self.current_token = self.lexer.next_token()
        
    def __eat(self, tokentype, error_msg):
        if self.current_token.tokentype == tokentype:
            self.__advance()
        else:
            self.__error(error_msg)
            
    def __error(self, error_msg):
        s = error_msg + ', found "' + self.current_token.lexeme + '" in parser'
        l = self.current_token.line
        c = self.current_token.column
        raise error.MyPLError(error_msg, l, c)
        
    # Beginning of recursive descent functions
    def __stmts(self, stmt_list_node):
        """<stmts> ::= <stmt> <stmts> | e"""
        if self.current_token.tokentype != token.EOS:
            self.__stmt(stmt_list_node)
            self.__stmts(stmt_list_node)
            
    def __stmt(self, stmt_list_node):
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
        if self.current_token.tokentype == token.STRUCTTYPE:
            #struct_node = ast.StructDeclStmt()
            self.__sdecl(stmt_list_node)
        elif self.current_token.tokentype == token.FUN:
            #fun_node = ast.FunDeclStmt()
            self.__fdecl(stmt_list_node)
        else:
            stmt_list_node.stmts.append(self.__bstmt())
    
    def __expr(self):
        rvalues = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID]
        mathrels = [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO]
        
        expr_node = ast.SimpleExpr()
        
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()
            expr_node = self.__expr()
            self.__eat(token.RPAREN, 'expecting ")"')
        elif self.current_token.tokentype in rvalues: 
        
            expr_node.term = self.__rvalue()
            
        if self.current_token.tokentype in mathrels:
            comp_expr_node = ast.ComplexExpr()
            comp_expr_node.first_operand = expr_node
            comp_expr_node.math_rel = self.current_token
            self.__advance()
            comp_expr_node.rest = self.__expr()
            return comp_expr_node
        
        return expr_node
        
            
    
    def __rvalue(self):
        rvals = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL]
        if self.current_token.tokentype in rvals:
            simple_rval_node = ast.SimpleRValue()
            simple_rval_node.val = self.current_token
            self.__advance()
            return simple_rval_node
        elif self.current_token.tokentype == token.NEW:
            self.__advance()
            new_rval_node = ast.NewRValue()
            new_rval_node.struct_type = self.current_token
            self.__eat(token.ID, 'expecting ID')
            return new_rval_node
        else:
            return self.__idrval()
        
    
    def __bstmts (self, stmt_list_node):
        conds = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        vals = [token.VAR, token.SET, token.IF, token.WHILE, token.RETURN]
        if self.current_token.tokentype in conds or self.current_token.tokentype in vals:
            stmt_list_node.stmts.append(self.__bstmt())
            self.__bstmts(stmt_list_node)
    
    def __bstmt(self):
        if self.current_token.tokentype == token.VAR: 
            return self.__vdecl()
        elif self.current_token.tokentype == token.SET:
            return self.__assign()
        elif self.current_token.tokentype == token.IF:
            return self.__cond()
        elif self.current_token.tokentype == token.RETURN:
            return self.__exit()
        elif self.current_token.tokentype == token.WHILE:
            return self.__while()
        else:
            expr_stmt = ast.ExprStmt()
            expr_stmt.expr = self.__expr()
            self.__eat(token.SEMICOLON, 'expecting semicolon')
            return expr_stmt
    
    def __sdecl(self, stmt_list_node):
        self.__eat(token.STRUCTTYPE, 'expecting struct')
        struct_node = ast.StructDeclStmt()
        struct_node.struct_id = self.current_token
        self.__eat(token.ID, 'expecting ID')
        self.__vdecls(struct_node)
        stmt_list_node.stmts.append(struct_node)
        self.__eat(token.END, 'expecting end')
        
    def __vdecls(self, struct_node):
        #create variable array
        if self.current_token.tokentype == token.VAR:
            struct_node.var_decls.append(self.__vdecl())
            self.__vdecls(struct_node)
    
    def __fdecl(self, stmt_list_node):
        self.__eat(token.FUN, 'expecting fun')
        fun_node = ast.FunDeclStmt()
        type = [token.ID, token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]
        if self.current_token.tokentype in type:
            fun_node.return_type = self.current_token
            self.__advance()
        else:
            fun_node.return_type = self.current_token
            self.__eat(token.NIL, 'expecting nil')
        fun_node.fun_name = self.current_token
        self.__eat(token.ID, 'expecting ID')
        self.__eat(token.LPAREN, 'expecting (')
        self.__params(fun_node)
        self.__eat(token.RPAREN, 'expecting rparren')
        self.__bstmts(fun_node.stmt_list)
        stmt_list_node.stmts.append(fun_node)
        self.__eat(token.END, 'expecting end')
        
    def __params(self, fun_node):
        if self.current_token.tokentype == token.ID:
            fun_params_node = ast.FunParam()
            fun_params_node.param_name = self.current_token
            self.__advance()
            self.__eat(token.COLON, 'expecting colon')
            type = [token.ID, token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]
            if self.current_token.tokentype in type:
                fun_params_node.param_type = self.current_token
                self.__advance()
                fun_node.params.append(fun_params_node)
            while self.current_token.tokentype == token.COMMA:
                fun_params_node = ast.FunParam()
                self.__advance()
                fun_params_node.param_name = self.current_token
                self.__eat(token.ID, 'expecting ID')
                self.__eat(token.COLON, 'expecting :')
                if self.current_token.tokentype in type:
                    fun_params_node.param_type = self.current_token
                    self.__advance()
                    fun_node.params.append(fun_params_node)
    
    def __exit(self):
        return_node = ast.ReturnStmt()
        return_node.return_token = self.current_token
        self.__eat(token.RETURN, 'expecting return')
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        if self.current_token.tokentype in types:
            return_node.return_expr = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting semicolon')
        return return_node
        
    
    def __vdecl(self):   
        self.__eat(token.VAR, 'expcecting variable')
        var_node = ast.VarDeclStmt()
        var_node.var_id = self.current_token
        self.__eat(token.ID, 'expecting ID')
        self.__tdecl(var_node)
        self.__eat(token.ASSIGN, 'expecting assign')
        var_node.var_expr = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting semicolon')
        return var_node
    
    def __tdecl(self, var_node):
        if self.current_token.tokentype == token.COLON:
            self.__advance()
            type = [token.ID, token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGTYPE]
            if self.current_token.tokentype in type:
                var_node.var_type = self.current_token
                self.__advance()
    
    def __assign(self):
        self.__eat(token.SET, 'expecting set')
        assign_node = ast.AssignStmt()
        #lvalue_node = ast.LValue()
        self.__lvalue(assign_node)
        self.__eat(token.ASSIGN, 'expecting assign')
        assign_node.rhs = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting semicolon')
        return assign_node
    
    def __lvalue(self, assign_node):
        lvalue_node = ast.LValue()
        lvalue_node.path.append(self.current_token)
        self.__eat(token.ID, 'expecting ID')
        while self.current_token.tokentype == token.DOT:
            self.__advance()
            lvalue_node.path.append(self.current_token)
            self.__eat(token.ID, 'expecting ID')
        assign_node.lhs = lvalue_node
    
    def __cond(self):
        self.__eat(token.IF, 'expecting if')
        if_node = ast.IfStmt()
        if_node.if_part.bool_expr = self.__bexpr()
        
        self.__eat(token.THEN, 'expecting then')

        self.__bstmts(if_node.if_part.stmt_list)
        self.__condt(if_node)
        self.__eat(token.END, 'expecting end')
        return if_node
    
    def __condt(self, if_node):
        if self.current_token.tokentype == token.ELIF:
            self.__advance()
            basic_if_node = ast.BasicIf()
            basic_if_node.bool_expr = self.__bexpr()
            self.__eat(token.THEN, 'expecting then')
        
            self.__bstmts(basic_if_node.stmt_list)
            if_node.elseifs.append(basic_if_node)
            self.__condt(if_node)
        elif self.current_token.tokentype == token.ELSE:
            if_node.has_else = True
            self.__advance()

            self.__bstmts(if_node.else_stmts)
    
    def __while(self):
        self.__eat(token.WHILE, 'expecting while')
        while_node = ast.WhileStmt()
        while_node.bool_expr = self.__bexpr()
        self.__eat(token.DO, 'expecting do')
        self.__bstmts(while_node.stmt_list)
        self.__eat(token.END, 'expecting end')
        return while_node
    
    def __idrval(self):
        id_rval_node = ast.IDRvalue()
        call_rval_node = ast.CallRValue()
        
        id_rval_node.path.append(self.current_token)
        call_rval_node.fun = self.current_token
        
        self.__eat(token.ID, 'expecting ID')
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()
            self.__exprlist(call_rval_node)
            self.__eat(token.RPAREN, 'expecting rparren')
            return call_rval_node
        else:
            while self.current_token.tokentype == token.DOT:
                self.__advance()
                id_rval_node.path.append(self.current_token)
                self.__eat(token.ID, 'expecting ID')
            return id_rval_node
    
    def __exprlist(self, call_rval_node):
        # tokens that can start an expression ...
        types = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.ID, token.LPAREN, token.NIL, token.NEW]
        if self.current_token.tokentype in types:
            call_rval_node.args.append(self.__expr())
            while self.current_token.tokentype == token.COMMA:
                self.__advance()
                call_rval_node.args.append(self.__expr())
    
    def __bexpr(self):
        bool_expr_node = ast.BoolExpr()
        if self.current_token.tokentype == token.NOT:
            bool_expr_node.negated = True
            self.__advance()
            bool_expr_node = self.__bexpr()
            self.__bexprt(bool_expr_node)
        elif self.current_token.tokentype == token.LPAREN:
            self.__advance()
            bool_expr_node.first_expr = self.__bexpr()
            self.__eat(token.RPAREN, 'expecting rparren')
            self.__bconnct(bool_expr_node)
        else:
            bool_expr_node.first_expr = self.__expr()
            self.__bexprt(bool_expr_node)
        return bool_expr_node
        
    
    def __bexprt(self, bool_expr_node):
        boolrel = [token.EQUAL, token.LESS_THAN, token.GREATER_THAN, token.GREATER_THAN_EQUAL, token.LESS_THAN_EQUAL, token.NOT_EQUAL]
        if self.current_token.tokentype in boolrel:
            bool_expr_node.bool_rel = self.current_token
            self.__advance()
            bool_expr_node.second_expr = self.__expr()
            
        self.__bconnct(bool_expr_node)
    
    def __bconnct(self, bool_expr_node):
        if self.current_token.tokentype == token.AND:
            bool_expr_node.bool_connector = self.current_token
            self.__advance()
            
            bool_expr_node.rest = self.__bexpr()
        elif self.current_token.tokentype == token.OR:
            bool_expr_node.bool_connector = self.current_token
            self.__advance()
           
            bool_expr_node.rest = self.__bexpr()