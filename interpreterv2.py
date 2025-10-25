from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

from typing import Optional, Dict, Any 
from element import Element

generate_image = False


class Environment:
    def __init__(self):
        self.env = {}

    # define new variable at function scope
    def fdef(self, varname):
        if self.exists(varname):
            return False
        self.env[varname] = None
        return True

    def exists(self, varname):
        return varname in self.env

    def get(self, varname):
        if varname in self.env:
            return self.env[varname]
        return None

    def set(self, varname, value):
        if not self.exists(varname):
            return False
        self.env[varname] = value
        return True


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)

        self.funcs = {}  # {name:element,}
        self.env = Environment()
        self.ops = {"-", "+"}

    def run(self, program):
        ast = parse_program(program, generate_image)

        for func in ast.get("functions"):
            self.funcs[func.get("name")] = func

        if "main" not in self.funcs:
            super().error(ErrorType.NAME_ERROR, "main function not found")

        for statement in self.funcs["main"].get("statements"):
            kind = statement.elem_type

            if kind == self.VAR_DEF_NODE:
                self.__run_vardef(statement)
            elif kind == "=":
                self.__run_assign(statement)
            elif kind == self.FCALL_NODE:
                self.__run_fcall(statement)

    def __run_vardef(self, statement):
        name = statement.get("name")

        if not self.env.fdef(name):
            super().error(ErrorType.NAME_ERROR, "variable already defined")

    def __run_assign(self, statement):
        name = statement.get("var")

        value = self.__eval_expr(statement.get("expression"))
        if not self.env.set(name, value):
            super().error(ErrorType.NAME_ERROR, "variable not defined")

    def __run_fcall(self, statement):
        fcall_name, args = statement.get("name"), statement.get("args")

        if fcall_name == "inputi":
            if len(args) > 1:
                super().error(ErrorType.NAME_ERROR, "too many arguments for inputi")

            if args:
                super().output(str(self.__eval_expr(args[0])))

            return int(super().get_input())

        if fcall_name == "print":
            out = ""

            for arg in args:
                out += str(self.__eval_expr(arg))

            super().output(out)

            return 0  # undefined behavior

        super().error(ErrorType.NAME_ERROR, "unknown function")

    def __eval_expr(self, expr):
        kind = expr.elem_type

        if kind == self.INT_NODE or kind == self.STRING_NODE:
            return expr.get("val")

        elif kind == self.QUALIFIED_NAME_NODE:
            var_name = expr.get("name")

            value = self.env.get(var_name)
            if value is None:
                super().error(ErrorType.NAME_ERROR, "variable not defined")

            return value

        elif kind == self.FCALL_NODE:
            return self.__run_fcall(expr)

        elif kind in self.ops:
            l, r = self.__eval_expr(expr.get("op1")), self.__eval_expr(expr.get("op2"))

            if isinstance(l, str) or isinstance(r, str):
                super().error(
                    ErrorType.TYPE_ERROR, "invalid operand types for arithmetic"
                )

            if kind == "-":
                return l - r

            elif kind == "+":
                return l + r






class Interpreter(InterpreterBase):
    def __init__(self, console_output: bool =True, inp:str|None = None, trace_output: bool=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor
        self.env = Environment()
        self.user_function_def : Dict[str,Element] = {} # name: element.
        self.ops = {"-", "+"}
        


    def run(self, program):
        ast=parse_program(program,False) # returns the program node of ast, have a list in its dict which holds all function nodes

        #Only the statements inside main are executed in Project #1. no need to check for other funcitons 
        ### TODO: Update to hold the user defined functions inside self.function_def 

        for func in ast.get('functions'):
            self.user_function_def[func.get('name')]=func # this also pushes main into the list

        if "main" not in self.user_function_def:
            super().error(ErrorType.NAME_ERROR, "main function not found")

        main_func= self.user_function_def["main"]

        if main_func == None:
                super().error(ErrorType.NAME_ERROR,"No main() function was found")
        
        else:
            self.run_func(main_func)
        

        
        
        



    def run_func(self, func_node:Element):
        stms=func_node.get('statements')
        if stms != None:
            for statement_node in stms:
                self.run_statement(statement_node)



    def run_statement(self, statement_node: Element):
        kind = statement_node.elem_type
        if kind==self.VAR_DEF_NODE:
            self.var_def_statement(statement_node)
        elif kind=='=':
            self.assign_statement(statement_node)
        elif kind==self.FCALL_NODE:
            self.func_call_statement(statement_node)


        ### TODO: for future project, check user function definition validity and call it

        return


    def var_def_statement(self, statement_node:Element):

        var_name=statement_node.get("name")
        
        if not self.env.fdef(var_name):
            super().error(ErrorType.NAME_ERROR, "variable already defined")
    



    def assign_statement(self, statement_node:Element):

        var_name=statement_node.get('var')
        expr=statement_node.get('expression')

        value = self.evaluate_expression(statement_node.get("expression")) # type: ignore

        if not self.env.set(var_name, value):
            super().error(ErrorType.NAME_ERROR, "variable not defined")

        return
    

    
    def func_call_statement(self, statement_node:Element) -> None|Any: # function can return anything, or nothing

        func_name=statement_node.get('name')
        args=statement_node.get("args")

        # by the AST tree graph and brista tests, all arguments should be in expression form; else -> NAME_ERROR
        if func_name=='print':
            out = ""
            for arg in args: # type: ignore 
                out += str(self.evaluate_expression(arg)) #no matter waht expression we returned (int or string), cast it to string
                super().output(out)

        
        elif func_name=='inputi':
            if args: 
                if len(args)>1:
                    super().error(ErrorType.NAME_ERROR,f"No inputi() function found that takes > 1 parameter")
                elif len(args)==1:
                    strout=""
                    for arg in args:
                        strout=self.evaluate_expression(arg)
                    super().output(strout)
            # reuturn the input as a string using th e super class method
            s= super().get_input()

            if s:
                return int (s) # Need to cast to int ourselves.
        
        #else log error for unknown functoin.
        
        super().error(ErrorType.NAME_ERROR, f"Unknown function")
    

    def evaluate_expression(self, expression_node:Element):
        kind = expression_node.elem_type
        if kind==self.INT_NODE or kind == self.STRING_NODE:
            return expression_node.get('val')
        
        elif kind==self.QUALIFIED_NAME_NODE:
            var_name=expression_node.get('name')
            value = self.env.get(var_name)
            if value is None:
                super().error(ErrorType.NAME_ERROR, "variable not defined")
            return value #fetch variable from our dictionary
        
        elif kind == self.FCALL_NODE:
            return self.func_call_statement(expression_node) #call function.
        
        elif kind in self.ops:
            # This evealuation step automatically handles any nested functions or +/- such as (9+(7-8)) reflected in AST after parsing
            
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            if (not isinstance(op1,int)) or (not isinstance(op2,int)): #f an expression attempts to operate on a string (e.g., 5 + "foo"), then your interpreter must generate an error
                super().error(ErrorType.TYPE_ERROR, f"adding non integers")
            
            if kind == "-":
                return op1 - op2

            elif kind == "+":
                return op1 + op2


        return
    
    
    






