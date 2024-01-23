import re
from os.path import exists

class Validator():

    @staticmethod
    def extract_variables(input_str: str) -> list:
        """extracts variables out of a mathematical expression

        :param input_str: input expression
        :type input_str: str
        :return: array of variables of the given expression
        :rtype: list(str)
        """
        seen = set()
        unique_vars = []

        for match in re.finditer(r'\b[a-zA-Z_]\w*\b|\b[a-zA-Z_]\b', input_str):
            variable_name = match.group()
            if variable_name not in seen:
                seen.add(variable_name)
                unique_vars.append(variable_name)

        return unique_vars

    @staticmethod
    def cut_off_lhs(equation:str) -> str:
        """cuts off the left side of an equation if exists
        is needed internally to check the input by the user

        :param equation: entered equation by the user
        :type equation: str
        :return: entered equation without lhs
        :rtype: str
        """
        ind = equation.find('=')
        if ind != -1:
            return equation[ind:].lstrip()
        else:
            return equation.lstrip()

    @staticmethod
    def are_variables_consistent(
        entered_model: str,
        entered_indep_var: str
    ) -> bool:
        indep_vars = re.split(r',\s|,|;\s|;', entered_indep_var)
        indep_vars = ['t'] if indep_vars == [''] else indep_vars
        expression = Validator.cut_off_lhs(entered_model)
        variables = Validator.extract_variables(expression)

        unfound_vars = []
        for var in indep_vars:
            if var not in variables:
                unfound_vars.append(var)

        return bool(unfound_vars)

    @staticmethod
    def does_file_path_exist(
        file_path: str
    ) -> bool:
        return exists(file_path)

    @staticmethod
    def are_components_equal(
        given_comps: int,
        expression: str
    ) -> bool:
        expression = Validator.cut_off_lhs(expression)
        assumed_comps = expression.count(',') + 1
        return given_comps == assumed_comps