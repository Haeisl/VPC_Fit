# standard library imports
import logging
from dataclasses import dataclass
from re import search, finditer
from typing import Optional

# related third party imports
from sympy import FunctionClass
from sympy import lambdify, symbols, parse_expr


logger = logging.getLogger("VPCModel")

@dataclass
class VPCModel():
    _model_string: str
    _independent_var: list[str]

    def __post_init__(self) -> None:
        self._expression_string: str = self.cut_off_lhs()
        self._model_function: FunctionClass = self.model_string_to_function()
        self._symbols: list[str] = self.extract_symbols(self._independent_var)
        self._constants: list[str] = [c for c in self._symbols if c not in self._independent_var]
        self._components: int = self.expression_string.count(",") + 1

        self._fitted_consts: Optional[dict[str, float]] = None # {"a": 1.437, "b": 3.25, ...}
        self._resulting_function: Optional[str] = None

    @property
    def model_string(self) -> str:
        return self.format_eq(self._model_string)

    @property
    def independent_var(self) -> list:
        return self._independent_var

    @property
    def expression_string(self) -> str:
        return self._expression_string

    @property
    def model_function(self) -> FunctionClass:
        return self._model_function

    @property
    def symbols(self) -> list[str]:
        return self._symbols

    @property
    def constants(self) -> list[str]:
        return self._constants

    @property
    def components(self) -> int:
        return self._components

    @property
    def fitted_consts(self) -> dict[str, float]:
        if self._fitted_consts is None:
            return {}
        return self._fitted_consts

    @property
    def resulting_function(self) -> str:
        if self._resulting_function is None:
            return ""
        return self._resulting_function

    def _set_fitted_consts(self, fitted_consts_dict: dict[str, float]) -> None:
        self._fitted_consts = fitted_consts_dict

    def _set_resulting_function(self, fitted_function: str) -> None:
        self._resulting_function = fitted_function

    def format_eq(self, equation: str) -> str:
        return equation.strip().replace("^", "**")

    def cut_off_lhs(self) -> str:
        """cuts off the left side of an equation including the equals sign if exists.
        Needed internally to check the input by the user.

        :param equation: entered equation by the user
        :type equation: str
        :return: entered equation without left hand side and "="
        :rtype: str
        """
        equation = self._model_string
        ind = equation.find("=")
        if ind != -1:
            return self.format_eq(equation[ind+1:])
        else:
            return self.format_eq(equation)

    def cut_off_rhs(self):
        equation = self._model_string
        ind = equation.find("=")
        if ind != -1:
            return self.format_eq(equation[:ind])
        else:
            return self.format_eq(equation)

    def extract_symbols(self, sorting_prio: Optional[list] = None) -> list[str]:
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
        """returns a lambda function based on the equation given by the user."""

        sorted_symbols = self.extract_symbols(self._independent_var)
        sympy_vars = symbols(sorted_symbols)
        expression = self._expression_string

        parsed_expression = parse_expr(expression)
        func: FunctionClass = lambdify(sympy_vars, parsed_expression, ["scipy", "numpy"])

        return func

    def is_ode(self) -> bool:
        """checks whether self._model_string is an ODE of at most 2nd order.

        :return: true if at most 2nd order ODE, false otherwise
        :rtype: bool
        """
        # pattern d^2{variable}/d{other_variable}^2
        second_derivative = r"\bd\^2([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\^2\b"
        # pattern d{variable}/d{other_variable}
        first_derivative = r"\bd([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\b"
        # pattern y''
        symbol_prime_prime = r"[a-zA-Z]+''"
        # pattern y'
        symbol_prime = r"[a-zA-Z]+'"

        patterns = [second_derivative, first_derivative, symbol_prime_prime, symbol_prime]

        match = any(search(pattern, self._model_string) for pattern in patterns)

        return match

    def is_vector(self) -> bool:
        if self.components < 1:
            raise Exception("Model components are unexpectedly less than 1.")
        return self.components > 1