# standard library imports
import logging
from dataclasses import dataclass
from re import search, finditer
import re

# related third party imports
from sympy import FunctionClass
from sympy import lambdify, symbols, parse_expr


logger = logging.getLogger("VPCModel")

@dataclass
class VPCModel():
    """Dataclass to store a model and extract relevant information from it."""

    _model_string: str
    _independent_var: list[str]

    def __post_init__(self) -> None:
        """Set some internal variables post initialization of the model."""

        self._expression_string: str = self.cut_off_lhs()
        self._model_function: FunctionClass = self.model_string_to_function()
        self._symbols: list[str] = self.extract_symbols(self._independent_var)
        self._constants: list[str] = [c for c in self._symbols if c not in self._independent_var]
        self._components: int = self.expression_string.count(",") + 1

        self._fitted_consts: dict[str, float] | None = None # {"a": 1.437, "b": 3.25, ...}
        self._resulting_function: str | None = None

    @property
    def model_string(self) -> str:
        """Property to return the model string of the class instance.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: The model string without leading/trailing spaces and some character replacements.
        :rtype: str
        """
        return self.format_eq(self._model_string)

    @property
    def independent_var(self) -> list[str]:
        """Property to return the list of independent variables of the class instance.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: List of all independent variables of the model.
        :rtype: list[str]
        """
        return self._independent_var

    @property
    def expression_string(self) -> str:
        """Property to return the expression string (right-hand side) of the class instance.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: The expression string of the model.
        :rtype: str
        """
        return self._expression_string

    @property
    def model_function(self) -> FunctionClass:
        """Property to return the lambdified model function of the class instance.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: FunctionClass / lambda expression of the model function.
        :rtype: sympy.FunctionClass
        """
        return self._model_function

    @property
    def symbols(self) -> list[str]:
        """Property to return the list of symbols that are in the expression of the class instance.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: List of all symbols in the model expression.
        :rtype: list[str]
        """
        return self._symbols

    @property
    def constants(self) -> list[str]:
        """Property to return the list of constants in the model expression that are to be fitted.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: List of all constants in the model expression.
        :rtype: list[str]
        """
        return self._constants

    @property
    def components(self) -> int:
        """Property to return the number of components the result has, i.e. if it is a vector.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: Number of components of the model expression.
        :rtype: int
        """
        return self._components

    @property
    def fitted_consts(self) -> dict[str, float]:
        """Property to return the dictionary of fitted constants of the function.
        If this value is not set at the time of accessing it through this property,
        an empty dictionary will be returned.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: Dictionary with constant:value as its pairs.
        :rtype: dict[str, float]
        """
        if self._fitted_consts is None:
            return {}
        return self._fitted_consts

    @property
    def resulting_function(self) -> str:
        """Property to return the stringified function with the computed constants in it.
        If this value is not set at the time of accessing it through this property,
        an empty string will be returned.

        A property without an accompanying setter is used to prohibit setting this value.

        :return: The string of the final/resulting function after the fit.
        :rtype: str
        """
        if self._resulting_function is None:
            return ""
        return self._resulting_function

    def _set_fitted_consts(self, fitted_consts_dict: dict[str, float]) -> None:
        """Function to set the computed fitted constants to its internal variable.

        :param fitted_consts_dict: Dictionary of {'const_name': value}
        :type fitted_consts_dict: dict[str, float]
        """
        self._fitted_consts = fitted_consts_dict

    def _set_resulting_function(self, fitted_function: str) -> None:
        """Function to set the computed fitted function to its internal variable.

        :param fitted_function: The fitted function string.
        :type fitted_function: str
        """
        self._resulting_function = fitted_function

    def format_eq(self, equation: str) -> str:
        """Replaces some characters for others in a string. Strips leading and trailing spaces.

        :param equation: The string in which characters will be replaced.
        :type equation: str
        :return: Stripped input string with replaced characters.
        :rtype: str
        """
        return equation.strip().replace("^", "**")

    def cut_off_lhs(self) -> str:
        """Cuts off the left hand side of an equation, indicated by an equals sign.
        Also strips leading and trailing spaces and replaces some characters if needed.

        :return: Model equation without left hand side, including the equals sign.
        :rtype: str
        """
        equation = self._model_string
        ind = equation.find("=")
        if ind != -1:
            return self.format_eq(equation[ind+1:])
        else:
            return self.format_eq(equation)

    def cut_off_rhs(self) -> str:
        """Cuts off the right hand side of an equation, indicated by an equals sign.
        Also strips leading and trailing spaces and replaces some characters if needed.

        :return: Model equation without right hand side, including the equals sign.
        :rtype: str
        """
        equation = self._model_string
        ind = equation.find("=")
        if ind != -1:
            return self.format_eq(equation[:ind])
        else:
            return self.format_eq(equation)

    def extract_symbols(self, sorting_prio: list[str] | None = None) -> list[str]:
        """Extract all unique symbols out of the model equations right-hand side.

        Unique symbols are single or multi-character sequences consisting of letters.
        If a sorting prio is given, the characters in it are returned at the front of the output,
        the rest is ordered alphabetically.

        :param sorting_prio: Characters to be placed at the start of the output , defaults to None
        :type sorting_prio: list[str] | None, optional
        :return: All unique symbols in the expression on the right-hand of the equation.
        :rtype: list[str]
        """
        expression = self._model_string

        if "=" in expression:
            expression = self.cut_off_lhs()

        seen = set()
        unique_symbols = []

        for match in finditer(r"\b[a-zA-Z]+\b|\b[a-zA-Z]\b", expression):
            symbol = match.group()
            if symbol not in seen:
                seen.add(symbol)
                unique_symbols.append(symbol)

        if sorting_prio:
            def custom_sort_key(char, prio):
                if char in prio:
                    return (0, char)
                else:
                    return (1, char)

            unique_symbols.sort(key=lambda c: custom_sort_key(c, sorting_prio))

        return unique_symbols

    def model_string_to_function(self) -> FunctionClass:
        """Create a lambda function based on the model equation.

        Extracts all symbols from the expression and converts them to SymPy symbols.
        Finally lambdifies the expression to return a callable model function.

        :return: Lambdified model expression.
        :rtype: FunctionClass
        """

        sorted_symbols: list[str] = self.extract_symbols(self._independent_var)
        expression: str = self._expression_string
        sympy_vars = symbols(sorted_symbols)
        parsed_expression = parse_expr(expression)
        func: FunctionClass = lambdify(sympy_vars, parsed_expression, ["scipy", "numpy"])

        return func

    def is_ode(self) -> bool:
        """Determines whether the model is an ODE of at most 2nd order.

        :return: True if at most 2nd order ODE, False otherwise.
        :rtype: bool
        """
        # # pattern d^2{variable}/d{other_variable}^2
        # second_derivative = r"\bd\^2([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\^2\b"
        # # pattern d{variable}/d{other_variable}
        # first_derivative = r"\bd([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\b"
        # # pattern y''
        # symbol_prime_prime = r"[a-zA-Z]+''"
        # # pattern y'
        # symbol_prime = r"[a-zA-Z]+'"

        # patterns = [second_derivative, first_derivative, symbol_prime_prime, symbol_prime]

        # match = any(search(pattern, self._model_string) for pattern in patterns)

        # return match

        patterns = [
            (
                re.compile(r"\bd\^2([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\^2\b"),
                "Pattern d^2(a)/d(b)^2"
            ),
            (
                re.compile(r"\bd([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\b"),
                "Pattern d(a)/d(b)"
            ),
            (
                re.compile(r"[a-zA-Z]+''"),
                "Pattern ()'"
            ),
            (
                re.compile(r"[a-zA-Z]+'"),
                "Pattern ()''"
            )
        ]

        for pattern, pattern_name in patterns:
            match = search(pattern=pattern, string=self._model_string)
            if match:
                logger.debug(f"Match found with: {pattern_name}, function determined to be an ODE.")
                return True
        logger.debug("No match found, function determined to not be an ODE.")
        return False

    def is_vector(self) -> bool:
        """Determine whether the function is a vector based on the number of its components.

        :raises Exception: If components are less than 1.
        :return: True if the model is a vector, False otherwise.
        :rtype: bool
        """
        if self.components < 1:
            raise Exception("Model components are unexpectedly less than 1.")
        return self.components > 1