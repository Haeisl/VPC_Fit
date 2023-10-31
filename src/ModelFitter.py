import numpy as np

class ModelFitter():
    """This is a class to handle the model fitter

    :param equation: the equation of the function to be fitted
    :type equation: str
    :param parameter: fitted parameter of the function
    :type parameter: any, optional
    """

    def __init__(self, equation):
        """Constructor method
        """
        self.equation = equation
        self.parameter = None

    def fit(self, data, equation):
        """returns the fitted parameters of the given equation based on the input data 

        :param data: _description_
        :type data: _type_
        :param equation: _description_
        :type equation: _type_
        """
        pass