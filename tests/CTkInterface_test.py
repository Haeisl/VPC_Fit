import pytest
from unittest.mock import patch, MagicMock
from src.CTkInterface import MainApp
from src.VPCModel import VPCModel

@pytest.fixture
def main_app():
    return MainApp()

def test_reset_state(main_app):
    main_app.file_name.set("test_file.xlsx")
    main_app.file_path = "/path/to/test_file.xlsx"
    main_app.equation_entry.insert(0, "test equation")
    main_app.what_parameter_entry.insert(0, "t")
    main_app.result_components_combobox.set("auto")

    main_app.reset_state()

    assert main_app.file_name.get() == "Browse..."
    assert main_app.file_path == ""
    assert main_app.equation_entry.get() == ""
    assert main_app.what_parameter_entry.get() == ""
    assert main_app.result_components_combobox.get() == "1"

@patch('src.FileHandler.read_file')
def test_confirm_input_with_valid_input(mock_read_file, main_app):
    mock_read_file.return_value = MagicMock()
    main_app.file_path = "/path/to/test_file.xlsx"
    main_app.equation_entry.insert(0, "test equation")
    main_app.what_parameter_entry.insert(0, "t")
    main_app.result_components_combobox.set("auto")

    main_app.confirm_input()

    assert main_app.input_confirmation_textbox.get("1.0", "end") != ""

@patch('src.FileHandler.read_file', side_effect=Exception)
def test_confirm_input_with_invalid_file(mock_read_file, main_app):
    main_app.file_path = "/path/to/nonexistent_file.xlsx"
    main_app.equation_entry.insert(0, "test equation")
    main_app.what_parameter_entry.insert(0, "t")
    main_app.result_components_combobox.set("auto")

    main_app.confirm_input()

    assert "file doesn't exist" in main_app.input_confirmation_textbox.get("1.0", "end")

def test_missing_independent_variables(main_app):
    main_app.equation_entry.insert(0, "f(t) = t")
    main_app.what_parameter_entry.insert(0, "x,y,z")
    main_app.model = VPCModel(main_app.equation_entry.get(), main_app.what_parameter_entry.get())
    missing_vars = main_app.missing_independent_variables()
    assert missing_vars == ["x", "y", "z"]

def test_are_components_equal(main_app):
    main_app.result_components_combobox.set("2")
    main_app.model = VPCModel("f = at, bt", ["t"])
    assert main_app.are_components_equal() == True

def test_check_inputs_populated(main_app):
    main_app.equation_entry.insert(0, "test equation")
    main_app.what_parameter_entry.insert(0, "t")
    main_app.result_components_combobox.set("auto")
    main_app.file_path = ""

    error_msg = main_app.check_inputs_populated()
    assert "No file path given" in error_msg

def test_check_inputs_sensible(main_app):
    main_app.equation_entry.insert(0, "f(t) = k * t")
    main_app.what_parameter_entry.insert(0, "t,x")
    main_app.result_components_combobox.set("auto")
    main_app.model = MagicMock()
    main_app.model.constants = ["k"]

    error_msg = main_app.check_inputs_sensible()
    assert "parameters were not found" in error_msg

def test_create_interpretation_string(main_app):
    interpretation = main_app.create_interpretation_string("f(t) = k * t", ["t"], ["k"])
    assert "Function:\n    f(t) = k * t" in interpretation

def test_display_interpreted_input(main_app):
    msg = "Test Message"
    main_app.display_interpreted_input(msg)
    assert msg in main_app.input_confirmation_textbox.get("1.0", "end")

def test_browse_files(main_app):
    with patch('tkinter.filedialog.askopenfile') as mock_askopenfile:
        mock_file = MagicMock()
        mock_file.name = "/path/to/test_file.xlsx"
        mock_askopenfile.return_value = mock_file

        main_app.browse_files()

        fn = "test_file.xlsx"
        assert main_app.file_name.get() == (fn[:12] + "..") if len(fn) > 12 else fn
        assert main_app.file_path == "/path/to/test_file.xlsx"