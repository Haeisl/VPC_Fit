import re
from os.path import exists


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

def are_variables_consistent(
    entered_model: str,
    entered_indep_var: str
) -> list:
    # check if the independent variables/symbols provided in the additional tab line up
    # with the expression in the model input in the basic tab
    indep_vars = re.split(r',\s|,|;\s|;', entered_indep_var)
    indep_vars = ['t'] if indep_vars == [''] else indep_vars
    expression = cut_off_lhs(entered_model)
    variables = extract_variables(expression)

    unfound_vars = []
    for var in indep_vars:
        if var not in variables:
            unfound_vars.append(var)

    return unfound_vars

def does_file_path_exist(file_path: str) -> bool:
    return exists(file_path)

def are_components_equal(
    given_comps: int,
    expression: str
) -> bool:
    # a vector like function is assumed to be provided like 'x+1, y+1, z+1'
    # with commas separating the components
    # update msg string with info if expression doesn't match provided #components
    expression = cut_off_lhs(expression)
    assumed_comps = expression.count(',') + 1
    return given_comps == assumed_comps