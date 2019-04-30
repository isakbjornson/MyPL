#mypl_interpreter.py
import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as sym_tbl

class ReturnException(Exception): pass

class Interpreter(ast.Visitor):
    """A MyPL interpret visitor implementation"""
    def __init__(self):
        # initialize the symbol table (for ids -> values)
        self.sym_table = sym_tbl.SymbolTable()
        # holds the type of last expression type
        self.current_value = None
        self.heap = {}
        
    def run(self, stmt_list):
        try:
            stmt_list.accept(self)
        except ReturnException:
            pass
        
    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)
        
    def visit_stmt_list(self, stmt_list):
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        self.sym_table.pop_environment()
        

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)
   
    def visit_var_decl_stmt(self, var_decl):
        var_decl.var_expr.accept(self)
        val = self.current_value
        var_name = var_decl.var_id.lexeme
        self.sym_table.add_id(var_decl.var_id.lexeme)
        self.sym_table.set_info(var_decl.var_id.lexeme, val)
        
 
    def visit_assign_stmt(self, assign_stmt): 
        assign_stmt.rhs.accept(self)
        rhs_val = self.current_value
        
        assign_stmt.lhs.accept(self)
        
        self.sym_table.set_info(assign_stmt.lhs, rhs_val)
        
  
    def visit_struct_decl_stmt(self, struct_decl):
        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        env_id = self.sym_table.get_env_id()
        self.sym_table.set_info(struct_decl.struct_id.lexeme, [env_id, struct_decl])
         
       
    def visit_fun_decl_stmt(self, fun_decl):
        env_id = self.sym_table.get_env_id()
        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [env_id, fun_decl])

        
    def visit_return_stmt(self, return_stmt):
        if return_stmt.return_expr is not None:
            return_stmt.return_expr.accept(self)
        else:
            self.current_value = None
        raise ReturnException()
        
                  

    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)
        if self.current_value:
            while_stmt.stmt_list.accept(self)
            while_stmt.accept(self)
  
    def visit_if_stmt(self, if_stmt):
        elseStmt = True
        elifStmt = True     #so that elifs are not executed if if is executed
        if_stmt.if_part.bool_expr.accept(self)   
        if self.current_value:
            if_stmt.if_part.stmt_list.accept(self)
            elseStmt = False
            elifStmt = False
            
        for n in range(len(if_stmt.elseifs)):
            if elifStmt:
                if_stmt.elseifs[n].bool_expr.accept(self)
                if self.current_value:
                    if_stmt.elseifs[n].stmt_list.accept(self)
                    elseStmt = False
                    elifStmt = False
                
        if if_stmt.has_else and elseStmt:
            if_stmt.else_stmts.accept(self)
            
    def visit_simple_expr(self, simple_expr): 
        simple_expr.term.accept(self)
           
    def visit_complex_expr(self, complex_expr):
        rel = complex_expr.math_rel.tokentype
        complex_expr.first_operand.accept(self)
        first_op = self.current_value
        
        if complex_expr.rest != None:
            complex_expr.rest.accept(self)
            second_op = self.current_value
            
            if complex_expr.math_rel != None:
                if rel == token.PLUS:
                    self.current_value = first_op + second_op
                elif rel == token.MINUS:
                    self.current_value = first_op - second_op
                elif rel == token.DIVIDE:
                    self.current_value = first_op / second_op
                elif rel == token.MULTIPLY:
                    self.current_value = first_op * second_op
                elif rel == token.MODULO:
                    self.current_value = first_op % second_op
            else:
                self.__error('Bad math operation', complex_expr.math_rel)
        
    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        lhs = self.current_value
        if bool_expr.bool_rel != None:
            rel = bool_expr.bool_rel.tokentype
            bool_expr.second_expr.accept(self)
            rhs = self.current_value
            if rel == token.EQUAL:
                self.current_value = lhs == rhs
            elif rel == token.GREATER_THAN_EQUAL:
                self.current_value = lhs >= rhs
            elif rel == token.GREATER_THAN:
                self.current_value = lhs > rhs
            elif rel == token.LESS_THAN_EQUAL:
                self.current_value = lhs <= rhs
            elif rel == token.LESS_THAN:
                self.current_value = lhs < rhs
            elif rel == token.NOT_EQUAL:
                self.current_value = lhs != rhs
            else:
                self.current_value = True
        else:
            self.current_value = lhs
                
        if bool_expr.bool_connector != None:
            lhs = self.current_value
            bool_expr.rest.accept(self)
            if bool_expr.bool_connector.tokentype == token.AND:
                self.current_value = lhs and self.current_value
            elif bool_expr.bool_connector.tokentype == token.OR:
                self.current_value = lhs or self.current_value
            
        if bool_expr.negated:
            self.current_value = not self.current_value       
            
    def visit_lvalue(self, lval):
        identifier = lval.path[0].lexeme
        if len(lval.path) == 1:
            self.sym_table.set_info(identifier, self.current_value)
        else:
            oid = self.sym_table.get_info(lval.path[0].lexeme)
            struct_obj = self.heap[oid]
            for path_id in lval.path[1:-1]:
                identifier = path_id.lexeme
                oid = struct_obj[identifier]
                struct_obj = self.heap[oid]
            identifier = lval.path[-1].lexeme
            struct_obj[identifier] = self.current_value
            self.sym_table.set_info(identifier, self.current_value)
             

    def visit_fun_param(self, fun_param):
        identifier = fun_param.param_name.lexeme
        self.sym_table.set_info(identifier, self.current_value)
            
    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_value = int(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_value = float(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_value = True
            if simple_rvalue.val.lexeme == 'false':
                self.current_value = False
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_value = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_value = None

    
    def visit_new_rvalue(self, new_rvalue):
        struct_info = self.sym_table.get_info(new_rvalue.struct_type.lexeme)
        #for v_decl in struct_info[1].var_decls:
            
        env_id = self.sym_table.get_env_id()
        self.sym_table.set_env_id(struct_info[0])
        struct_obj = {}
        self.sym_table.push_environment()
        for v_decl in struct_info[1].var_decls:
            v_decl.accept(self)
            struct_obj[v_decl.var_id.lexeme] = self.current_value
        self.sym_table.pop_environment()
        self.sym_table.set_env_id(env_id)
        oid = id(struct_obj)
        self.heap[oid] = struct_obj
        self.current_value = oid
        
    def visit_call_rvalue(self, call_rvalue):
        # handle built in functions first
        built_ins = ['print', 'length', 'get', 'readi', 'reads', 'readf', 'itof', 'itos', 'ftos', 'stoi', 'stof']
        if call_rvalue.fun.lexeme in built_ins:
            self.__built_in_fun_helper(call_rvalue)
        else:
            fun_info = self.sym_table.get_info(call_rvalue.fun.lexeme)
            env_id = self.sym_table.get_env_id()
            fun_args = []
            for i, arg in enumerate(call_rvalue.args):
                call_rvalue.args[i].accept(self)
                fun_args.append(self.current_value)
            self.sym_table.set_env_id(fun_info[0])
            self.sym_table.push_environment()
            i = 0
            while i < len(fun_args):
                if not self.sym_table.id_exists(fun_info[1].params[i].param_name.lexeme):
                    self.sym_table.add_id(fun_info[1].params[i].param_name.lexeme)
                self.sym_table.set_info(fun_info[1].params[i].param_name.lexeme,fun_args[i])
                i = i+1
            try:
                fun_info[1].stmt_list.accept(self)
            except ReturnException:
                pass
            self.sym_table.pop_environment()
            self.sym_table.set_env_id(env_id)


    
    def visit_id_rvalue(self, id_rvalue):
        var_name = id_rvalue.path[0].lexeme
        var_val = self.sym_table.get_info(var_name)
        self.current_value = var_val
        
        if len(id_rvalue.path) > 1:
            oid = self.current_value
            rval = self.heap[oid]
            for path_id in id_rvalue.path[1:]:
                var_val = rval[path_id.lexeme]
                try:
                    if self.heap[oid]:
                        oid = rval[path_id.lexeme]
                        rval = self.heap[oid]
                except:
                    pass
            self.current_value = var_val
        
    def __built_in_fun_helper(self, call_rvalue):
        fun_name = call_rvalue.fun.lexeme
        arg_vals = []
        #... evaluate each call argument and store in arg_vals ...
        for i, arg in enumerate(call_rvalue.args):
            call_rvalue.args[i].accept(self)
            arg_vals.append(self.current_value)
        # check for nil values
        for i, arg in enumerate(arg_vals):
            if arg is None:
                self.__error('value is nil', call_rvalue.fun)
        # perform each function
        if fun_name == 'print':
            arg_vals[0] = arg_vals[0].replace(r'\n','\n')
            print(arg_vals[0], end = '')
        elif fun_name == 'length':
            self.current_value = len(arg_vals[0])
        elif fun_name == 'get':
            if 0 <= arg_vals[0] < len(arg_vals[1]):
                self.current_value = arg_vals[1][arg_vals[0]]
            else:
                self.__error('out of range', call_rvalue.fun)
        elif fun_name == 'reads':
            self.current_value = input()
        elif fun_name == 'readi':
            try:
                self.current_value = int(input())
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'readf':
            try:
                self.current_value = float(input())
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)
        elif fun_name == 'itof':
            try:
                self.current_value = float(arg_vals[0])
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)
        elif fun_name == 'itos':
            try:
                self.current_value = str(arg_vals[0])
            except ValueError:
                self.__error('bad string value', call_rvalue.fun)
        elif fun_name == 'ftos':
            try:
                self.current_value = str(arg_vals[0])
            except ValueError:
                self.__error('bad string value', call_rvalue.fun)
        elif fun_name == 'stoi':
            try:
                self.current_value = int(arg_vals[0])
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'stof':
            try:
                self.current_value = float(arg_vals[0])
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)