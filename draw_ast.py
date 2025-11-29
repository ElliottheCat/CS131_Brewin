from brewparse import parse_program
from interpreterv1 import Interpreter


program_source1="""
def fooi(i) { 
  return i+1; 
}

def main() {
  print(fooi(41)); 

  var o;
  o = @;
  o.memberf = fooi;
  print(o.memberf(41)); /* 42 */

  var ao;
  ao = @;
  ao.addf = lambdai(ai,bi) { return ai+bi; }; /* addf is a method of ao */
  ao.ai=1;
  ao.addf(1,2);
}
"""

program_source2="""
interface Q {
  fooi;
  barb;
  bletchs;
  func1f(i);
  func2f(&b,s); /* interfaces can refer to other interfaces like R */
}

def f1v(pi) {
  print(pi);
}
def f2s(&paramb, params) {
  paramb = false;
  return params + "!";
}

def main() {
  var o;
  o = @;
  o.fooi = 10;
  o.barb = true;
  o.bletchs = "haha";
  o.func1f =f1v;
  o.func2f = f2s;
  var blahQ; /* blahQ is a variable that is guaranteed to point to either nil or an object that has
  blahQ = o; /* this works because object o has all required fields/types of interface Q */
  
}



"""
program_source3="""
interface Q {
  func1f(i);
  func2f(&b,s); /* interfaces can refer to other interfaces like R */
}

def f1v(pi) {
  print(pi);
}
def f2s(&paramb, params) {
  paramb = false;
  return params + "!";
}

def main() {
  var o;
  o = @;
  o.func1f =f1v;
  o.func2f = f2s;
  var blahQ; /* blahQ is a variable that is guaranteed to point to either nil or an object that has
  blahQ = o; /* this works because object o has all required fields/types of interface Q */
  
}



"""
program_source4="""
interface B { vali; }
interface A { callf(&B); }
def implv(&objB) { objB.vali = objB.vali + 10; }
def main() {
  var bo; bo = @; bo.vali = 5;
  var ao; ao = @; ao.callf = implv;
  var xA; xA = ao; /* ao satisfies A */
  xA.callf(bo); /* bo satisfies B; updated by reference */
  print(bo.vali); /* 15 */
}
"""

def main():
    ast=parse_program(program_source4,True)
    # added save to png in plot.py, doesn't affect other stuff. 
    #ast = parse_program(program_source, False)
    #print(ast.elem_type)             
    #print(type(ast))                 
    #print(type(ast.get("functions")))
    #interpret=Interpreter()
    #interpret.run(program_source3)



if __name__ == '__main__':
    main()