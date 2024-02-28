from ctypes import Union
from dataclasses import dataclass
from sympy import lambdify as sym_lambdify, symbols as sym_symbols, parse_expr as sym_parse_expr
from re import search as re_search, finditer as re_finditer
from typing import Any, Optional

class VPCModel():
    def __init__(self, model_string: str, independent_var: list[str]) -> None:
        self._model_string = model_string
        self._independent_var = independent_var

        self._expression_string: Optional[str] = None
        self._symbols: Optional[list[str]] = None
        self._constants: Optional[list[str]] = None

        self._fitted_consts: Optional[dict[str, float]] = None # {'a': 1.437, 'b': 3.25, ...}
        self._resulting_function: Optional[str] = None

    @property
    def model_string(self) -> str:
        return self.format_eq(self._model_string)

    @property
    def independent_var(self) -> list:
        return self._independent_var

    @property
    def expression_string(self) -> str:
        if self._expression_string is None:
            self._expression_string = self.cut_off_lhs()
        return self._expression_string

    @property
    def symbols(self) -> list[str]:
        if self._symbols is None:
            self._symbols = self.extract_symbols()
        return self._symbols

    @property
    def constants(self) -> list[str]:
        if self._symbols is None:
            self._symbols = self.extract_symbols()
        if self._constants is None:
            self._constants = [c for c in self._symbols if c not in self._independent_var]
        return self._constants

    @property
    def fitted_consts(self) -> Optional[dict[str, float]]:
        if self._fitted_consts is None:
            return None
        return self._fitted_consts

    @property
    def resulting_function(self) -> Any:
        return self._resulting_function


    def _set_fitted_consts(self, fitted_consts_dict: dict[str, float]) -> None:
        self._fitted_consts = fitted_consts_dict


    def format_eq(self, equation: str) -> str:
        return equation.strip().replace('^', '**')


    def cut_off_lhs(self) -> str:
        """cuts off the left side of an equation including the equals sign if exists.
        Needed internally to check the input by the user.

        :param equation: entered equation by the user
        :type equation: str
        :return: entered equation without left hand side and '='
        :rtype: str
        """
        equation = self._model_string
        ind = equation.find('=')
        if ind != -1:
            return self.format_eq(equation[ind+1:])
        else:
            return self.format_eq(equation)


    def cut_off_rhs(self):
        equation = self._model_string
        ind = equation.find('=')
        if ind != -1:
            return self.format_eq(equation[:ind])
        else:
            return self.format_eq(equation)


    def extract_symbols(self, sorting_prio: Optional[list] = None) -> list[str]:
        expression = self._model_string

        if '=' in expression:
            expression = self.cut_off_lhs()

        seen = set()
        unique_symbols = []

        for match in re_finditer(r'\b[a-zA-Z]+\b|\b[a-zA-Z]\b', expression):
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


    def model_string_to_function(self):
        """returns a lambda function based on the equation given by the user."""

        sorted_symbols = self.extract_symbols(self._independent_var)
        sympy_vars = sym_symbols(sorted_symbols)
        expression = self._expression_string

        parsed_expression = sym_parse_expr(expression)
        func = sym_lambdify(sympy_vars, parsed_expression, 'sympy')

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

        match = any(re_search(pattern, self._model_string) for pattern in patterns)

        return match