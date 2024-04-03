"""
This module provides functions to fit a model to data.

The fitting routines are based on the assumption that the model is of type VPCModel
with provided data consisting of a list of lists where each sub-list is a column from a datasheet.
"""
# standard library imports
import inspect
import logging
from typing import Any, Callable

# related third party imports
import numpy as np
import numpy.typing as npt
import sympy as sp
from scipy.integrate import odeint
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit
from scipy.optimize import minimize

# local imports
from src.VPCModel import VPCModel


logger = logging.getLogger("ModelFitter")


def fit(model: VPCModel, data: list[list[int | float]]) -> None:
    """Main entry function for the fitting process. Delegates ``model`` and ``data`` to the correct
    fitting routine based on whether it's an ordinary differential equation or not.

    :param model: The model that is supposed to be fitted.
    :type model: VPCModel
    :param data: The data the model is supposed to be fitted to.
    :type data: list[list[int  |  float]]
    """
    print(inspect.getsource(model.model_function))
    if model.is_ode():
        _fit_ode(model, data)
    else:
        _fit_reg(model, data)


def _fit_ode(model: VPCModel, data: list[list[int | float]]) -> None:
    """Fitting routine that fits a model that's an ordinary differential equation to the provided
    data. Sets the models internal variables to reflect the fit.

    :param model: The model that is to be fit.
    :type model: VPCModel
    :param data: The provided data to which the model is fitted.
    :type data: list[list[int  |  float]]
    """
    initial_value: list[float] = model.initial_values

    ode_func = add_argument_if_not_exists(model.model_function, 't')

    t_data = data[0]
    y_data = data[1:]

    def objective_function(
        consts: tuple[float,...],
        t_data: list[float],
        y_data: list[float],
        y0: float
    ) -> Any:
        """Helper Function that is the objective to minimize. Used to fit the constants.

        :param consts: The constants of the function.
        :type consts: tuple[float,...]
        :param t_data: The data for the independent variable, e.g. the time ``t``.
        :type t_data: list[float]
        :param y_data: The resulting data.
        :type y_data: list[float]
        :param y0: The initial condition of the differential equation.
        :type y0: float
        :return: The sum of squares of the differences between a certain set of constants and\
        the result data.
        :rtype: Any
        """
        sol = solve_ivp(
            fun=ode_func,
            t_span=[t_data[0], t_data[-1]],
            y0=[y0],
            t_eval=t_data,
            args=consts
        )
        return np.sum((sol.y[0] - y_data)**2)

    initial_guess = [0.1 for i in model.constants]
    result = minimize(objective_function, initial_guess, args=(t_data, y_data, initial_value[1]))

    fitted_consts = dict(zip(model.constants, result.x))
    set_model_information(model, fitted_consts)


def _fit_reg(model: VPCModel, data: list[list[int | float]]) -> None:
    """Fitting routine that gets called when the underlying model is not an ordinary differential
    equation. Sets the model's internal parameters to reflect the fit.

    :param model: The model that is to be fitted.
    :type model: VPCModel
    :param data: The provided data to which the model is fitted.
    :type data: list[list[int  |  float]]
    :return: Tuple consisting of a callable function, as well as values\
    for the independent variable and their resulting data, taken from the provided input data
    :rtype: None
    """
    num_indep_vars = len(model.independent_var)
    if check_model_is_valid_vector(model, len(data)):
        # assumption: first col for independent var, rest for results for components in order
        formatted_function = lambda indep, *args: np.ravel(model.model_function(*indep, *args))
        model_res_vals = np.array(list(zip(*data[num_indep_vars:]))).T.ravel()
    else:
        # assumption: first col for independent var, second for results
        formatted_function = lambda indep, *args: model.model_function(*indep, *args)
        model_res_vals = np.array(data[num_indep_vars])

    running_var_vals = tuple(np.array(data[i]) for i in range(num_indep_vars))

    popt, pcov = curve_fit(
        f=formatted_function,
        xdata=running_var_vals,
        ydata=model_res_vals,
        p0=np.ones(len(model.constants))
    )

    fitted_consts = dict(zip(model.constants, popt))
    set_model_information(model, fitted_consts)


def add_argument_if_not_exists(func: Callable, arg_name: str) -> Callable:
    """Helper function that adds an argument ``arg_name`` to a supplied function ``func`` if that
    argument is not already present.

    :param func: The function that gets another argument, if it doesn't already exist.
    :type func: Callable
    :param arg_name: The name of the argument that is checked or added.
    :type arg_name: str
    :return: A function that will always have an argument ``arg_name``.
    :rtype: Callable
    """
    # Get the signature of the original function
    original_signature = inspect.signature(func)

    # Check if the argument already exists in the function signature
    if arg_name in original_signature.parameters:
        return func  # Argument already exists, no need to modify the function

    # Define a new parameter
    new_parameter = inspect.Parameter(arg_name, inspect.Parameter.POSITIONAL_OR_KEYWORD)

    # Update the function signature with the new parameter
    new_parameters = list(original_signature.parameters.values())
    new_parameters.append(new_parameter)
    new_signature = original_signature.replace(parameters=new_parameters)

    # Create a new function with the updated signature
    def wrapper(*args, **kwargs):
        bound_arguments = new_signature.bind(*args, **kwargs)
        return func(*bound_arguments.args, **bound_arguments.kwargs)

    # Copy the original function's metadata to the wrapper function
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__

    return wrapper


def check_model_is_valid_vector(model: VPCModel, columns: int) -> bool:
    """Checks if the model is valid when comparing it the the sample data.
    A model is an invalid if there are not enough columns in the data to account for all
    independent variables and the result components.

    :param model: The model that is to be checked.
    :type model: VPCModel
    :param columns: The number of columns in the provided data.
    :type columns: int
    :raises Exception: If there are too few or too many columns in the data.\
    Too few make it impossible to fit the model, too many make it ambiguous as to what the extra\
    columns are supposed to mean, or which columns are even to be regarded and which ones not.
    :return: Whether the model is a vector.
    :rtype: bool
    """
    num_indep_vars = len(model.independent_var)
    has_invalid_dimensions: bool = model.components + num_indep_vars != columns
    if has_invalid_dimensions:
        raise Exception("Each model component needs its own data column.")
    return model.is_vector()


def evaluate_fit(pcov):
    """Evaluate the goodness of fit based on the covariance matrix.

    :param pcov: Covariance matrix of the fit.
    :type pcov: 2D-array
    :return: Dictionary containing evaluation metrics.
    :rtype: dict
    """
    if pcov is None:
        raise ValueError("Covariance matrix 'pcov' cannot be None.")

    # Extract variances from the diagonal of the covariance matrix
    variances = np.diag(pcov)

    # Calculate standard deviations from variances
    std_devs = np.sqrt(variances)

    # Calculate confidence intervals assuming normal distribution
    confidence_intervals = 1.96 * std_devs  # 95% confidence interval for a normal distribution

    # Calculate the mean squared error (MSE) as a measure of goodness of fit
    # This is the average squared difference between observed and predicted values
    mse = np.mean(variances)

    # Calculate the root mean squared error (RMSE)
    rmse = np.sqrt(mse)

    # Construct a dictionary to hold evaluation metrics
    evaluation_metrics = {
        "variances": variances,
        "std_devs": std_devs,
        "confidence_intervals": confidence_intervals,
        "mse": mse,
        "rmse": rmse
    }

    return evaluation_metrics


def set_model_information(model: VPCModel, fitted_consts: dict[str, float]) -> None:
    """Set the fitted model information to the models internal variables.

    :param model: The fitted model that gets its information set.
    :type model: VPCModel
    :param fitted_consts: The fitted model constants.
    :type fitted_consts: dict[str, float]
    """
    model._set_fitted_consts(fitted_consts)
    res_func = model.model_string
    for constant in fitted_consts:
        res_func = res_func.replace(constant, f"{fitted_consts[constant]:.2f}")
    res_func = res_func.replace("**", "^")
    res_func = res_func.replace("+-", "-")
    res_func = res_func.replace("+", " + ")
    res_func = res_func.replace("-", " - ")
    model._set_resulting_function(res_func)