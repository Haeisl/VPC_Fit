import pytest
from src.VPCModel import VPCModel

@pytest.fixture
def quad_model_unclean() -> VPCModel:
    return VPCModel("  f(t) = a*t^2 + b*t + c      ", ["t"])

@pytest.fixture
def quad_model_clean() -> VPCModel:
    return VPCModel("f(t) = a*t**2 + b*t + c", ["t"])


def test_model_string_getter(quad_model_unclean: VPCModel, quad_model_clean: VPCModel) -> None:
    assert quad_model_unclean.model_string == "f(t) = a*t**2 + b*t + c"
    assert quad_model_clean.model_string == "f(t) = a*t**2 + b*t + c"