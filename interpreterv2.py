from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

from typing import Optional, Dict, Any, Tuple
from element import Element

generate_image = False

# NOTE: I am just using value None as nil in the project unless otherwise specified.

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
    def __init__(self, console_output: bool =True, inp:str|None = None, trace_output: bool=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor
        self.env = Environment()

        self.user_function_def : Dict[Tuple[str,int],Element] = {} # (name, arg#): element.

        self.integer_ops_bi = {"-", "/","*"} # NOTE: use // for integer division and truncation in python. 
        # self.integer_ops_un = {"-"} # covered in NEG_NODE already!
        self.integer_ops_com = {"<","<=",">",">="}

        self.boolean_ops_bi = {"||","&&"}
        self.boolean_ops_un ={"!"}


        self.string_or_int_ops_bi= {"+"}

        self.ops_com = {"==","!="}
        


    def run(self, program):
        ast=parse_program(program,False) # returns the program node of ast, have a list in its dict which holds all function nodes

        #Only the statements inside main are executed in Project #1. no need to check for other funcitons 
        ### TODO: Update to hold the user defined functions inside self.function_def 

        for func in ast.get('functions'):
            # use name AND arg count as identification
            name=func.get('name')
            args=len(func.get('args'))
            self.user_function_def[(name,args)]=func # this also pushes main into the list

        if ("main",0) not in self.user_function_def:
            super().error(ErrorType.NAME_ERROR, f"main function not found")

        main_func= self.user_function_def[("main",0)]

        if main_func == None:
                super().error(ErrorType.NAME_ERROR,f"No main() function was found")
        
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
        elif kind==self.IF_NODE:
            self.if_statement_execution(statement_node)
        elif kind==self.WHILE_NODE:
            self.while_statement_execution(statement_node)
        elif kind==self.RETURN_NODE:
            self.return_statement_execution(statement_node)


        ### TODO: for future project, check user function definition validity and call it




    def var_def_statement(self, statement_node:Element):

        var_name=statement_node.get("name")
        
        if not self.env.fdef(var_name):
            super().error(ErrorType.NAME_ERROR, "variable already defined")
    



    def assign_statement(self, statement_node:Element):

        var_name=statement_node.get('var')
        expr=statement_node.get('expression')

        value = self.evaluate_expression(expr) # type: ignore

        if not self.env.set(var_name, value):
            super().error(ErrorType.NAME_ERROR, "variable not defined")

        return
    

    
    def func_call_statement(self, statement_node:Element) -> None|Any: # function can return anything, or nothing

        func_name=statement_node.get('name')
        args=statement_node.get("args")

        # by the AST tree graph and brista tests, all arguments should be in expression form; else -> NAME_ERROR
        if func_name=='print':
            # TODO: support int, string, boolean (true or false)
            out = ""

            for arg in args: #type: ignore
                out += str(self.evaluate_expression(arg))

            super().output(out)

            return 0  # undefined behavior

        
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
            
            elif func_name=='inputs':
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
                    return str (s) # I guess input is always a string so this coersion is unnecessary, but I want to make sure it fits the type.
        
        #else log error for unknown functoin.
        
        super().error(ErrorType.NAME_ERROR, f"Unknown function")
    

    def evaluate_expression(self, expression_node:Element):
        kind = expression_node.elem_type
        if kind==self.INT_NODE or kind == self.STRING_NODE or kind == self.BOOL_NODE:
            return expression_node.get('val')
        # for boolean node, self.dict has 'val' mapping to True or False (booleans print as true/false), parser already mapped the raw text to True or False!
        
        elif kind == self.NIL_NODE:
            return None
        
        elif kind==self.QUALIFIED_NAME_NODE:
            var_name=expression_node.get('name')
            value = self.env.get(var_name)
            if value is None:
                super().error(ErrorType.NAME_ERROR, "variable not defined")
            return value #fetch variable from our dictionary
        
        elif kind == self.FCALL_NODE:
            return self.func_call_statement(expression_node) #call function.
        
        elif kind == self.NEG_NODE:
            op=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            if not isinstance(op,int):
                super().error(ErrorType.TYPE_ERROR, f"int unary negation of non-integer")
            return - op
        
        elif kind == self.
        elif kind in self.integer_ops_bi:
            # This evealuation step automatically handles any nested functions or +/- such as (9+(7-8)) reflected in AST after parsing
            
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            if ((not isinstance(op1,int)) or (not isinstance(op2,int) )): #f an expression attempts to operate on a string (e.g., 5 + "foo"), then your interpreter must generate an error
                super().error(ErrorType.TYPE_ERROR, f"integer arithmitic on non integers")
            
            if kind == "-":
                return op1 - op2

            elif kind == "/":
                return op1 // op2
            elif kind == "*":
                return op1 * op2
        
        elif kind in self.string_or_int_ops_bi:
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            if ((not isinstance(op1,int)) or (not isinstance(op2,int) )):
                if ((not isinstance(op1,str)) or (not isinstance(op2,str) )):
                    super().error(ErrorType.TYPE_ERROR, f"add or concatenating non int and non string")
            
            #python + works the same for strign and int for our purposes
            return op1+op2 #type: ignore
        
            


        

            
        return
    

    def if_statement_execution(self, expression_node:Element):
        # TODO: if condition not Boolean, return Type error
        cond=expression_node.get('condition')
        if not isinstance(cond,bool):
            super().error(ErrorType.TYPE_ERROR, f"if condition not boolean")

        if cond:
            to_exex=expression_node.get('statements')
        else:
            to_exex=expression_node.get('else_statements')

        if to_exex:
                for stm in to_exex:
                    self.run_statement(stm)


        return
    

    def while_statement_execution(self, expression_node:Element):
        # TODO: if condition not Boolean, return Type error
        return
    

    def return_statement_execution(self, expression_node:Element):
        # if something to return, return it
        # terminate current function immediately (if in main, terminate program)
        return
    
    
    




