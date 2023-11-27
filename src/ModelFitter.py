import numpy as np
from sympy import parse_expr, symbols, lambdify
from scipy.optimize import curve_fit
from scipy.optimize import minimize
from scipy.integrate import odeint
import re
import inspect

class ModelFitter():
    """This is a class to handle the model fitter
    """

    def __init__(self, equation=None):
        """Constructor method

        :param equation: the equation of the function to be fitted
        :type equation: str
        :param parameter: fitted parameter of the function
        :type parameter: list[float], optional
        """
        self.equation = equation
        self.parameter = None

    def fit(self, equation, data, prio=['t','x']):
        """returns the fitted parameters of the given equation based on the input data 

        :param equation: the function equation entered by the user
        :type equation: str
        :param data: the user's input measurement data
        :type data: list[VPCData]
        """
        
        x, y = data[0], data[1]
        
        variables = self.extractVariables(equation, prio)
        
        objective = self.stringToFunction(equation, variables)
        
        # print(inspect.getsource(objective))
        
        # initGuess = np.ones(len(variables)-1)
        #, p0=initGuess
        result, _ = curve_fit(objective, x, y)
        
        print(result)
        
        return result, variables
    
    def stringToFunction(self, equation, variables):
        """returns a lambda function based on the equation given by the user

        :param equation: the function equation that the user enters for the fit
        :type equation: str
        :return: function given by the user as lambda expression
        :rtype: sympy.FunctionClass instance
        """
        
        sympyVars = symbols(variables)
        
        for var, symVar in zip(variables, sympyVars):
            equation = equation.replace(var, str(symVar))
        
        expr = parse_expr(equation)
        
        func = lambdify(sympyVars, expr, 'sympy')
        
        return func
    
    def extractVariables(self, inputStr, prio):
        """extracts variables out of a mathematical expression
        and sorts them such that 'x' would always be the first element
        and the rest according to the alphabet.

        :param inputStr: input expression
        :type inputStr: str
        :return: array of variables of the given expression
        :rtype: list(str)
        """
        # a, b -> set() -> {a, b} -> tolist() -> [a,b] | [b,a]
        # a*x**2+b*x+c
        # [a,x,b,c]
        # array gets sorted anyway, maybe change from set() + list to only set and then tolist()
        seen = set()
        uniqueVars = []
        
        for match in re.finditer(r'\b[a-zA-Z_]\w*\b|\b[a-zA-Z_]\b', inputStr):
            variableName = match.group()
            if variableName not in seen:
                seen.add(variableName)
                uniqueVars.append(variableName)
        
        def customSortKey(char, prio):
            if char in prio:
                return (0, char)
            else:
                return (1, char)
    
        uniqueVars.sort(key=lambda x: customSortKey(x, prio))
        
        return uniqueVars