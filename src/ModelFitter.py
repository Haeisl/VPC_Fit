"""
This module provides functions to fit a model to data.

The fitting routines are based on the assumption that the model is of type VPCModel
with provided data consisting of a list of lists where each sub-list is a column from a datasheet.
"""
# standard library imports
import logging
from typing import Any, Callable

# related third party imports
import numpy as np
import numpy.typing as npt
from scipy.integrate import odeint
from scipy.optimize import curve_fit
from scipy.optimize import minimize

# local imports
from src.VPCModel import VPCModel


logger = logging.getLogger("ModelFitter")


def fit(model: VPCModel, data: list[list[int | float]]) -> None:
    """Main entry function for fitting.
    Fitting a model to data, using slightly different routines for models
    that are differential equation. Should be able to handle most regular functions
    and ODEs up to second order.

    :param model: The model that is supposed to be fitted.
    :type model: VPCModel
    :param data: The data the model is supposed to be fitted to.
    :type data: list[list[int  |  float]]
    """
    if model.is_ode():
        formatted_function, running_var_vals, model_res_vals = _fit_ode(model, data)
    else:
        formatted_function, running_var_vals, model_res_vals = _fit_reg(model, data)

    popt, pcov = curve_fit(
        f=formatted_function,
        xdata=running_var_vals,
        ydata=model_res_vals,
        p0=np.ones(len(model.constants))
    )
    fitted_consts = dict(zip(model.constants, popt))
    set_model_information(model, fitted_consts)


# def _fit_ode(
#     model: VPCModel, data: list[list[int | float]]
#     ) -> tuple[Callable, tuple[npt.NDArray[Any], ...], npt.NDArray[Any]]:
#     return
def _fit_ode(
    model: VPCModel,
    data: list[list[int | float]]
    ) -> tuple[Callable, tuple[npt.NDArray[Any], ...], npt.NDArray[Any]]:
    """Fit a model to data assuming it's a system of ordinary differential equations (ODE).

    :param model: The model that is supposed to be fitted.
    :type model: VPCModel
    :param data: The data the model is supposed to be fitted to.
    :type data: list[list[int  |  float]]
    :return: A tuple containing the formatted function, independent variable values, and model result values.
    :rtype: tuple[Callable, tuple[npt.NDArray[Any], ...], npt.NDArray[Any]]
    """
    num_indep_vars = len(model.independent_var)
    # Assuming the first column represents the independent variable
    independent_variable = np.array(data[0])
    # Assuming the rest of the columns represent dependent variables
    dependent_variables = [np.array(col) for col in data[1:]]
    initial_conditions = np.ones(num_indep_vars)  # Initial conditions for the ODE system
    model_solution = odeint(model.model_function, initial_conditions, independent_variable)
    formatted_function = lambda indep, *args: np.ravel(model_solution(indep, *args))
    model_res_vals = np.ravel(dependent_variables)

    return formatted_function, (independent_variable,), model_res_vals


def _fit_reg(
    model: VPCModel,
    data: list[list[int | float]]
    ) -> tuple[Callable, tuple[npt.NDArray[Any], ...], npt.NDArray[Any]]:
    """TODO: add docu"""
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

    return formatted_function, running_var_vals, model_res_vals

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