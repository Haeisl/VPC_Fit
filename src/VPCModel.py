import re


class VPCModel():

    def __init__(self, model_string: str) -> None:
        self._model_string = model_string
        self._expression_string = None
        self._symbols = None

    @property
    def model_string(self) -> str:
        return self._model_string.strip()

    @model_string.setter
    def model_string(self, _):
        raise TypeError("Cannot set model string manually.")

    @property
    def expression_string(self) -> str:
        if self._expression_string is None:
            self._expression_string = self.cut_off_lhs()
        return self._expression_string

    @expression_string.setter
    def expression_string(self, _):
        raise TypeError("Cannot set expression string manually.")

    @property
    def symbols(self) -> list:
        return self.extract_symbols()

    @symbols.setter
    def symbols(self, _):
        raise TypeError("Cannot set symbols manually.")


    def cut_off_lhs(self) -> str:
        """cuts off the left side of an equation if exists
        is needed internally to check the input by the user

        :param equation: entered equation by the user
        :type equation: str
        :return: entered equation without lhs
        :rtype: str
        """
        equation = self._model_string
        ind = equation.find('=')
        if ind != -1:
            return equation[ind:].strip()
        else:
            return equation.strip()
        

    def cut_off_rhs(self):
        equation = self._model_string
        ind = equation.find('=')
        if ind != -1:
            return equation[:ind].strip()
        else:
            return equation.strip()


    def extract_symbols(self) -> list:
        expression = self._model_string

        if '=' in expression:
            expression = self.cut_off_lhs()

        seen = set()
        unique_symbols = []

        for match in re.finditer(r'\b[a-zA-Z]+\b|\b[a-zA-Z]\b', expression):
            symbol = match.group()
            if symbol not in seen:
                seen.add(symbol)
                unique_symbols.append(symbol)

        return unique_symbols


    def is_ode(self) -> bool:
        """checks whether self._model_string is an ODE of at most 2nd order.

        :return: true if at most 2nd order ODE, false otherwise
        :rtype: bool
        """
        # pattern d^2{variable}/d{other_variable}^2
        second_derivative = r'\bd\^2([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\^2\b'
        # pattern d{variable}/d{other_variable}
        first_derivative = r'\bd([a-zA-Z]+)\/d((?!\1)[a-zA-Z]+)\b'
        # pattern y''
        symbol_prime_prime = r'\b[a-zA-Z]+\'\'\b'
        # pattern y'
        symbol_prime = r'\b[a-zA-Z]+\'\b'

        patterns = [second_derivative, first_derivative, symbol_prime_prime, symbol_prime]

        match = any(re.search(pattern, self._model_string) for pattern in patterns)

        return match