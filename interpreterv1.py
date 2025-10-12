from brewparse import parse_program
from intbase import InterpreterBase, ErrorType
from typing import Optional, Tuple, Dict, List,Any
from element import Element
# need data structures:
# Need a variable hash map
# TA: Also need a structure to hold all functions you see (is this necessary?)
    # for project 2..

class Interpreter(InterpreterBase):
    def __init__(self, console_output: bool =True, inp:str =None, trace_output: bool=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor
        self.variable_name_to_value: Dict [str,Any] = {}
        self.function_def = Dict[str,Any]
        


    def run(self, program_source):
        ast=parse_program(program_source,False) # generates an image of AST
        
        # find the program entry
        for node in ast:
            if node.elem_type=='program':
                #self.dict[functions] holds a list of function definiton nodes representing each of the functions in the program
                self.pg:Element=node
                break
        
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
        main_func:Element|None = self.pg.get("main")
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

        

    def do_assignment(self, statement_node: Element):

        

    def evaluate_expression(self, expression_node:Element):



