"""
This module provides functions to fit a model to data.

The fitting routines are based on the assumption that the model is of type VPCModel
with provided data consisting of a list of lists where each sub-list is a column from a datasheet.
"""
# standard library imports
import logging
from typing import Any

# related third party imports
import numpy as np
import numpy.typing as npt
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
    if model.is_ode():
        _fit_ode(model, data)
    else:
        _fit_reg(model, data)


def _fit_ode(model: VPCModel, data: list[list[int | float]]) -> None:
    """Fit a model represented by an ordinary differential equation (ODE) to provided data.

    This function sets the internal variables of the model to reflect the fit.

    :param model: The model that is to be fit.
    :type model: VPCModel
    :param data: The provided data to which the model is fitted.
    :type data: list[list[int  |  float]]
    :raises RuntimeError: If an error occurs during the minimization process or while solving the initial value problem.
    """
    if len(model.independent_var) > 1:
        ode_func = model.model_function
    else:
        ode_func = lambda t, *args: model.model_function(*args) # type: ignore

    t_data = data[0]
    y_data = data[1]

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
        :raises RuntimeError: If an error occurrs while solving the initial value problem.
        :return: The sum of squares of the differences between a certain set of constants and\
        the result data.
        :rtype: Any
        """
        try:
            sol = solve_ivp(
                fun=ode_func,
                t_span=[t_data[0], t_data[-1]],
                y0=[y0],
                t_eval=t_data,
                args=(*consts,)
            )
        except ValueError as ve:
            logger.error(
                f"Value Error occurred in solve_ivp. Message:\n"
                f"  {ve}"
                f"  List of values for the call:\n"
                f"  {ode_func=}, span={t_data[0]=}, {t_data[-1]}, {y0=}, t_eval={t_data}, args={consts}"
            )
            logger.debug(f"Trying again with altered initial value y0 *= 0.1.")
            try:
                sol = solve_ivp(
                fun=ode_func,
                t_span=[t_data[0], t_data[-1]],
                y0=[y0*0.1],
                t_eval=t_data,
                args=(*consts,)
            )
            except Exception as e:
                raise RuntimeError("Error in solving initial value problem.") from e
        except RuntimeError as re:
            logger.error(
                f"Encountered a runtime error while solving initial value problem. See:\n"
                f"  {re}"
            )
            raise
        return np.sum((sol.y[0] - y_data)**2)

    initial_guess = [1 for c in model.constants]

    try:
        result = minimize(objective_function, initial_guess, args=(t_data, y_data, y_data[1]))
        fitted_consts = dict(zip(model.constants, result.x))
        model.set_fit_information(fitted_consts)
    except RuntimeError as re:
        logger.error(
            f"Failed to minimize the objective function."
            f"  This error suggests a problem in solving the initial value problem. See:"
            f"  {re}"
        )
        model.set_fit_information(error=True)
        raise
    except Exception as e:
        logger.error(
            f"Failed to minimize the objective function. See:"
            f"  {e}"
        )
        model.set_fit_information(error=True)
        raise RuntimeError("Error in minimize function.") from e


def _fit_reg(model: VPCModel, data: list[list[int | float]]) -> None:
    """Fit a model that is not represented by an ordinary differential equation (ODE) to provided data.

    This function sets the internal parameters of the model to reflect the fit.

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

    try:
        popt, pcov = curve_fit(
            f=formatted_function,
            xdata=running_var_vals,
            ydata=model_res_vals,
            p0=np.ones(len(model.constants))
        )
        fitted_consts = dict(zip(model.constants, popt))
        model.set_fit_information(fitted_consts)
        print(evaluate_fit(pcov))
    except ValueError as ve:
        logger.error("Value error in curve fitting regular function.")
        raise RuntimeError("Value error in curve_fit.") from ve
    except RuntimeError as re:
        logger.error("Runtime error in curve fitting regular function.")
        raise


def check_model_is_valid_vector(model: VPCModel, columns: int) -> bool:
    """Checks if the model is valid when comparing it the the sample data.

    A model is an invalid if there are not enough columns in the data to account for all
    independent variables and the result components.

    :param model: The model to be checked.
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
        raise RuntimeError("Each model component needs its own data column.")
    return model.is_vector()


def evaluate_fit(pcov: npt.NDArray) -> dict[str, float]:
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