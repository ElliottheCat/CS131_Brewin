from brewparse import parse_program
from interpreterv1 import Interpreter


program_source="""
def swapv(&ai, &bi) {
  ai = bi;

}

def main() {
  var x;
  x=true;

  if (x){
    bvar y;
  }
  bvar z;
  var r;

  r.q = @;
  r.q.r = 5;
  print(x);
  swapv(x,z);
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