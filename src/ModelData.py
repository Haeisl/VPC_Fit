from dataclasses import dataclass, field

@dataclass
class ModelData:
    fitted_model: str | None = None
    fitted_consts: dict[str, float] | str | None = None
    model: str = "f(t) = ..."
    user_input_model: str = "f(t) = ..."
    parameter: list[str] = field(default_factory=lambda: ["..."])
    user_input_parameter: str = "..."
    consts: list[str] = field(default_factory=lambda: ["..."])
    user_input_consts: list[str] = field(default_factory=lambda: ["..."])
    user_input_path: str = "path/to/data"