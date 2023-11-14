import numpy as np
from sympy import sympify, symbols, lambdify

class ModelFitter():
    """This is a class to handle the model fitter
    """

    def __init__(self, equation=None):
        """Constructor method

        :param equation: the equation of the function to be fitted
        :type equation: str
        :param parameter: fitted parameter of the function
        :type parameter: any, optional
        """
        self.equation = equation
        self.parameter = None

    def fit(self, data, equation):
        """returns the fitted parameters of the given equation based on the input data 

        :param data: the user's input measurement data
        :type data: list[VPCData]
        :param equation: the function equation entered by the user
        :type equation: str
        """
        pass
    
    def stringToFunction(self, equation):
        # mf = ModelFitter()
        # func = mf.stringToFunction('a**b+t*c')
        
        # print(func(a=symbols('a'),t=1,b=5,c=3))
        
        variables = set()
        for char in equation:
            if char.isalpha():
                variables.add(char)
        variables = list(variables)
        
        sympyVars = [symbols(var) for var in variables]
        
        for var, symVar in zip(variables, sympyVars):
            equation = equation.replace(var, str(symVar))
        
        expr = sympify(equation)
        
        func = lambdify(sympyVars, expr, 'numpy')
        
        return func
        