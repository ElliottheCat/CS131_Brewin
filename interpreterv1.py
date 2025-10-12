from brewparse import parse_program
from intbase import InterpreterBase
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
        
        for node in ast:
            if node.name=='main':
                main_func = node
                break
        



    def run_func(self, func_node:Element):
        stms=func_node.get('statements')
        if not stms == None:
            for statement_node in stms:
                run_statement(statement_node)

    def run_statement(self, statement_node: Element):
        

    def do_assignment(self, statement_node: Element):

    def evaluate_expression(expression_node:Element):



