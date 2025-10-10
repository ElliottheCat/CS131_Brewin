from brewparse import parse_program
from intbase import InterpreterBase

# need data structures:
# Need a variable hash map
# TA: Also need a structure to hold all functions you see (is this necessary?)

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor


    def run(self, program_source):
        parsed_program=parse_program(program_source,False) # generates an image of your AST

    

