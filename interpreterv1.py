from brewparse import parse_program
from intbase import InterpreterBase, ErrorType
from typing import Optional, Dict, Any 
from element import Element
# need data structures:
# Need a variable hash map
# TA: Also need a structure to hold all functions you see (is this necessary?)
    # for project 2..


"""
Notes:
I quoted the original specs in the triple quoted strings, and my own comments as well as future development notes after # comments. 
The spec explained almost everything so for the parts explained by the quoted specs, I didn't have much commenst myself. 

"""

class Interpreter(InterpreterBase):
    def __init__(self, console_output: bool =True, inp:str|None = None, trace_output: bool=False):
        super().__init__(console_output, inp) # call InterpreterBase's constructor
        self.variable_name_to_value: Dict [str,Any] = {}
        self.user_function_def : Dict[str,Element] = {} # name: element.
    
        


    def run(self, program):
        ast=parse_program(program,False) # returns the program node of ast, have a list in its dict which holds all function nodes

        
        """ SPEC
        A Function node will have the following fields:
            self.elem_type whose value is 'func', identifying this node as a Function node
            self.dict which holds up to three keys:
                'name' → a string containing the name of the function (e.g., 'main')
                'args' → a (possibly empty) list of Argument nodes (ignored by this interpreter)
                'statements' → a list of Statement nodes, representing each of the statements that make up the function, in their order of execution

        To interpret a function, you must interpret all of its statements from top to bottom
        """
        #Only the statements inside main are executed in Project #1. no need to check for other funcitons 
        ### TODO: Update to hold the user defined functions inside self.function_def 

        """
        If a program does not have a main function defined, then you must generate an error of type ErrorType.NAME_ERROR by calling InterpreterBase.error()
        """

        funcs = ast.get('functions')
        main_func: Element|None=None
        if funcs == None:
            super().error(ErrorType.NAME_ERROR,"No function was found in program")
        else:
            for func in funcs:
                if func.get('name')=='main':
                    main_func=func


        if main_func == None:
                super().error(ErrorType.NAME_ERROR,"No main() function was found")
        
        else:
            self.run_func(main_func)
        

        
        
        



    def run_func(self, func_node:Element):
        stms=func_node.get('statements')
        """The main function must have at least one statement defined within it. You do NOT need to check for this, all of our main functions that we test with will have at least one statement.
        
        Every function consists of zero or more statements. Statements in Brewin v1 come in three forms:

            variable definition statements
            assignment statements
            function call statements
        """
        if stms != None:
            for statement_node in stms:
                self.run_statement(statement_node)



    def run_statement(self, statement_node: Element):
        """
        Statement Nodes
            Variable Definition Statement
                Declares a new variable in the current environment.
                A Statement node representing a variable definition will have the following fields:
                    self.elem_type whose value is 'vardef'
                    self.dict which holds one key:
                        'name' → a string holding the name of the variable to be defined
            Assignment Statement
                Assigns the result of an expression to an existing variable.
                A Statement node representing an assignment will have the following fields:
                    self.elem_type whose value is '='
                    self.dict which holds two keys:
                        'var' → the name of the variable on the left-hand side of the assignment (e.g., 'x' for x = 1 + y;)
                        'expression' → an Expression node whose value is computed and stored into the named variable
                The target variable must already have been declared via a variable definition statement.
            
            Function Call Statement
                Invokes a built-in function for its side effects (its return value, if any, is ignored when used as a statement).
                A Statement node representing a function call will have the following fields:
                    self.elem_type whose value is 'fcall'
                    self.dict which holds two keys:
                        'name' → the name of the function to be called (e.g., 'print', 'inputi')
                        'args' → a list containing zero or more Expression nodes representing arguments to the function call

                REMEMBER TO CHECK IF FUNCTION IS DEFINED OR BUILDIN
        """
        if statement_node.elem_type=='vardef':
            self.var_def_statement(statement_node)
        elif statement_node.elem_type=='=':
            self.assign_statement(statement_node)
        elif statement_node.elem_type=='fcall':
            self.func_call_statement(statement_node)


        ### TODO: for future project, check user function definition validity and call it
        return


    def var_def_statement(self, statement_node:Element):
        """
        Variable Definition Statement
                Declares a new variable in the current environment.
                A Statement node representing a variable definition will have the following fields:
                    self.elem_type whose value is 'vardef'
                    self.dict which holds one key:
                        'name' → a string holding the name of the variable to be defined

        If a program defines an existing variable again, then you must generate an error of type ErrorType.NAME_ERROR by calling InterpreterBase.error()
        """
        var_name=statement_node.get("name")
        if var_name in self.variable_name_to_value:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} defined more than once")
        
        if not isinstance(var_name,str):
            super().error(ErrorType.TYPE_ERROR, f"Variable name {var_name} not string from parser")
            return
        #Define variable name in variable dictionary
        self.variable_name_to_value[var_name]=None
        return
    



    def assign_statement(self, statement_node:Element):
        """
        Assigns the result of an expression to an existing variable.
                A Statement node representing an assignment will have the following fields:
                    self.elem_type whose value is '='
                    self.dict which holds two keys:
                        'var' → the name of the variable on the left-hand side of the assignment (e.g., 'x' for x = 1 + y;)
                        'expression' → an Expression node whose value is computed and stored into the named variable
                The target variable must already have been declared via a variable definition statement.

        """

        var_name=statement_node.get('var')
        expr=statement_node.get('expression')

        """
        If a program tries to assign a non-defined variable to an expression, then you must generate an error of type ErrorType.NAME_ERROR by callingInterpreterBase.error()
        """
        if var_name not in self.variable_name_to_value:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")

        if expr==None:
            super().error(ErrorType.NAME_ERROR, f"No expression to be assigned; parser error.")
        expr_val=self.evaluate_expression(expr)
        self.variable_name_to_value[var_name]=expr_val

        return
    

    
    def func_call_statement(self, statement_node:Element)-> None | int:
        """
        The only function call statements you must support are the print() function call and the inputi() function call (as well as the automatic call to the main function to start the program). You can assume we won’t make any recursive calls (i.e., we will never invoke the main function from main itself). Calls to any function other than print() or inputi() should result in an error of type ErrorType.NAME_ERROR by calling InterpreterBase.error().
        """
        func_name=statement_node.get('name')

        """
        Your print function call must accept zero or more arguments, which it will
        evaluate to get a resulting value, then concatenate without spaces into a string,
        and then output using the output() method in our InterpreterBase base class:

        
        In project #1, the only valid function call you can make in an expression is a call to the inputi() function (calling the print() function in an expression is UNDEFINED BEHAVIOR and will NOT be tested).
        The inputi() function may take either no parameters or a single parameter:

        You may assume that if the inputi() function is invoked with a single argument, the argument will always have the type of string (you don’t need to check for this).

        If an inputi() function call has a prompt parameter, you must first output it to the screen using our InterpreterBase.output() method before obtaining input from the user:

        If an inputi() expression has more than one parameter passed to it, then you must generate an error of type ErrorType.NAME_ERROR by calling InterpreterBase.error()

        The get_input() method returns a string regardless of what the user types in, so you’ll need to convert the result to an integer yourself. You may assume that only valid integers will be entered in response to an inputi() prompt and do NOT need to test for non-integer values being entered.

        You may use any error message string you like as we will not check the message in our testing.
        
        """
        # by the AST tree graph and brista tests, all arguments should be in expression form; else -> NAME_ERROR
        if func_name=='print':
            args=statement_node.get('args')
            if args == None:
                # nothing but an empty line
                super().output("")
            else:
                string_to_output=""
                for arg in args:
                    val=self.evaluate_expression(arg)
                    string_to_output+=str(val) #no matter waht expression we returned (int or string), cast it to string
                super().output(string_to_output)

        
        elif func_name=='inputi':
            args=statement_node.get('args')
            
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
        
        #else log error for unknown functoin.
        else:
            super().error(ErrorType.NAME_ERROR, f"Unknown function")
    

    def evaluate_expression(self, expression_node:Element):
        """
        Expression Nodes
            Binary Operation Expression
                Represents integer arithmetic with + or -.
                An Expression node representing a binary operation has:
                self.elem_type: '+' or '-'
                self.dict with:
                    'op1' → first operand (an Expression node)
                    'op2' → second operand (an Expression node)
                Type rules enforced by the interpreter:
                Both operands must evaluate to integers; if either evaluates to a string, it is a type error.
                '-' computes integer subtraction; '+' computes integer addition.

            Function Call Expression
                Represents calling a built-in function for its resulting value.
                A function-call Expression node has:
                self.elem_type: 'fcall'
                self.dict with:
                    'name' → function name (string)
                    'args' → list of Expression nodes (actual arguments)

            Qualified Name (Variable) Expression
                Represents a variable name referenced in an expression.
                A qname node has:
                self.elem_type: 'qname'
                self.dict with:
                    'name' → the variable’s name (e.g., 'x')
                The variable must have been declared and assigned a value before being read.
                Reading a declared-but-unassigned variable is an error.

            Value Nodes
                Integer Literal
                    self.elem_type: 'int'
                    self.dict:
                    'val' → the integer value (e.g., 5)

                String Literal
                    self.elem_type: 'string'
                    self.dict:
                    'val' → the string value (e.g., "hello")
        """

        if expression_node.elem_type=='string':
            return expression_node.get('val')
        
        elif expression_node.elem_type=='int':
            return expression_node.get('val')
        
        elif expression_node.elem_type=='qname':
            var_name=expression_node.get('name')
            if var_name not in self.variable_name_to_value:
                super().error(ErrorType.NAME_ERROR, f"expression variable name undefined")
            return self.variable_name_to_value[var_name] #fetch variable from our dictionary
        
        elif expression_node.elem_type=='fcall':
            return self.func_call_statement(expression_node) #call function.
        
        elif expression_node.elem_type=='+':
            arg1=expression_node.get('op1')
            arg2=expression_node.get('op2')
            if (not isinstance(arg1,Element)) or (not isinstance(arg2,Element)):
                super().error(ErrorType.TYPE_ERROR, f"+ argument is not an element")
            
            # This evealuation step automatically handles any nested functions or +/- such as (9+(7-8)) reflected in AST after parsing
            op1=self.evaluate_expression(arg1)
            op2=self.evaluate_expression(arg2)
            if (not isinstance(op1,int)) or (not isinstance(op2,int)): #f an expression attempts to operate on a string (e.g., 5 + "foo"), then your interpreter must generate an error
                super().error(ErrorType.TYPE_ERROR, f"adding non integers")

            sum=op1+op2

            return sum
        elif expression_node.elem_type=='-':
            arg1=expression_node.get('op1')
            arg2=expression_node.get('op2')
            if (not isinstance(arg1,Element)) or (not isinstance(arg2,Element)):
                super().error(ErrorType.TYPE_ERROR, f"+ argument is not an element")
            
            # This evealuation step automatically handles any nested functions or +/- such as (9+(7-8))
            op1=self.evaluate_expression(arg1)
            op2=self.evaluate_expression(arg2)
            if (not isinstance(op1,int)) or (not isinstance(op2,int)):
                super().error(ErrorType.TYPE_ERROR, f"adding non integers")

            dif=op1-op2

            return dif


        return
    
    
    






