from brewparse import parse_program
from intbase import InterpreterBase, ErrorType
from typing import Optional, Tuple, Dict, List,Any
from element import Element
# need data structures:
# Need a variable hash map
# TA: Also need a structure to hold all functions you see (is this necessary?)
    # for project 2..

class Interpreter(InterpreterBase):
    def __init__(self, console_output: bool =True, inp:str|None = None, trace_output: bool=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor
        self.variable_name_to_value: Dict [str,Any] = {}
        self.user_function_def : Dict[str,Any] = {} # STORE USER DEFINED FUNCTION IN THIS!!!

        


    def run(self, program):
        ast=parse_program(program,False) # returns the program node of ast, have a list in its dict which holds all function nodes

        
        """ SPEC
        A Function node will have the following fields:
            self.elem_type whose value is 'func', identifying this node as a Function node
            self.dict which holds up to three keys:
                'name' → a string containing the name of the function (e.g., 'main')
                'args' → a (possibly empty) list of Argument nodes (ignored by this interpreter)
                'statements' → a list of Statement nodes, representing each of the statements that make up the function, in their order of execution

        To interpret a function, you must interpret all of its statements from top to bottom
        """
        ### Only the statements inside main are executed in Project #1.
        ### TODO: Update to hold the user defined functions inside self.function_def ###

        """
        If a program does not have a main function defined, then you must generate an error of type ErrorType.NAME_ERROR by calling InterpreterBase.error()
        """

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
        """The main function must have at least one statement defined within it. You do NOT need to check for this, all of our main functions that we test with will have at least one statement.
        
        Every function consists of zero or more statements. Statements in Brewin v1 come in three forms:

            variable definition statements
            assignment statements
            function call statements
        """
        if stms != None:
            for statement_node in stms:
                self.run_statement(statement_node)



    def run_statement(self, statement_node: Element):
        """
        Statement Nodes
            Variable Definition Statement
                Declares a new variable in the current environment.
                A Statement node representing a variable definition will have the following fields:
                    self.elem_type whose value is 'vardef'
                    self.dict which holds one key:
                        'name' → a string holding the name of the variable to be defined
            Assignment Statement
                Assigns the result of an expression to an existing variable.
                A Statement node representing an assignment will have the following fields:
                    self.elem_type whose value is '='
                    self.dict which holds two keys:
                        'var' → the name of the variable on the left-hand side of the assignment (e.g., 'x' for x = 1 + y;)
                        'expression' → an Expression node whose value is computed and stored into the named variable
                The target variable must already have been declared via a variable definition statement.
            
            Function Call Statement
                Invokes a built-in function for its side effects (its return value, if any, is ignored when used as a statement).
                A Statement node representing a function call will have the following fields:
                    self.elem_type whose value is 'fcall'
                    self.dict which holds two keys:
                        'name' → the name of the function to be called (e.g., 'print', 'inputi')
                        'args' → a list containing zero or more Expression nodes representing arguments to the function call

                REMEMBER TO CHECK IF FUNCTION IS DEFINED OR BUILDIN
        """
        if statement_node.elem_type=='vardef':
            self.var_def_statement(statement_node)
        elif statement_node.elem_type=='=':
            self.assign_statement(statement_node)
        elif statement_node.elem_type=='fcall':
            self.func_call_statement(statement_node)


        ### TODO: check user function definition validity and call it
        return


    def var_def_statement(self, statement_node:Element):
        """
        Variable Definition Statement
                Declares a new variable in the current environment.
                A Statement node representing a variable definition will have the following fields:
                    self.elem_type whose value is 'vardef'
                    self.dict which holds one key:
                        'name' → a string holding the name of the variable to be defined

        If a program defines an existing variable again, then you must generate an error of type ErrorType.NAME_ERROR by calling InterpreterBase.error()
        """
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
        return
    



    def do_assignment(self, statement_node: Element):
        return
    
    def func_call_statement(self, statement_node:Element):
        return
    def evaluate_expression(self, expression_node:Element):
        return
    
    
    






