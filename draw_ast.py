from brewparse import parse_program
from interpreterv1 import Interpreter


program_source="""

var a;
a = (1 == 1);
print(a);

"""


def main():
    ast=parse_program(program_source,False)
    # added save to png in plot.py, doesn't affect other stuff. 
    #ast = parse_program(program_source, False)
    #print(ast.elem_type)             
    #print(type(ast))                 
    #print(type(ast.get("functions")))
    interpret=Interpreter()
    interpret.run(program_source)



if __name__ == '__main__':
    main()