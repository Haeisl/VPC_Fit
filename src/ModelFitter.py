import numpy as np

class ModelFitter():
    """This is a class to handle the model fitter
    """

    def __init__(self, equation):
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
        :type data: supported data types are currently excel, csv and xml
        :param equation: the function equation entered by the user
        :type equation: str
        """
        pass