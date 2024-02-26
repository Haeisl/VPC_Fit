from src.VPCModel import VPCModel

def test_model() -> None:
    model = VPCModel("f(x) = x + 1", ["x"])
    assert model.model_string == "f(x) = x + 1"