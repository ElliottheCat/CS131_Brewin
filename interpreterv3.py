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



generate_image = False



# NOTE: I am just using value None as nil in the project unless otherwise specified.

class Value:
    def __init__(self, t, v=None):
        if v is None:
            self.t = t
            if t == Type.INT: # different default values according to types
                self.v = 0
            elif t == Type.BOOL:
                self.v = False
            elif t == Type.OBJ:
                self.v = None
            elif t == Type.STRING:
                self.v = ""
            else:
                self.v = None # default to None, shouldn't reach here we have outside checks


        else:
            self.t = t
            self.v = v


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
        top_env[0][varname] = Value(vartype)
        return True

    def exists(self, varname):
        for block in self.env[-1]:
            if varname in block:
                return True
        return False

    def get(self, varname):
        top_env = self.env[-1]
        for block in top_env:
            if varname in block:
                return block[varname]
        return None

    def set(self, varname, value):
        if not self.exists(varname):
            return False
        top_env = self.env[-1]
        for block in top_env:
            if varname in block:
                block[varname] = value
        return True




class Interpreter(InterpreterBase):
    def __init__(self, console_output: bool =True, inp:str|None = None, trace_output: bool=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor
        self.env = Environment() # initialize to main
        self.scope = ("main",0) # function we are in

        self.return_stack=[]
        self.set_return=False
        
        self.user_function_def : Dict[Tuple[str,Tuple[Type,...]],Element] = {} # (name, arg#): element.

        self.integer_ops_bi = {"-", "/","*"} # NOTE: use // for integer division and truncation in python. 
        # self.integer_ops_un = {"-"} # covered in NEG_NODE already!
        self.integer_ops_com = {"<","<=",">",">="}

        self.boolean_ops_bi = {"||","&&"}
        self.boolean_ops_un ={"!"}


        self.string_or_int_ops_bi= {"+"}

        self.ops_com = {"==","!="}
        


    def run(self, program):
        ast=parse_program(program,False) # returns the program node of ast, have a list in its dict which holds all function nodes

        #Only the statements inside main are executed in Project #1. no need to check for other funcitons 
        ### TODO: Update to hold the user defined functions inside self.function_def 

        for func in ast.get('functions'):
            # use name AND arg count as identification
            name=func.get('name')
            args=func.get('args')
            args_types=self.get_tuple_args_type(args)
            self.user_function_def[(name,args_types)]=func # this also pushes main into the list

        if ("main",0) not in self.user_function_def:
            super().error(ErrorType.NAME_ERROR, f"main function not found")

        main_func= self.user_function_def[("main",())]

        if main_func == None:
                super().error(ErrorType.NAME_ERROR,f"No main() function was found")
        
        else:
            self.run_func(main_func)
        
    def create_function_table(self, ast):
        self.user_function_def = {}
        for func in ast.get("functions"):
            self.user_function_def[(func.get("name"), self.get_tuple_args_type(func.get("args")))] = func
        
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


    

    def run_func(self, func_node:Element):
        self.set_return=False
        stms=func_node.get('statements')
        if stms != None:
            for statement_node in stms:
                
                temp = self.run_statement(statement_node)
                if self.set_return: #return logic
                    return temp




    def run_statement(self, statement_node: Element):
        kind = statement_node.elem_type
        if kind==self.VAR_DEF_NODE:
            self.var_def_statement(statement_node)
        elif kind=='=':
            self.assign_statement(statement_node)
        elif kind==self.FCALL_NODE:
            return self.func_call_statement(statement_node) # return the value!
        elif kind==self.IF_NODE:
            self.if_statement_execution(statement_node)
        elif kind==self.WHILE_NODE:
            self.while_statement_execution(statement_node)
        elif kind==self.RETURN_NODE:
            self.return_statement_execution(statement_node)


        ### TODO: for future project, check user function definition validity and call it. - DONE




    def var_def_statement(self, var:Element):

        var_name=var.get("name")
        var_type=self.determine_var_type(var)
        if var_type not in ['i','o','b','s']:
            super().error(ErrorType.TYPE_ERROR, "variable type not defined")
        if not self.env.fdef(var_type, var_name):
            super().error(ErrorType.NAME_ERROR, "variable already defined")
        
    
    def assign_statement(self, statement:Element):
        name = statement.get("var")
        value = self.evaluate_expression(statement.get("expression")) # type:ignore
        var_type=self.determine_var_type(name)# type:ignore
        value_type=self.type_translation(value)
        if not var_type == value_type:
            super().error(ErrorType.NAME_ERROR, "variable type and value type doesn't match in assignemnt")
        if not self.env.set(name, value):
            super().error(ErrorType.NAME_ERROR, "variable not defined")
        self.env.set(name, var_type,value) # type:ignore ignore possible non from get expression
    
    def type_translation(self, val): 
        if isinstance(val,Value):
            return val.t
        if type(val) == bool:
            return Type.BOOL
        if type(val) == int:
            return Type.INT
        if type(val) == str:
            return Type.STRING
        
        if val is None:
            return Type.OBJ
        if type(val) == dict: # All OBJ are dictionaries!!! No funcitons
            return Type.OBJ

        # else we exhausted all possible valid types
        super().error(ErrorType.TYPE_ERROR, "value type undefined, failed to translate")


    def handle_input(self, fcall_name, args):
        """Handle inputi and inputs function calls"""
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "too many arguments for input function")

        if args:
            self.handle_print(args)

        res = super().get_input()

        return (
            Value(Type.INT, int(res)) 
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
        return Value(Type.OBJ, None)

    
    def func_call_statement(self, statement_node:Element) -> None|Any: # function can return anything, or nothing

        # reset return flag at the beginging of funciton calls
        func_name=statement_node.get('name')
        args=statement_node.get("args")

        # by the AST tree graph and brista tests, all arguments should be in expression form; else -> NAME_ERROR
        if func_name=='print':
            # TODO: support int, string, boolean (true or false)
            out = ""

            for arg in args: #type: ignore
                val= self.evaluate_expression(arg)
                if type(val) is bool: # have to manually convert to the lowercase
                    match val:
                        case True:
                            out += "true"
                        case False:
                            out += "false"
                elif val == None:
                    out+="nil" # must print nil
                else:
                    out += str(val)

            super().output(out)

            return None  # should return nil as the test cases defined

        
        elif func_name=='inputi':
            if args: 
                if len(args)>1:
                    super().error(ErrorType.NAME_ERROR,f"No inputi() function found that takes > 1 parameter")
                elif len(args)==1:
                    strout=""
                    for arg in args:
                        strout=self.evaluate_expression(arg)
                    super().output(strout)
            # reuturn the input as a string using th e super class method
            s= super().get_input()

            if s:
                return int (s) # Need to cast to int ourselves.
            
        elif func_name=='inputs':
            if args: 
                if len(args)>1:
                    super().error(ErrorType.NAME_ERROR,f"No inputi() function found that takes > 1 parameter")
                elif len(args)==1:
                    strout=""
                    for arg in args:
                        strout=self.evaluate_expression(arg)
                    super().output(strout)
            # reuturn the input as a string using th e super class method
            s= super().get_input()

            if s:
                return str (s) # I guess input is always a string so this coersion is unnecessary, but I want to make sure it fits the type.
        elif (func_name, len(args)) in self.user_function_def: #type:ignore
            # TODO: for user defined funciton, push new scope including passed in variables by value on to scope stack.
            # entering user defined function, we need a new environment.
            arg_len=len(args) #type:ignore
            new_env=Environment()
            called_func=self.user_function_def[(func_name, arg_len)]#type: ignore
            
            # evaluate teh variables to their values while we are still in the old scope. Else, we will have issues such as variable not defined if we evaluate it after entering the new funciton scope.
            values=[]
            for arg in args: #type:ignore
                values.append(self.evaluate_expression(arg))

            #enter new funciton scope
            last_scope=self.scope
            last_env=self.env
            self.scope=(func_name, arg_len)
            self.env=new_env

            name_list=called_func.get('args')

            for i in range(arg_len):
                arg_name=name_list[i].get('name') #type:ignore 
                # name_list[i] is a argument node!!!!! remember to use get name!
                arg_val=values[i] #type:ignore
                if not self.env.fdef(arg_name):
                    super().error(ErrorType.NAME_ERROR, "variable already defined")
                if not self.env.set(arg_name, arg_val):
                    super().error(ErrorType.NAME_ERROR, "variable not defined")

            # don't need scope stack if we are keeping track of the last scope
            #self.scope_stack.append((func_name,arg_len,new_env)) #type:ignore

            self.run_func(called_func)

            self.scope=last_scope
            self.env=last_env
            
            self.set_return = False # This keeps the function scope here! we don't end up returning outer function too!
            if self.return_stack: #if there is anything to return
                
                return self.return_stack.pop()
            else:
                return None

        #else log error for unknown functoin.

        super().error(ErrorType.NAME_ERROR, f"Unknown function")
    

    def evaluate_expression(self, expression_node:Element):
        kind = expression_node.elem_type
        if kind==self.INT_NODE or kind == self.STRING_NODE or kind == self.BOOL_NODE:
            return expression_node.get('val')
        # for boolean node, self.dict has 'val' mapping to True or False (booleans print as true/false), parser already mapped the raw text to True or False!
        
        elif kind == self.NIL_NODE:
            return None
        
        elif kind==self.QUALIFIED_NAME_NODE:
            var_name=expression_node.get('name')
            if not self.env.exists(var_name):
                super().error(ErrorType.NAME_ERROR, "variable not defined")
            value = self.env.get(var_name) # shouldn't just check if it;s None!!!! nil is a value!!!!
            
                
            return value #fetch variable from our dictionary
        
        elif kind == self.FCALL_NODE:
            return self.func_call_statement(expression_node) #call function.
        
        elif kind == self.NEG_NODE:
            op=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            if not isinstance(op,int):
                super().error(ErrorType.TYPE_ERROR, f"int unary negation of non-integer")
            return - op
        
        elif kind == self.NOT_NODE:#logical not
            op=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            if type(op) is not bool:
                super().error(ErrorType.TYPE_ERROR, f"bool unary negation of non-boolean")

            return not op
        
        
        elif kind in self.integer_ops_bi:
            # This evealuation step automatically handles any nested functions or +/- such as (9+(7-8)) reflected in AST after parsing
            
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            if ((not type(op1) is int) or (not type(op2) is int )): #f an expression attempts to operate on a string (e.g., 5 + "foo"), then your interpreter must generate an error
                super().error(ErrorType.TYPE_ERROR, f"integer arithmitic on non integers")
            
            if kind == "-":
                return op1 - op2

            elif kind == "/":
                return op1 // op2
            elif kind == "*":
                return op1 * op2
        
        elif kind in self.string_or_int_ops_bi:
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            if (  not (type(op1) is int and type(op2) is int) ):
                if ( not (isinstance(op1,str) and isinstance(op2,str)) ):
                    super().error(ErrorType.TYPE_ERROR, f"add or concatenating non int and non string")
            
            #python + works the same for strign and int for our purposes
            return op1+op2 #type: ignore
        
        elif kind in self.integer_ops_com:
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            if ((not type(op1) is int) or (not type(op2) is int )): # bool is subtype of int
                super().error(ErrorType.TYPE_ERROR, f"integer comparison on non integers")
            
            match kind:
                case "<":
                    return op1 < op2
                case ">":
                    return op1 > op2
                case "<=":
                    return op1 <= op2
                case ">=":
                    return op1 >= op2
            
        elif kind in self.boolean_ops_bi:
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            if (not type(op1) is bool) or (not type(op2) is bool): 
                super().error(ErrorType.TYPE_ERROR, f"bool binary on non booleans")

            match kind: # use lazy evaluation 
                case "&&":
                    return op1 and op2
                case "||":
                    return op1 or op2
        
        elif kind in self.ops_com:
            op1=self.evaluate_expression(expression_node.get('op1')) #type: ignore
            op2=self.evaluate_expression(expression_node.get('op2')) #type: ignore
            t1 = type(op1)
            t2 = type(op2)
            
            equal=True
            if op1 == None and op2==None: # just a special case I want to make sure it works
                equal=True
            elif op1 == None or op2==None: # everything not None is not equal to None 
                equal = False
            elif not t1 == t2:
                equal = False
            else:
            # everything should be the same type at this point: 
                equal = (op1 == op2)

            match kind:
                case "==":
                    return equal
                case "!=":
                    return not equal
            
        return
    
    def if_statement_execution(self, statement):
        cond = self.evaluate_expression(statement.get("condition"))

        if cond.t != Type.BOOL: #type:ignore
            super().error(ErrorType.TYPE_ERROR, "condition must be boolean")

        self.env.enter_block() 

        res, ret = None, False

        if cond.v: #type:ignore
            # enter if body
            res, ret = self.__run_statements(statement.get("statements"))
        elif statement.get("else_statements"):
            #enter else statement if condition is false and exist else statement
            res, ret = self.__run_statements(statement.get("else_statements"))

        self.env.exit_block()

        return res, ret
    

    def while_statement_execution(self, statement:Element):
        res, ret = Value(), False

        while True:
            cond = self.evaluate_expression(statement.get("condition")) # type:ignore
            if cond.t != Type.BOOL: # type:ignore
                super().error(ErrorType.TYPE_ERROR, "condition must be boolean")

            if not cond.v: # type:ignore
                # end loop if value is False
                break

            self.env.enter_block()
            res, ret = self.__run_statements(statement.get("statements"))
            self.env.exit_block()
            if ret:
                break

        return res, ret
    
    
    def return_statement_execution(self, statement):
        expr = statement.get("expression")
        if expr:
            return (self.evaluate_expression(expr), True)
        # else, return none
        return (Value(), True)



        if rtr==None:
            self.set_return=True
            
            return
        else:
            self.set_return=True
            
            self.return_stack.append(rtr)#type: ignore
            return
    
    





    def determine_func_return_type(self, func:Element):
        fname=func.get('name')
        if fname=="main":
            return Type.VOID
        
        ftype=fname[-1] #type:ignore Assume fname exists as long as parser worked, get last char 
        if ftype=='i':
            return Type.INT
        if ftype=='s':
            return Type.STRING
        if ftype=='b':
            return Type.BOOL
        if ftype=='o':
            return Type.OBJ
        if ftype=='v':
            return Type.VOID # MUST NOT RETURN VALUE
    
        super().error(ErrorType.TYPE_ERROR, "invalid funciton return type in name")
    



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


    

