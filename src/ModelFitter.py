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
        # T | Temporary, should be replaced with an earlier check
        # E | maybe ask user what variable should stay?
        # M | otherwise just assume 't' and throw error else
        # P | 
        t = symbols('t')
        expr = sympify(equation)
        func = lambdify(t, expr, 'numpy')
        
        return func
        