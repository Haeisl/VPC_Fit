
import numpy as np
from scipy.optimize import curve_fit
from sympy import FunctionClass
import sympy


def model_string_to_function(expression, symbols) -> FunctionClass:
        """returns a lambda function based on the equation given by the user."""

        sympy_vars = sympy.symbols(symbols)

        #parsed_expression = sympy.parse_expr(expression)
        parsed_expression = sympy.sympify(expression)
        func: FunctionClass = sympy.lambdify(sympy_vars, parsed_expression)

        return func


def main() -> None:
    # a = 2.5, b = 1.0
    # f(t) = (2.5*t**2 + 1, 2.5*t+1)
    # symbols = ["t", "a", "b"]
    symbols = ["t", "a"]
    consts = ["a"]
    # func = model_string_to_function("(a*t**2+b, a*t)", symbols)
    func = model_string_to_function("(a*sin(t), a+t)", symbols)
    # func(t, a, b)

    format_func = lambda *args: np.array(func(*args)).ravel()

    xdata = np.linspace(0, 5, 10)
#     y = np.array([(0.,2.10966154),(3.5847688,3.98163183),(3.18088023,  1.42336797),
#  (-0.76227185, -2.71863183),(-3.85726847, -3.8356971),(4.,4.55555556),
#   (5.11111111,5.66666667),(6.22222222,  6.77777778),(7.33333333,7.88888889),
#   (8.44444444,9.)])
#     y = y.ravel()
    y1 = [0.,3.5847688,3.18088023,-0.76227185,-3.85726847,4.,5.11111111,6.22222222,7.33333333,8.44444444]
    y2 = [2.10966154,3.98163183,  1.42336797, -2.71863183, -3.8356971,4.55555556,5.66666667,  6.77777778,7.88888889,9.]
    y = np.ravel(list(zip(y1,y2)))
    # y = func(xdata, 4)
    rng = np.random.default_rng()
    y_noise = 0.2 * rng.normal(size=xdata.size*2)
    # y_noise = 0.2 * rng.normal(size=xdata.size)
    ydata = y + y_noise

    # vielleicht ydata.T.ravel()
    # https://stackoverflow.com/questions/41306732/how-to-properly-define-vector-function-for-scipys-curve-fit
    popt, pcov = curve_fit(format_func, xdata, ydata, p0=np.ones(len(consts)))
    # popt, pcov = curve_fit(func, xdata, ydata)

    print(popt)

if __name__ == '__main__':
    main()


"""
TODO:
result components irgendwie in VPCModel rein bekommen,
s.d. wir im ModelFitter je nach dem,
ob es sich um einen vektor handelt eine der beiden implementationen oben anwenden.

Überlegen wie Reihenfolge von is_ode und quasi dem neuen is_vector dann funktioniert.
Wahrscheinlich nicht zulassen, dass vektor aus ODE möglich ist.
df/dt = (..., ..., ...) -> nein
is_ode && res_comps != 1 -> nein
is_ode && , in expr -> nein



"""