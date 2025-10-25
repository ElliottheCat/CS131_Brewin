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
        self.variable_name_to_value: Dict [str,Any] = {}
        self.user_function_def : Dict[str,Element] = {} # name: element.
    
        


    def run(self, program):
        ast=parse_program(program,False) # returns the program node of ast, have a list in its dict which holds all function nodes

        #Only the statements inside main are executed in Project #1. no need to check for other funcitons 
        ### TODO: Update to hold the user defined functions inside self.function_def 

        funcs = ast.get('functions')
        main_func: Element|None=None
        if funcs == None:
            super().error(ErrorType.NAME_ERROR,"No function was found in program")
        else:
            for func in funcs:
                if func.get('name')=='main':
                    main_func=func


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
        
        if statement_node.elem_type=='vardef':
            self.var_def_statement(statement_node)
        elif statement_node.elem_type=='=':
            self.assign_statement(statement_node)
        elif statement_node.elem_type=='fcall':
            self.func_call_statement(statement_node)


        ### TODO: for future project, check user function definition validity and call it
        return


    def var_def_statement(self, statement_node:Element):

        var_name=statement_node.get("name")
        if var_name in self.variable_name_to_value:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} defined more than once")
        
        if not isinstance(var_name,str):
            super().error(ErrorType.TYPE_ERROR, f"Variable name {var_name} not string from parser")
            return
        #Define variable name in variable dictionary
        self.variable_name_to_value[var_name]=None
        return
    



    def assign_statement(self, statement_node:Element):

        var_name=statement_node.get('var')
        expr=statement_node.get('expression')

        if var_name not in self.variable_name_to_value:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")

        if expr==None:
            super().error(ErrorType.NAME_ERROR, f"No expression to be assigned; parser error.")
        expr_val=self.evaluate_expression(expr)
        self.variable_name_to_value[var_name]=expr_val

        return
    

    
    def func_call_statement(self, statement_node:Element)-> None | int:

        func_name=statement_node.get('name')

        # by the AST tree graph and brista tests, all arguments should be in expression form; else -> NAME_ERROR
        if func_name=='print':
            args=statement_node.get('args')
            if args == None:
                # nothing but an empty line
                super().output("")
            else:
                string_to_output=""
                for arg in args:
                    val=self.evaluate_expression(arg)
                    string_to_output+=str(val) #no matter waht expression we returned (int or string), cast it to string
                super().output(string_to_output)

        
        elif func_name=='inputi':
            args=statement_node.get('args')
            
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
        else:
            super().error(ErrorType.NAME_ERROR, f"Unknown function")
    

    def evaluate_expression(self, expression_node:Element):

        if expression_node.elem_type=='string':
            return expression_node.get('val')
        
        elif expression_node.elem_type=='int':
            return expression_node.get('val')
        
        elif expression_node.elem_type=='qname':
            var_name=expression_node.get('name')
            if var_name not in self.variable_name_to_value:
                super().error(ErrorType.NAME_ERROR, f"expression variable name undefined")
            return self.variable_name_to_value[var_name] #fetch variable from our dictionary
        
        elif expression_node.elem_type=='fcall':
            return self.func_call_statement(expression_node) #call function.
        
        elif expression_node.elem_type=='+':
            arg1=expression_node.get('op1')
            arg2=expression_node.get('op2')
            if (not isinstance(arg1,Element)) or (not isinstance(arg2,Element)):
                super().error(ErrorType.TYPE_ERROR, f"+ argument is not an element")
            
            # This evealuation step automatically handles any nested functions or +/- such as (9+(7-8)) reflected in AST after parsing
            op1=self.evaluate_expression(arg1)
            op2=self.evaluate_expression(arg2)
            if (not isinstance(op1,int)) or (not isinstance(op2,int)): #f an expression attempts to operate on a string (e.g., 5 + "foo"), then your interpreter must generate an error
                super().error(ErrorType.TYPE_ERROR, f"adding non integers")

            sum=op1+op2

            return sum
        elif expression_node.elem_type=='-':
            arg1=expression_node.get('op1')
            arg2=expression_node.get('op2')
            if (not isinstance(arg1,Element)) or (not isinstance(arg2,Element)):
                super().error(ErrorType.TYPE_ERROR, f"+ argument is not an element")
            
            # This evealuation step automatically handles any nested functions or +/- such as (9+(7-8))
            op1=self.evaluate_expression(arg1)
            op2=self.evaluate_expression(arg2)
            if (not isinstance(op1,int)) or (not isinstance(op2,int)):
                super().error(ErrorType.TYPE_ERROR, f"adding non integers")

            dif=op1-op2

            return dif


        return
    
    
    






