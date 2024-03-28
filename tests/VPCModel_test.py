import pytest
from src.VPCModel import VPCModel

@pytest.fixture
def valid_model():
    model_str = "y = x**2 + 3*x - 5"
    independent_var = ["x"]
    return VPCModel(model_str, independent_var)

@pytest.fixture
def invalid_model_string():
    return "y = x**2 + 3*x - 5 +"

@pytest.fixture
def invalid_independent_var():
    return []

@pytest.fixture
def empty_model_expression():
    return ""

@pytest.fixture
def fitted_consts():
    return {"a": 1.437, "b": 3.25}

@pytest.fixture
def fitted_function():
    return "y = 1.437*x**2 + 3.25*x - 5"

@pytest.fixture
def invalid_mathematical_expression():
    return "y = 1.437*x**2 + 3.25*x - "

@pytest.fixture
def incomplete_equation():
    return "y = "

def test_format_eq(valid_model):
    eq = " x ^ 2 + 3*x"
    formatted_eq = valid_model.format_eq(eq)
    assert formatted_eq == "x ** 2 + 3*x"

def test_cut_off_lhs(valid_model):
    assert valid_model.cut_off_lhs() == "x**2 + 3*x - 5"

def test_cut_off_rhs(valid_model):
    assert valid_model.cut_off_rhs() == "y"

def test_extract_symbols(valid_model):
    assert valid_model.extract_symbols() == ['x']

def test_model_string_to_function(valid_model):
    assert callable(valid_model.model_function)

def test_is_ode():
    model_str_ode = "y'' + y = 0"
    independent_var = ["x"]
    model_ode = VPCModel(model_str_ode, independent_var)
    assert model_ode.is_ode() == True

    model_str_non_ode = "y = x**2 + 3*x - 5"
    model_non_ode = VPCModel(model_str_non_ode, independent_var)
    assert model_non_ode.is_ode() == False

def test_is_vector():
    model_str_single_component = "y = x**2 + 3*x - 5"
    independent_var = ["x"]
    model_single_component = VPCModel(model_str_single_component, independent_var)
    assert model_single_component.is_vector() == False

    model_str_multiple_component = "y = x**2 + 3*x - 5, 2*x"
    model_multiple_component = VPCModel(model_str_multiple_component, independent_var)
    assert model_multiple_component.is_vector() == True

def test_invalid_model_string(invalid_model_string):
    with pytest.raises(Exception):
        independent_var = ["x"]
        VPCModel(invalid_model_string, independent_var)

def test_invalid_independent_var(invalid_independent_var):
    with pytest.raises(Exception):
        model_str = "y = x**2 + 3*x - 5"
        VPCModel(model_str, invalid_independent_var)

def test_empty_model_expression(empty_model_expression):
    with pytest.raises(Exception):
        independent_var = ["x"]
        VPCModel(empty_model_expression, independent_var)

def test_set_and_get_fitted_consts(valid_model, fitted_consts):
    valid_model._set_fitted_consts(fitted_consts)
    assert valid_model.fitted_consts == fitted_consts

def test_set_and_get_resulting_function(valid_model, fitted_function):
    valid_model._set_resulting_function(fitted_function)
    assert valid_model.resulting_function == fitted_function

def test_invalid_mathematical_expression(invalid_mathematical_expression):
    with pytest.raises(Exception):
        independent_var = ["x"]
        VPCModel(invalid_mathematical_expression, independent_var)

def test_incomplete_equation(incomplete_equation):
    with pytest.raises(Exception):
        independent_var = ["x"]
        VPCModel(incomplete_equation, independent_var)
