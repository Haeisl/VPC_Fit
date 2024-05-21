import pytest
import numpy as np
from unittest.mock import MagicMock
from scipy.optimize import OptimizeResult

from src.VPCModel import VPCModel
import src.ModelFitter as mf

@pytest.fixture
def mock_vpcmodel():
    mock_model = MagicMock(spec=VPCModel)
    mock_model.independent_var = [0, 1]
    mock_model.constants = ['a', 'b']
    mock_model.model_function = MagicMock(return_value=lambda t, a, b: a * np.exp(b * t))
    mock_model.is_ode.return_value = True
    mock_model.is_vector.return_value = False
    return mock_model

@pytest.fixture
def mock_vpcmodel_reg():
    mock_model = MagicMock(spec=VPCModel)
    mock_model.independent_var = [0]
    mock_model.constants = ['a', 'b']
    mock_model.model_function = MagicMock(return_value=lambda t, a, b: a * t + b)
    mock_model.is_ode.return_value = False
    mock_model.is_vector.return_value = False
    return mock_model

def test_fit_ode(mock_vpcmodel):
    data = [[0, 1, 2, 3], [1, 2.7, 7.3, 20.1]]
    mf.fit(mock_vpcmodel, data)
    mock_vpcmodel.set_fit_information.assert_called_once()

def test_fit_reg(mock_vpcmodel_reg):
    data = [[0, 1, 2, 3], [1, 3, 5, 7]]
    mf.fit(mock_vpcmodel_reg, data)
    mock_vpcmodel_reg.set_fit_information.assert_called_once()

def test_fit_raises_runtimeerror_with_invalid_model(mock_vpcmodel):
    mock_vpcmodel.is_ode.side_effect = RuntimeError("Model error")
    data = [[0, 1, 2, 3], [1, 2.7, 7.3, 20.1]]
    with pytest.raises(RuntimeError, match="Model error"):
        mf.fit(mock_vpcmodel, data)

def test_check_model_is_valid_vector_raises_runtimeerror(mock_vpcmodel):
    mock_vpcmodel.independent_var = [0]
    mock_vpcmodel.components = 2
    with pytest.raises(RuntimeError, match="Each model component needs its own data column."):
        mf.check_model_is_valid_vector(mock_vpcmodel, 2)

def test_evaluate_fit():
    pcov = np.array([[1, 0.1], [0.1, 1]])
    metrics = mf.evaluate_fit(pcov)
    assert "variances" in metrics
    assert "std_devs" in metrics
    assert "confidence_intervals" in metrics
    assert "mse" in metrics
    assert "rmse" in metrics

def test_evaluate_fit_raises_valueerror():
    with pytest.raises(ValueError, match="Covariance matrix 'pcov' cannot be None."):
        mf.evaluate_fit(None)

def test_fit_ode_with_minimize_failure(mock_vpcmodel):
    def side_effect(*args, **kwargs):
        raise RuntimeError("Minimize function error")
    mock_vpcmodel.model_function.side_effect = side_effect
    data = [[0, 1, 2, 3], [1, 2.7, 7.3, 20.1]]
    with pytest.raises(RuntimeError, match="Error in minimize function."):
        mf.fit(mock_vpcmodel, data)

def test_fit_reg_with_curve_fit_failure(mock_vpcmodel_reg):
    def side_effect(*args, **kwargs):
        raise ValueError("Curve fit error")
    mf.curve_fit = MagicMock(side_effect=side_effect)
    data = [[0, 1, 2, 3], [1, 3, 5, 7]]
    with pytest.raises(RuntimeError, match="Value error in curve_fit."):
        mf.fit(mock_vpcmodel_reg, data)
