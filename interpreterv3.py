from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from typing import Optional, Dict, Any, Tuple
from element import Element
import enum

class Type(enum.Enum):
    VOID = 0 # for function returns
    INT = 1
    STRING = 2
    BOOL = 3
    OBJ = 4

generate_image = True

# NOTE: I am just using value None as nil in the project unless otherwise specified.
# define heleper that always clones
# flag: if there is a reference and return object reference. else return deepcopy 
class Value:
    def __init__(self, t, v=None):
        if v is None:
            self.t = t
            if t == Type.INT: # different default values according to types
                self.v = 0
            elif t == Type.BOOL:
                self.v = False
            elif t == Type.OBJ:
                self.v = {} # initialize to dictionary!!!
            elif t == Type.STRING:
                self.v = ""
            else:
                self.v = None # default to None, shouldn't reach here we have outside checks


        else:
            self.t = t
            self.v = v

    def set_val(self, value):
        self.v=value

################################################################################################################################################################################################################

class Environment:
    def __init__(self):
        self.env = []

    def enter_block(self):
        self.env[-1].append({})

    def exit_block(self):
        self.env[-1].pop()

    def enter_func(self):
        self.env.append([{}])

    def exit_func(self):
        self.env.pop()

    # define new variable at function scope
    def fdef(self, vartype, varname):
        if self.exists(varname):
            return False
        top_env = self.env[-1]
        top_env[0][varname] = Value(vartype) # index 0 is the functional variable list, others are block variable lists
        return True
    
    #define new var at block scope
    def bdef(self, vartype,varname):
        if self.exists(varname): 
            return False
        cur_block=self.env[-1][-1] # the last list in envicronment is the block scope we are in. this is true even if we only have the funtional scope left. 
        cur_block[varname]=Value(vartype)
        return True

    def recur_lookup(self, varname):
        for block in self.env[-1]:
            if varname in block:
                return block
        return None

    def exists(self, varname):
        dot_var=varname.split('.')
        top_name=dot_var[0] # only keep tract of top level name in the environment. rest is in the library
        target=self.recur_lookup(top_name)
        if target is None:
            return False # got nothing
        

        if len(dot_var)==1: #type:ignore not a recursive object
            return True


        obj_content=target[top_name] #type:ignore

        nest_var=dot_var[1] # safe, we checked lenth of dot var earlier 

        if obj_content.t!=Type.OBJ or obj_content.v is None or nest_var not in obj_content:
            # something is wrong witht he given name!
            return False
            
        separate='.'
        return self.exists(separate.join(dot_var[1:])) # passed the checks :)


    def get(self, varname):
        dot_var=varname.split('.')
        top_name=dot_var[0] # only keep tract of top level name in the environment. rest is in the library
        target=self.recur_lookup(top_name)
        if target is None:
            return False # nothing found
        
        value=target[top_name]

        if len(dot_var)==1:
            return value # no recursion, plain value, also the last level of objects
        
        obj_content = value
        
        nest_var=dot_var[1] # safe, we checked lenth of dot var earlier 
        if obj_content.t != Type.OBJ or obj_content.v is None or nest_var not in obj_content:
            return None
        separate='.'
        return self.get(separate.join(dot_var[1:]))
        


    def set(self, varname, value):
        
        # don't check for exist since it waste time. we will do it with set itself

        dot_var=varname.split('.')
        top_name=dot_var[0] # only keep tract of top level name in the environment. rest is in the library
        target=self.recur_lookup(top_name)
        if target is None:
            return False # nothing found, top var name doesn't exits
        
        if len(dot_var)==1: # no recursion
            # do type check in Interpreter! assume everything woerks 
            target[dot_var]=value
            return True
        
        obj_content = value

        nest_var=dot_var[1] # safe, we checked lenth of dot var earlier 
        if obj_content.t != Type.OBJ or obj_content.v is None or nest_var not in obj_content:
            return False
        separate='.'
        return self.set(separate.join(dot_var[1:]),value)



###################################################################################################################################################################################################

class Interpreter(InterpreterBase):
    def __init__(self, console_output: bool =True, inp:str|None = None, trace_output: bool=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor
        self.env = Environment() # initialize to main
        self.scope = ("main",0) # function we are in

        self.return_stack=[]
        self.set_return=False
        
        self.user_function_def : Dict[Tuple[str,Tuple[Type,...]],Element] = {} # (name, arg#): element.

        self.cur_func="main"
        self.should_return=False # is this still useful???

        # NOTE: use // for integer division and truncation in python. 
        # self.integer_ops_un = {"-"} # covered in NEG_NODE already!
        self.bops = {"+", "-", "*", "/", "==", "!=", ">", ">=", "<", "<=", "||", "&&"}
        


    def run(self, program):
        ast=parse_program(program,False) # returns the program node of ast, have a list in its dict which holds all function nodes

        #Only the statements inside main are executed in Project #1. no need to check for other funcitons 
        ### TODO: Update to hold the user defined functions inside self.function_def 

        
        self.create_function_table(ast)

        if ("main",()) not in self.user_function_def:
            super().error(ErrorType.NAME_ERROR, f"main function not found")

        main_func= self.user_function_def[("main",())]

        if main_func == None:
                super().error(ErrorType.NAME_ERROR,f"No main() function was found")
        else:
            self.run_func(main_func)
        
        
    def create_function_table(self, ast):
        self.user_function_def = {}

        for func in ast.get('functions'):
            # use name AND arg count as identification
            name=func.get('name')
            args=func.get('args')
            args_types=self.get_tuple_args_type(args)

            func_identity=(name, self.get_tuple_args_type(func.get("args")))
            
            if  (name != "main"):
                if (name[-1] not in ['i','o','b','s','v']):
                    return super().error(ErrorType.NAME_ERROR,f"function return type not defined") # all function other than main have to declare return type as last char

            if func_identity in self.user_function_def:
                return super().error(ErrorType.NAME_ERROR,f"duplicate function with same name and parameters")

            self.user_function_def[(name,args_types)]=func # this also pushes main into the list
        
    def get_tuple_args_type(self, args:list[Element]) -> Tuple[Type, ...]: # return variable length tuple
        args_type_list=()
        for arg in args:
            arg_type=self.determine_var_type(arg)
            args_type_list=args_type_list+(arg_type,)

        return args_type_list

    def get_function(self, name, parameter_type=()):
        if (name, parameter_type) not in self.user_function_def:
            super().error(ErrorType.NAME_ERROR, "function not found")
        return self.user_function_def[(name, parameter_type)]


    
    def run_func(self, func_call_ast):
        fcall_name, args = func_call_ast.get("name"), func_call_ast.get("args")

        if fcall_name == "inputi" or fcall_name == "inputs":
            return self.handle_input(fcall_name, args)

        if fcall_name == "print":
            self.handle_print(args) # should return void if it's a print function!
            return 

        args_types=self.get_tuple_args_type(args)
        # check if function exist
        func_def = self.get_function(fcall_name, args_types) # based on name and types of arg

        formal_args = [a.get("name") for a in func_def.get("args")] #type:ignore
        actual_args = [self.evaluate_expression(a) for a in args]



        self.should_return=False# set the flag to false at begining
        last_func=self.cur_func
        self.cur_func=fcall_name # set current function's name so return knows what value to default to 
        self.env.enter_func()
        for formal, actual in zip(formal_args, actual_args):
            self.env.fdef(self.type_translation(actual),formal)
            self.env.set(formal, actual)
        res, _ = self.run_statements(func_def.get("statements"))
        self.env.exit_func()
        self.cur_func=last_func
        return res
    

    def run_statements(self, statements):
        res, ret = None, False

        for statement in statements:
            kind = statement.elem_type

            if kind == self.VAR_DEF_NODE:
                self.function_level_var_def_statement(statement)
            elif kind==self.BVAR_DEF_NODE:
                self.block_level_var_def_statement(statement)
            elif kind == "=":
                self.variable_assign_statement(statement)
            elif kind == self.FCALL_NODE:
                self.run_func(statement)
            elif kind == self.IF_NODE:
                res, ret = self.if_statement_execution(statement)
                if ret:
                    break
            elif kind == self.WHILE_NODE:
                res, ret = self.while_statement_execution(statement)
                if ret:
                    break
            elif kind == self.RETURN_NODE:
                if self.type_translation(self.cur_func)!=Type.VOID:
                    res, ret = self.return_statement_execution(statement) #type:ignore
                    #must return something if current function is not void! 
                else:
                    ret= True # res stays None
                break

        return res, ret



    def function_level_var_def_statement(self, var:Element):
        var_name=var.get("name")
        var_type=self.determine_var_type(var)
        if var_type not in ['i','o','b','s']:
            super().error(ErrorType.TYPE_ERROR, "variable type not defined")
        if not self.env.fdef(var_type, var_name):
            super().error(ErrorType.NAME_ERROR, "variable already defined")
    
    def block_level_var_def_statement(self, var:Element):
        var_name=var.get("name")
        var_type=self.determine_var_type(var)
        if var_type not in ['i','o','b','s']:
            super().error(ErrorType.TYPE_ERROR, "variable type not defined")
        if not self.env.bdef(var_type, var_name):
            super().error(ErrorType.NAME_ERROR, "variable already defined")

    def variable_assign_statement(self, statement:Element):
        name = statement.get("var")
        value = self.evaluate_expression(statement.get("expression")) # type:ignore
        if not self.var_val_type_match(name,value):
            super().error(ErrorType.NAME_ERROR, "variable type and value type doesn't match in assignemnt")
        if not self.env.set(name, value):
            super().error(ErrorType.NAME_ERROR, "variable not defined")
        self.env.set(name, var_type,value) # type:ignore ignore possible non from get expression



    def determine_var_type(self, var:Element):
        varname=var.get('name')
        vtype=varname[-1] #type:ignore
        if vtype=='i':
            return Type.INT
        if vtype=='b':
            return Type.BOOL
        if vtype=='s':
            return Type.STRING
        if vtype=='o':
            return Type.OBJ
        
        super().error(ErrorType.TYPE_ERROR, "invalid variable type in name")

    def type_translation(self, val): 
        if isinstance(val,Value):
            return val.t
        if type(val) == bool:
            return Type.BOOL
        if type(val) == int:
            return Type.INT
        if type(val) == str:
            return Type.STRING
        if type(val) == dict: # All OBJ are dictionaries!!! No funcitons
            return Type.OBJ
        if type(val) == None:
            return Type.VOID

        # else we exhausted all possible valid types
        super().error(ErrorType.TYPE_ERROR, "value type undefined, failed to translate")
    
    def var_val_type_match(self,name,value):
        var_type=self.determine_var_type(name)# type:ignore
        value_type=self.type_translation(value)
        if not var_type == value_type:
            super().error(ErrorType.NAME_ERROR, "variable type and value type doesn't match in assignemnt")
            return False
        return True


    def handle_input(self, fcall_name, args):
        """Handle inputi and inputs function calls"""
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "too many arguments for input function")

        if args:
            self.handle_print(args)

        res = super().get_input()

        return (
            Value(Type.INT, int(res)) #type: ignore
            if fcall_name == "inputi"
            else Value(Type.STRING, res)
        )

    def handle_print(self, args):
        """Handle print function calls"""
        out = ""

        for arg in args:
            c_out = self.evaluate_expression(arg) 
            if c_out.t == Type.BOOL: #type: ignore
                out += str(c_out.v).lower() #type: ignore
            else:
                out += str(c_out.v) #type: ignore
        super().output(out)
        return #return void!

    def eval_binary_op(self, kind, vl, vr):
        """Evaluate binary operations"""
        tl, tr = vl.t, vr.t
        vl_val, vr_val = vl.v, vr.v

        if kind == "==":
            if vl.t==Type.OBJ:
                result= tl == tr and vl_val is vr_val
                # even for empty objects in Python, None is None evaluates to True.
                return result
            # else just compare normally
            return Value(Type.BOOL, tl == tr and vl_val == vr_val)
        if kind == "!=":
            if vl.t==Type.OBJ:
                result = tl == tr and vl_val is vr_val
                # even for empty objects in Python, None is None evaluates to True.
                return not result # NOT answer since we are evaluating for !=
            # else just compare normally
            return Value(Type.BOOL, not (tl == tr and vl_val == vr_val))

        if tl == Type.STRING and tr == Type.STRING:
            if kind == "+":
                return Value(Type.STRING, vl_val + vr_val)
        if tl == Type.INT and tr == Type.INT:
            if kind == "+":
                return Value(Type.INT, vl_val + vr_val)
            if kind == "-":
                return Value(Type.INT, vl_val - vr_val)
            if kind == "*":
                return Value(Type.INT, vl_val * vr_val)
            if kind == "/":
                return Value(Type.INT, vl_val // vr_val)
            if kind == "<":
                return Value(Type.BOOL, vl_val < vr_val)
            if kind == "<=":
                return Value(Type.BOOL, vl_val <= vr_val)
            if kind == ">":
                return Value(Type.BOOL, vl_val > vr_val)
            if kind == ">=":
                return Value(Type.BOOL, vl_val >= vr_val)

        if tl == Type.BOOL and tr == Type.BOOL:
            if kind == "&&":
                return Value(Type.BOOL, vl_val and vr_val)
            if kind == "||":
                return Value(Type.BOOL, vl_val or vr_val)
            
        super().error(ErrorType.TYPE_ERROR, "invalid binary operation")

    def evaluate_expression(self, expr):
        kind = expr.elem_type 

        if kind == self.INT_NODE:
            return Value(Type.INT, expr.get("val"))

        if kind == self.STRING_NODE:
            return Value(Type.STRING, expr.get("val"))

        if kind == self.BOOL_NODE:
            return Value(Type.BOOL, expr.get("val"))

        if kind == self.EMPTY_OBJ_NODE: # none
            return Value(Type.OBJ, None)

        if kind == self.QUALIFIED_NAME_NODE:
            var_name = expr.get("name") # possibly dotted

            if not self.env.exists(var_name):
                super().error(ErrorType.NAME_ERROR, "variable not defined")
            return self.env.get(var_name)

        if kind == self.FCALL_NODE:
            rtr = self.run_func(expr)
            return rtr # could be None

        if kind in self.bops:
            l, r = self.evaluate_expression(expr.get("op1")), self.evaluate_expression(expr.get("op2"))
            return self.eval_binary_op(kind, l, r)

        if kind == self.NEG_NODE:
            o = self.evaluate_expression(expr.get("op1"))
            if o.t == Type.INT:
                return Value(Type.INT, -o.v)

            super().error(ErrorType.TYPE_ERROR, "cannot negate non-integer")

        if kind == self.NOT_NODE:
            o = self.evaluate_expression(expr.get("op1"))
            if o.t == Type.BOOL:
                return Value(Type.BOOL, not o.v)

            super().error(ErrorType.TYPE_ERROR, "cannot apply NOT to non-boolean")

        if kind == self.CONVERT_NODE:
            to_type=expr.get("dict")["to_type"] #one of int, bool, str
            to_convert=expr.get("dict")["expr"]

        

        raise Exception("should not get here!!!!")

    


    def if_statement_execution(self, statement):
        cond = self.evaluate_expression(statement.get("condition"))

        if cond.t != Type.BOOL: #type:ignore
            super().error(ErrorType.TYPE_ERROR, "condition must be boolean")

        self.env.enter_block() 

        res, ret = None, False

        if cond.v: #type:ignore
            # enter if body
            res, ret = self.run_statements(statement.get("statements"))
        elif statement.get("else_statements"):
            #enter else statement if condition is false and exist else statement
            res, ret = self.run_statements(statement.get("else_statements"))

        self.env.exit_block()

        return res, ret
    

    def while_statement_execution(self, statement:Element):
        res, ret = None, False # we won;t use while in a expression evaluation anyways, returned value doesn't matter

        while True:
            cond = self.evaluate_expression(statement.get("condition")) # type:ignore
            if cond.t != Type.BOOL: # type:ignore
                super().error(ErrorType.TYPE_ERROR, "condition must be boolean")

            if not cond.v: # type:ignore
                # end loop if value is False
                break

            self.env.enter_block()
            res, ret = self.run_statements(statement.get("statements"))
            self.env.exit_block()
            if ret:
                break

        return res, ret
    

    def func_retval_type_match(self, funcname,retVal):
        """
        Checks a funtionls return type, if it mathches a given value, and return the return type as well as teh comparing result.
        """
        ftype=funcname[-1] #type:ignore Assume fname exists as long as parser worked, get last char 
        f_rtr_type=Type.VOID # default
        if ftype=='i' : # also consider inputi
            f_rtr_type= Type.INT
        elif ftype=='s': # also consider inputs
            f_rtr_type= Type.STRING
        elif ftype=='b':
            f_rtr_type= Type.BOOL
        elif ftype=='o':
            f_rtr_type= Type.OBJ
        elif ftype=='v' or funcname=="main": # don't falsely reject main
            f_rtr_type= Type.VOID # MUST NOT RETURN VALUE
        else:
            super().error(ErrorType.TYPE_ERROR, "invalid funciton return type in name") # should enver reach hear after initial screenign in loading functions

        ret_val_type=self.type_translation(retVal)
        if f_rtr_type==ret_val_type:
            return (f_rtr_type,True)
        super().error(ErrorType.TYPE_ERROR, "function return value doesn't match return type") # NO IMPLICITY TYPE CONVERSION

        return (None,False)

    def return_statement_execution(self, statement):
        expr = statement.get("expression")
        if expr:
            rval=self.evaluate_expression(expr)
            ftype,match=self.func_retval_type_match(self.cur_func,rval) #type:ignore Assume fname exists as long as parser worked, get last char 
            if ftype==Type.VOID or match == False:
                super().error(ErrorType.TYPE_ERROR, "returning value from void functions OR return type doesn't match with return value")
            # else, we can return the results and set self.should_return to True
            return (rval,True)
        self.should_return=True
        ftype, _ =self.func_retval_type_match(self.cur_func,0) # doens't care if match or not
        if ftype!=Type.VOID:
            return_val=Value(ftype)#automatically creates the default value of it 
            return (return_val,True)
        return (None, True)# return for void functions



    
    





    


