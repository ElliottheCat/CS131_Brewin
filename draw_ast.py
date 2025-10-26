from brewparse import parse_program
from interpreterv1 import Interpreter


program_source="""

def main() {
  var a;
  a = 5;
  foo(10);
  foo(20,30);
}

def foo(a) {
  print(a);
}

def foo(a,b) {
  print(a," ",b);
}

/*
*OUT*
10
20 30
*OUT*
*/

"""


def main():
    ast=parse_program(program_source,True)
    # added save to png in plot.py, doesn't affect other stuff. 
    #ast = parse_program(program_source, False)
    #print(ast.elem_type)             
    #print(type(ast))                 
    #print(type(ast.get("functions")))
    interpret=Interpreter()
    interpret.run(program_source)



if __name__ == '__main__':
    main()