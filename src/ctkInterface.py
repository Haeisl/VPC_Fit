# standard library imports
import inspect
import logging
import re
from pathlib import Path
from tkinter import filedialog, Widget
from typing import  Optional, Union

# related third party imports
import customtkinter
from sympy import FunctionClass
from tktooltip import ToolTip

# local imports
from src import FileHandler
from src import ModelFitter
from src.CTkResultInterface import ResultInterface
from src.FileHandler import FileExtensions
from src.VPCModel import VPCModel


logger = logging.getLogger("Interface")


customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")


class MainApp(customtkinter.CTk):
    """This is a class to handle the functionality and setup of the interface

    :param customtkinter: tkinter extension to create modern looking user interfaces
    :type customtkinter: CustomTkinter module
    """
    def __init__(self) -> None:
        """Constructor method to set up the main application"""
        super().__init__()

        # window configuration
        self.title("Virtual Patient Cohorts - Fitting App")
        window_width: int  = 500
        window_height: int  = 280
        screen_width: int  = self.winfo_screenwidth()
        screen_height: int  = self.winfo_screenheight()
        center_x: int  = int(screen_width/2 - window_width/2)
        center_y: int  = int(screen_height/2 - window_height/2)

        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.resizable(width=False, height=False)

        # font that is used
        font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
        button_font = customtkinter.CTkFont(family="Arial", size=14)

        # variables that change through user interaction
        self.file_name = customtkinter.StringVar(self, "Browse...")
        self.file_path: str = ""

        # main frame tabview
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=0, padx=(5,2), pady=(5,5), sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.tabview = customtkinter.CTkTabview(self.main_frame, width=200, height=100)
        self.tabview.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.tabview.add("Basic")
        self.tabview.add("Additional")
        self.tabview._segmented_button.configure(font=button_font)
        self.tabview.tab("Basic").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Basic").grid_columnconfigure(1, weight=1)
        self.tabview.tab("Additional").grid_columnconfigure(0, weight=1)

        # tabview "Basic"
        self.equation_label = customtkinter.CTkLabel(
            self.tabview.tab("Basic"),
            text="Model:",
            font=font,
            compound="left"
        )
        self.equation_label.grid(
            row=0, column=0,
            padx=(20,5), pady=(5,0),
            sticky="ew",
            columnspan=2
        )
        self.equation_entry = customtkinter.CTkEntry(
            self.tabview.tab("Basic"),
            placeholder_text="f(t) = ...",
            font=font,
            width=178,
            justify=customtkinter.CENTER
        )
        self.equation_entry.grid(
            row=1, column=0,
            padx=10, pady=(0,5),
            sticky="ew",
            columnspan=2
        )
        self.data_input_label = customtkinter.CTkLabel(
            self.tabview.tab("Basic"),
            text="Data:",
            font=font,
            compound="left"
        )
        self.data_input_label.grid(
            row=2, column=0,
            padx=(20,5), pady=(5,35),
            sticky="w"
        )
        self.data_input_button = customtkinter.CTkButton(
            self.tabview.tab("Basic"),
            textvariable=self.file_name,
            font=button_font,
            width=80,
            command=self.browse_files
        )
        self.data_input_button.grid(
            row=2, column=1,
            padx=(0,20), pady=(5,35),
            sticky="w"
        )

        # tabview "Additional"
        self.what_parameter_label = customtkinter.CTkLabel(
            self.tabview.tab("Additional"),
            text="Independent Parameters:",
            font=font
        )
        self.what_parameter_label.grid(
            row=0, column=0,
            padx=10, pady=(2,0),
            columnspan=2
        )
        self.what_parameter_entry = customtkinter.CTkEntry(
            self.tabview.tab("Additional"),
            placeholder_text="t",
            font=font,
            width=80
        )
        self.what_parameter_entry.grid(
            row=1, column=0,
            padx=10, pady=(0,10),
            columnspan=2
        )
        self.result_components_label = customtkinter.CTkLabel(
            self.tabview.tab("Additional"),
            text="Result Components:",
            font=font
        )
        self.result_components_label.grid(
            row=2, column=0,
            padx=10,
            pady=(0,0),
            columnspan=2
        )
        self.result_components_combobox = customtkinter.CTkComboBox(
            self.tabview.tab("Additional"),
            values=["auto", "1", "2", "3"],
            #variable=self.result_components,
            font=font,
            width=80
        )
        self.result_components_combobox.grid(
            row=3, column=0,
            padx=10, pady=(0,10),
            columnspan=2
        )

        # Confirm button at the bottom of the left frame
        self.confirm_inputs_button = customtkinter.CTkButton(
            self.main_frame,
            text="Confirm",
            font=button_font,
            command=self.confirm_input
        )
        self.confirm_inputs_button.grid(
            row=3, column=0,
            pady=(20,25)
        )

        # compute frame
        self.compute_frame = customtkinter.CTkFrame(self, height=300, corner_radius=0)
        self.compute_frame.grid(row=0, column=1, rowspan=2, padx=(3,5), pady=(5,5), sticky="nsew")
        self.compute_frame.grid_columnconfigure(0, weight=1)
        self.compute_frame.grid_rowconfigure((2), weight=1)
        self.input_confirmation_label = customtkinter.CTkLabel(
            self.compute_frame,
            text="Interpreted Input:",
            font=font
        )
        self.input_confirmation_label.grid(
            row=0, column=0,
            padx=10, pady=(10,0)
        )
        self.input_confirmation_textbox = customtkinter.CTkTextbox(
            self.compute_frame,
            height=141,
            font=font
        )
        self.input_confirmation_textbox.grid(
            row=1, column=0,
            padx=10, pady=(10,0),
            sticky="nsew"
        )
        self.compute_params_button = customtkinter.CTkButton(
            self.compute_frame,
            text="Compute Parameters",
            font=button_font,
            command=self.compute_params
        )
        self.compute_params_button.grid(
            row=3, column=0,
            pady=(20,25)
        )

        # set default values
        msg = self.create_interpretation_string()
        self.input_confirmation_textbox.insert("1.0", msg)
        self.compute_params_button.configure(state="disabled")

        # set tooltip for compute button
        self.compute_button_tooltip = self.create_tooltip_for(
            widget=self.compute_params_button,
            msg="You need to confirm your inputs before computation."
        )

        # set tooltip for model equation entry
        self.model_entry_tooltip = self.create_tooltip_for(
            widget=self.equation_entry,
            msg="Explicitly state mathematical operations."
        )

    def create_tooltip_for(self, widget: Widget, msg: str) -> ToolTip:
        return ToolTip(
            widget=widget,
            msg=msg,
            delay=0,
            parent_kwargs={"bg": "gray14", "padx": 2, "pady": 2},
            fg="#ffffff", bg="gray17", padx=3, pady=3
        )

    def reset_state(self) -> None:
        self.file_name.set("Browse...")
        self.file_path = ""
        self.equation_entry.delete(0, customtkinter.END)
        self.what_parameter_entry.delete(0, customtkinter.END)
        self.result_components_combobox.set("1")

        self.input_confirmation_textbox.delete("1.0", customtkinter.END)
        msg = self.create_interpretation_string()
        self.input_confirmation_textbox.insert("1.0", msg)

        self.compute_params_button.configure(state="disabled")

        self.compute_button_tooltip = self.create_tooltip_for(
            widget=self.compute_params_button,
            msg="You need to confirm your inputs before computation.",
        )

        attribute_names: list[str] = [
            "_model", "_data", "_independent_vars",
            "_result_comps", "_parameters_to_fit", "_file_path"
        ]
        for attr_name in attribute_names:
            if hasattr(self, attr_name):
                delattr(self, attr_name)
            else:
                raise AttributeError(f"tried to find Attribute {attr_name}, but nothing was found")

        logger.info("Successfully reset to initial state.")
        # print("Successfully reset to initial state.")

    def remove_compute_tooltip(self) -> None:
        """removes the tooltip and enables the "compute parameters" button
        """
        if self.compute_button_tooltip.winfo_exists():
            # unbinding compute button bindings
            self.compute_params_button.unbind("<Enter>")
            self.compute_params_button.unbind("<Leave>")
            self.compute_params_button.unbind("<Motion>")
            self.compute_params_button.unbind("<ButtonPress>")
            # destroying the tooltip
            self.compute_button_tooltip.destroy()
            # enabling the button
            self.compute_params_button.configure(state="normal")

    def create_interpretation_string(
        self,
        function: str = "...",
        var: list[str] = ["..."],
        consts: list[str] = ["..."],
        **kwargs: Optional[str]
    ) -> str:
        """creates the interpretation string of the user input

        :param function: interpreted function, defaults to "..."
        :type function: str, optional
        :param var: interpreted independent variable(s), defaults to "..."
        :type var: str, optional
        :param consts: interpreted parameters to fit, defaults to "..."
        :type consts: str, optional
        :return: all together, interpreted input
        :rtype: str
        """
        msg = f"Function:\n" +\
            f"    {function}\n" +\
            f"Independent Variable(s):\n" +\
            f"    {", ".join(str(c) for c in var)}\n"+\
            f"Constants to be fitted:\n"+\
            f"    {", ".join(str(c) for c in consts)}"
        if kwargs:
            msg += f"\n\nExtra:"
            for descr, val in kwargs.items():
                msg += f"\n{descr}:\n    {val}\n"
        return msg

    def display_interpreted_input(self, msg: str) -> None:
        """shows the interpretation of the user input

        :param msg: interpretation of the user input
        :type msg: str
        """
        # clear text Widget
        self.input_confirmation_textbox.delete("1.0", customtkinter.END)
        # add new text to widget
        self.input_confirmation_textbox.insert("1.0", msg)

    def browse_files(self) -> None:
        """opens a filedialog to let the user select a data file
        sets the filepath and filename when selected
        """
        logger.info("Browse files button pressed")
        filetypes = [("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All", "*.*")]
        logger.debug(f"Starting filedialog")
        fp = filedialog.askopenfile(filetypes=filetypes)
        logger.debug(
            f"Completed filedialog with:\n"+
            f"  {fp}"
        )

        if fp is None:
            return

        fn = fp.name.split("/")[-1]
        displayed_name = (fn[:12] + "..") if len(fn) > 12 else fn
        self.file_name.set(displayed_name)
        self.file_path = fp.name

    def missing_independent_variables(self) -> list:
        """returns list of all variables that were entered (t if nothing entered)
        that are not present in model

        :return: list of symbols
        :rtype: list
        """
        indep_vars = re.split(r",\s|,|;\s|;", self.what_parameter_entry.get())
        # default to t if nothing was explicitly entered
        indep_vars = ["t"] if indep_vars == [""] else indep_vars

        variables = self.model.symbols

        missing_vars = []
        for var in indep_vars:
            if var not in variables:
                missing_vars.append(var)

        return missing_vars

    def are_components_equal(self) -> bool:
        if self.result_components_combobox.get() == "auto":
            return True
        given = int(self.result_components_combobox.get())
        assumed = self.model.expression_string.count(",") + 1
        return given == assumed

    def check_input_validity(self) -> str:
        """checks the user input for errors

        :return: message with errors, if found
        :rtype: str
        """
        msg = ""
        if self.equation_entry.get() == "":
            msg += (
                f"No model equation entered.\n\n"
            )
        missing_vars = self.missing_independent_variables()
        if missing_vars:
            if len(missing_vars) == 1:
                msg += (
                    f"The following independent\nparameter was not found in\n"
                    f"the model expression:\n{missing_vars}\n\n"
                )
            else:
                msg += (
                    f"The following independent\nparameters were not found in\n"
                    f"the model expression:\n{missing_vars}\n\n"
                )
        valid = {str(i) for i in range(10)}
        valid.add("auto")
        if self.result_components_combobox.get() not in valid:
            msg += (
                f"Result Components\n"
                f"have to be \"auto\" or 1-9\n\n"
            )
        elif not self.are_components_equal():
            msg += (
                f"Entered model suggests\n"
                f"different # of components\n"
                f"than # provided in\n"
                f"\"additional\" tab.\n\n"
            )
        if not Path(self.file_path).exists():
            msg += (
                f"No file path given\n"
                f"or path doesn\"t exist.\n\n"
            )
        if (self.file_path != "") and (not FileHandler.is_extension_supported(self.file_path)):
            msg += (
                f"Unsupported file extension.\n"
                f"Use .xlsx or .csv\n\n"
            )
        return msg

    def confirm_input(self) -> None:
        """displays the user"s input and removes tooltip
        or displays errors in the input, if any are found
        """
        logger.info("Confirm button pressed")
        ip = self.what_parameter_entry.get().replace(" ", "").split(",")
        indep_param = ["t"] if ip == [""] else ip

        self.model = VPCModel(self.equation_entry.get(), indep_param)

        error_msg = self.check_input_validity()
        if error_msg:
            self.display_interpreted_input(error_msg)
            return

        if not self.model.constants:
            self.display_interpreted_input(
                f"No constants to fit"
            )
            return

        combobox_entry = self.result_components_combobox.get()
        auto_value = self.model.expression_string.count(",") + 1
        res_comps = auto_value if combobox_entry == "auto" else int(combobox_entry)

        msg = self.create_interpretation_string(
            self.model.model_string,
            self.model.independent_var,
            self.model.constants
        )

        self.display_interpreted_input(msg)

        self.remove_compute_tooltip()

        data = FileHandler.read_file(self.file_path)
        data_list = FileHandler.dataframe_tolist(data)

        logger.debug(
            f"Dynamic lambda {self.model.model_function} with:\n"
            f"  {inspect.getsource(self.model.model_function).strip()}"
        )

        # set internal vars to validated inputs
        self._model: VPCModel = self.model
        self._data: list[list[Union[int, float]]] = data_list
        self._lambda_func: FunctionClass = self.model.model_function
        self._independent_vars: list[str] = indep_param
        self._result_comps: int = res_comps
        self._parameters_to_fit: list[str] = self.model.constants
        self._file_path: str = self.file_path

        logger.debug(
            f"Internal variables:\n"
            f"  Model: {self._model}\n"
            f"  Data: {self._data}\n"
            f"  Lambda: {self._lambda_func}\n"
            f"  Independent vars: {self._independent_vars}\n"
            f"  Result components: {self._result_comps}\n"
            f"  Constants: {self._parameters_to_fit}\n"
            f"  File path: {self._file_path}"
        )

    def compute_params(self) -> None:
        """starts the calculation process of the parameters to be fitted
        """
        logger.info("Compute parameters button pressed")

        ModelFitter.fit(self._model, self._data)

        result_window = ResultInterface(self)
        result_window.attributes("-topmost", True)

    def save_results(self) -> int:
        data = FileHandler.create_dataframe_from_for(
            fitted_model = self._model.resulting_function,
            model = self._model.model_string,
            user_input_model = self.equation_entry.get(),
            parameter = self._independent_vars,
            user_input_parameter = self.what_parameter_entry.get(),
            consts = self._parameters_to_fit,
            user_input_consts = self._model.constants,
            user_input_path = self.file_path,
            format = FileExtensions.EXCEL
        )
        try:
            logger.debug(
                f"Attempting to write results file with:\n"
                f"{data.to_string()}"
            )
            FileHandler.write_file(data, file_format=FileExtensions.EXCEL)
            return 0
        except TypeError as e:
            logger.error(f"Error writing file {e}", exc_info=True)
            return 1