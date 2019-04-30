import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table

class TypeChecker(ast.Visitor):
    """A MyPL type checker visitor implementation where struct types
    take the form: type_id -> {v1:t1, ..., vn:tn} and function types
    take the form: fun_id -> [[t1, t2, ..., tn,], return_type]
    """
    def __init__(self):
        # initialize the symbol table (for ids -> types)
        self.sym_table = symbol_table.SymbolTable()
        # current_type holds the type of the last expression type
        self.current_type = None
        # global env (for return)
        self.sym_table.push_environment()
        # set global return type to int
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', token.INTTYPE)
        # load in built-in function types
        self.sym_table.add_id('print')
        self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL])
        
        self.sym_table.add_id('length')
        self.sym_table.set_info('length', [[token.STRINGTYPE], token.NIL])
        
        self.sym_table.add_id('get')
        self.sym_table.set_info('get', [[token.INTTYPE, token.STRINGTYPE], token.INTTYPE])#
        
        self.sym_table.add_id('reads')
        self.sym_table.set_info('reads', [token.STRINGTYPE])
        
        self.sym_table.add_id('readi')
        self.sym_table.set_info('readi', [token.STRINGTYPE])
        
        self.sym_table.add_id('readf')
        self.sym_table.set_info('readf', [token.STRINGTYPE])
        
        self.sym_table.add_id('itos')
        self.sym_table.set_info('itos', [token.INTTYPE, token.STRINGTYPE])
        
        self.sym_table.add_id('ftos')
        self.sym_table.set_info('ftos', [token.FLOATTYPE, token.STRINGTYPE])
        
        self.sym_table.add_id('itof')
        self.sym_table.set_info('itof', [token.INTTYPE, token.FLOATTYPE])
        
        self.sym_table.add_id('stoi')
        self.sym_table.set_info('stoi', [token.STRINGTYPE, token.INTTYPE])#
        
        self.sym_table.add_id('stof')
        self.sym_table.set_info('stof', [token.STRINGTYPE, token.FLOATTYPE])#
        
    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)
        
    def visit_stmt_list(self, stmt_list):
        # add new block (scope)
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        # remove new block
        self.sym_table.pop_environment()
        
    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)
        
    ####    
    def visit_var_decl_stmt(self, var_decl):
        #print(var_decl.var_expr.term.val)
        var_decl.var_expr.accept(self)
        expr_type = self.current_type
        if (var_decl.var_type != None):
            if var_decl.var_type.tokentype == token.ID:
                v_type = var_decl.var_type.lexeme
            else: 
                v_type = var_decl.var_type.tokentype
        else:
            v_type = expr_type
        
        if expr_type != token.NIL and expr_type != v_type:
            print(expr_type)
            print(v_type)
        
            msg = 'mismatch type in variable expression'
            self.__error(msg, var_decl.var_id)
            
        self.sym_table.add_id(var_decl.var_id.lexeme)
        #print(var_decl.var_id.lexeme)
        self.sym_table.set_info(var_decl.var_id.lexeme, v_type)
    
            
    
    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        rhs_type = self.current_type
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type
        if rhs_type != token.NIL and rhs_type != lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])
      
    
    def visit_struct_decl_stmt(self, struct_decl):
        #self.sym_table.push_environment()
        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        struct_params = {}
        for var_decl in struct_decl.var_decls:
            var_decl.accept(self)
            struct_params[var_decl.var_id.lexeme] = self.current_type
        self.sym_table.set_info(struct_decl.struct_id.lexeme, struct_params)
        
        #self.sym_table.push_environment()
        
    def visit_fun_decl_stmt(self, fun_decl):
        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        fun_params = []
        if fun_decl.return_type is None:
            return_type = token.NIL
        else:
            return_type = fun_decl.return_type
            if not return_type is str:
                return_type = return_type.tokentype
        self.sym_table.push_environment()
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', return_type)
        for params in fun_decl.params:  
            params.accept(self)
            fun_params.append(self.current_type)
            
        fun_decl.stmt_list.accept(self)
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [fun_params, return_type])

        self.sym_table.pop_environment()
    
    
    
    def visit_return_stmt(self, return_stmt):
        #if return_stmt.return_expr != None:
        return_stmt.return_expr.accept(self)
        return_type = self.current_type
        #print(return_type)
        
        expected_type = self.sym_table.get_info('return')
        if return_type != token.NIL and return_type != expected_type:
            msg = "return types don't match"
            self.__error(msg, return_stmt.return_token)
        
    
    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)

        while_stmt.stmt_list.accept(self)
        
    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.bool_expr.accept(self)
        
        if_stmt.if_part.stmt_list.accept(self)
        for elseif in if_stmt.elseifs:
            elseif.stmt_list.accept(self)
        if if_stmt.has_else:
            if_stmt.else_stmts.accept(self)
    
    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)
        
        
    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        first_type = self.current_type
        rel = complex_expr.math_rel.tokentype
        complex_expr.rest.accept(self)
        second_type = self.current_type
        
        if rel == token.MODULO:
            if (first_type == token.INTTYPE and second_type == token.INTTYPE):
                pass
            else:
                msg = "improper values, can only do int, int"
                self.__error(msg, complex_expr.math_rel)
        if rel == token.DIVIDE or rel == token.MULTIPLY or rel == token.MINUS:
            if (first_type == token.INTTYPE and second_type == token.INTTYPE) or (first_type == token.FLOATTYPE and second_type == token.FLOATTYPE): 
                pass
            else:
                msg = "improper values, can only int, int, or float, float"
                self.__error(msg, complex_expr.math_rel)
        if rel == token.PLUS:
            if (first_type == token.INTTYPE and second_type == token.INTTYPE) or (first_type == token.FLOATTYPE and second_type == token.FLOATTYPE) or (first_type == token.STRINGTYPE and second_type == token.STRINGTYPE):
                pass
            else:
                msg = "improper values, can only int, int, or float, float or string, string"
                self.__error(msg, complex_expr.math_rel)
        
    
    def visit_bool_expr(self, bool_expr):

        bool_expr.first_expr.accept(self)
        first_expr_type = self.current_type
        
        if bool_expr.bool_rel is None:
            if first_expr_type != token.BOOLTYPE:
                msg = 'missing bool expression'
                self.__error(msg, bool_expr.bool_rel)
            
        else:
            bool_expr.second_expr.accept(self)
            second_expr_type = self.current_type
            
            if bool_expr.bool_rel.tokentype == token.EQUAL or bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                pass
            elif first_expr_type != second_expr_type:
                msg = 'mismatching comparison types'
                self.__error(msg, bool_expr.bool_rel)
                

        if bool_expr.bool_connector is not None:
            bool_expr.rest.accept(self)
        
    
    def visit_lvalue(self, lval):
        # check the first id in the path
        var_token = lval.path[0]
        if not self.sym_table.id_exists(var_token.lexeme):
            msg = 'undefined variable "%s"' % var_token.lexeme
            self.__error(msg, var_token)
        self.current_type = self.sym_table.get_info(var_token.lexeme)
        # check if struct for a longer path expression
    
    def visit_fun_param(self, fun_param):
        self.sym_table.add_id(fun_param.param_name.lexeme)
        self.sym_table.set_info(fun_param.param_name.lexeme, fun_param.param_type.tokentype)

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_type = token.INTTYPE
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_type = token.FLOATTYPE
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_type = token.BOOLTYPE
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_type = token.STRINGTYPE
            #if self.sym_table.id_exists(simple_rvalue.val.lexeme):
            #    self.current_type = self.sym_table.get_info(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_type = token.NIL

      
    def visit_new_rvalue(self, new_rvalue):
        if not self.sym_table.id_exists(new_rvalue.struct_type.lexeme):
            msg = 'Struct ID not declared'
            self.__error(msg, new_rvalue)
        self.current_type = new_rvalue.struct_type.lexeme
        
        
        
    def visit_call_rvalue(self, call_rvalue):
        if not self.sym_table.id_exists(call_rvalue.fun.lexeme):
            msg = 'Struct ID not declared'
            self.__error(msg, call_rvalue.fun)
        for expr in call_rvalue.args:
            expr.accept(self)
        
        
    
    def visit_id_rvalue(self, id_rvalue):
        for i in id_rvalue.path:
            if not self.sym_table.id_exists(i.lexeme):
                msg = 'ID rval not declared'
                self.__error(msg, i)
        self.current_type = self.sym_table.get_info(id_rvalue.path[-1].lexeme)
    
    