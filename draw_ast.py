from brewparse import parse_program
from interpreterv1 import Interpreter


program_source="""
def main() {
 var i;
 i = 3;
 while (i > 0) {
  print(i);
  i = i - 1;
 }
}
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