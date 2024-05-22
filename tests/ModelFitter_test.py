import pytest
import numpy as np
from src.ModelFitter import fit, _fit_ode, _fit_reg, check_model_is_valid_vector, evaluate_fit
from src.VPCModel import VPCModel

# Fixtures
@pytest.fixture
def vpc_model_ode():
    return VPCModel("y' = -k * y", ["y"])

@pytest.fixture
def vpc_model_reg():
    return VPCModel("m * x + c", ["x"])

@pytest.fixture
def vpc_model_vec():
    return VPCModel("a*t, b+t", ["t"])

# Tests
def test_fit_ode(vpc_model_ode):
    data = [
        [0, 1, 2, 3, 4],  # t data
        [1, 0.7, 0.5, 0.35, 0.25]  # y data
    ]
    fit(vpc_model_ode, data)
    assert hasattr(vpc_model_ode, 'fitted_consts')
    assert vpc_model_ode.fitted_consts is not None

def test_fit_reg(vpc_model_reg):
    data = [
        [0, 1, 2, 3, 4],  # x data
        [1., 2., 3., 4., 5.]  # y data
    ]
    fit(vpc_model_reg, data)
    assert hasattr(vpc_model_reg, 'fitted_consts')
    assert vpc_model_reg.fitted_consts is not None

def test_check_model_is_valid_vector(vpc_model_reg, vpc_model_vec):
    invalid = check_model_is_valid_vector(vpc_model_reg, 2)
    valid = check_model_is_valid_vector(vpc_model_vec, 3)
    assert not invalid
    assert valid

def test_evaluate_fit():
    pcov = np.array([[0.1, 0], [0, 0.2]])
    eval_metrics = evaluate_fit(pcov)
    assert "variances" in eval_metrics
    assert "std_devs" in eval_metrics
    assert "confidence_intervals" in eval_metrics
    assert "mse" in eval_metrics
    assert "rmse" in eval_metrics
    assert eval_metrics["mse"] > 0