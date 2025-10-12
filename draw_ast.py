from brewparse import parse_program



program_source="""
def main() {
  var a;
  a = inputi("Enter a value: ");
  print(a,5,"string", 5+6);  
}
def fun(){
    var y;
}
"""


def main():
    ast=parse_program(program_source,True)
    # added save to png in plot.py, doesn't affect other stuff. 
    #ast = parse_program(program_source, False)
    #print(ast.elem_type)             
    #print(type(ast))                 
    #print(type(ast.get("functions")))


if __name__ == '__main__':
    main()