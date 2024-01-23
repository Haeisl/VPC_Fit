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
        :param parameter: fitted parameter of the function, NONE in the inital state
        :type parameter: list[float], optional
        """
        self.equation = equation
        self.parameter = None

    def fit(self, equation, data, prio=['t'], variables=None):
        """returns the fitted parameters of the given equation based on the input data

        :param equation: the function equation entered by the user
        :type equation: str
        :param data: the user's input measurement data
        :type data: list[VPCData]
        :param prio: priority run variables that are searched first in the equation
        :type prio: list[str]
        :return: variables extracted from the equation, an array with the optimal fitted parameters and a 2-D array with the estimated approximate covariance of this array
        """
        if variables is not None:
            variables = self.extract_variables_sorted(equation, prio)

        x, y = data[0], data[1]

        objective = self.string_to_function(equation, variables)

        # print(inspect.getsource(objective))

        # initGuess = np.ones(len(variables)-1)
        #, p0=initGuess
        result, _ = curve_fit(objective, x, y)

        print(result)

        return result, variables

    def string_to_function(self, equation, variables):
        """returns a lambda function based on the equation given by the user

        :param equation: the function equation that the user enters for the fit
        :type equation: str
        :return: function given by the user as lambda expression
        :rtype: sympy.FunctionClass instance
        """

        sympy_vars = symbols(variables)

        for var, sym_var in zip(variables, sympy_vars):
            equation = equation.replace(var, str(sym_var))

        expr = parse_expr(equation)

        func = lambdify(sympy_vars, expr, 'sympy')

        return func

    def extract_variables_sorted(self, input_str, prio) -> list:
        """extracts variables out of a mathematical expression
        and sorts them such that 'x' would always be the first element
        and the rest according to the alphabet.

        :param input_str: input expression
        :type input_str: str
        :return: array of variables of the given expression
        :rtype: list(str)
        """
        # a, b -> set() -> {a, b} -> tolist() -> [a,b] | [b,a]
        # a*x**2+b*x+c
        # [a,x,b,c]
        # array gets sorted anyway, maybe change from set() + list to only set and then tolist()
        seen = set()
        unique_vars = []

        for match in re.finditer(r'\b[a-zA-Z_]\w*\b|\b[a-zA-Z_]\b', input_str):
            variable_name = match.group()
            if variable_name not in seen:
                seen.add(variable_name)
                unique_vars.append(variable_name)

        def custom_sort_key(char, prio):
            if char in prio:
                return (0, char)
            else:
                return (1, char)

        unique_vars.sort(key=lambda x: custom_sort_key(x, prio))

        return unique_vars

    def validate_expression(self):
        pass


    def fit_ODE(self, equation, data):
        # given Data
        x_axis_data = data[0]
        y_axis_data = data[1]

        # define ODE
        def system_of_ODEs(x, t, equation):
            p1 = equation[0]
            p2 = equation[1]
            dxdt = p1-p2*x
            return dxdt

        # solve ODEs at xaxisData points
        # and return calculated yaxisCalc using
        # current values of the parameters
        def model(x_axis_data, *params):
            # initial condition for ODEs
            y_axis_0 = 0.0
            y_axis_calc = np.zeros(x_axis_data.size)
            for i in np.arange(0, len(x_axis_data)):
                if x_axis_data[i] == 0.0:
                    y_axis_calc[i] = y_axis_0
                else:
                    x_axis_span = np.linspace(0, x_axis_data[i], 101)
                    y_soln = odeint(system_of_ODEs, y_axis_0, x_axis_span, args = (params,))
                    y_axis_calc[i] = y_soln[-1]
            return y_axis_calc

        parameter_soln, pcov = curve_fit(model, x_axis_data, y_axis_data)

        return parameter_soln, pcov