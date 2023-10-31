import numpy as np

class ModelFitter():
    """
    A class to handle the model fitter

    ...

    Attributes
    ----------

    equation: str
        equation of the function to be fitted
    parameter: any
        fitted parameters of the function

    
    Methods
    -------
    fit():
        returns the fitted parameters of the function equation based on the given data

    """


    def __init__(self, equation):
        self.equation = equation
        self.parameter = None

    def fit(self, data, equation):
        pass