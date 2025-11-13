from brewparse import parse_program
from interpreterv1 import Interpreter


program_source="""

def main() {
  var o;
  o = @;
  var io;
  io = @;
  var nested1o;
  nested1o = @;
  var nested2o;
  nested2o = @;
  
  o.io = io;
  o.io.nested1o = nested1o;
  o.io.nested1o.nested2o = nested2o;
  o.io.nested1o.nested2o.xi = 5;
  print(o.io.nested1o.nested2o.xi);
}

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