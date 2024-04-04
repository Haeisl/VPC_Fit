# standard library imports
import inspect
import logging
import re
from pathlib import Path
from tkinter import filedialog, Widget

# related third party imports
import customtkinter
from sympy import FunctionClass
from tktooltip import ToolTip

# local imports
from src import FileHandler
from src import ModelFitter
from src.CTkResultInterface import ResultInterface, FailedFitInterface
from src.FileHandler import FileExtensions
from src.ModelData import ModelData
from src.VPCModel import VPCModel


logger = logging.getLogger("Interface")


customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")


class MainApp(customtkinter.CTk):
    """Main interface of the program. Providing ways for the user to input information
    that gets checked for to finally be able to fit a model to data.

    Uses a ``tkinter`` extension called ``customtkinter`` to achieve a modern look.
    """
    def __init__(self) -> None:
        """Setup of the main interface window seen after starting the program,
        arranging widgets and setting default values.
        """
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
        button_font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")

        # variables that change through user interaction
        self.file_name = customtkinter.StringVar(self, "Browse...")
        self.file_path: str = ""

        # main frame tabview
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=0, padx=(5,2), pady=(5,5), sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.tabview = customtkinter.CTkTabview(
            self.main_frame, width=200, height=100, text_color="white"
        )
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
            command=self.browse_files,
            text_color="white"
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
        self.confirm_inputs_button = customtkinter.CTkButton(
            self.main_frame,
            text="Confirm",
            font=button_font,
            command=self.confirm_input,
            text_color="white"
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
            command=self.compute_params,
            text_color="white"
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

        self.what_parameter_entry_tooltip = self.create_tooltip_for(
            widget=self.what_parameter_entry,
            msg="Order needs to match order of independent variable columns in provided data."
        )

    def create_tooltip_for(self, widget: Widget, msg: str) -> ToolTip:
        """Helper Function to create a ``ToolTip`` for and attach it to a ``tkinter.Widget``.

        :param widget: The ``tkinter.Widget`` the ``ToolTip`` is binded to.
        :type widget: Widget
        :param msg: What the ``ToolTip`` should say.
        :type msg: str
        :return: A new ``ToolTip`` instance.
        :rtype: ToolTip
        """
        return ToolTip(
            widget=widget,
            msg=msg,
            delay=1.0,
            parent_kwargs={"bg": "gray14", "padx": 2, "pady": 2},
            fg="#ffffff", bg="gray17", padx=3, pady=3,
            width=300
        )

    def reset_state(self) -> None:
        """Resets the program to an initial state without closing and reopening it.

        :raises AttributeError: if one of the internal attributes that should have been set are\
        not found and therefore couldn't be reset.
        """
        self.file_name.set("Browse...")
        self.file_path = ""
        self.equation_entry.delete(0, customtkinter.END)
        self.what_parameter_entry.delete(0, customtkinter.END)
        # self.ode_initial_value_entry.delete(0, customtkinter.END)

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
                logger.warning(f"tried to find Attribute {attr_name}, but nothing was found")
                continue

        logger.info("Successfully reset to initial state.")

    def remove_compute_tooltip(self) -> None:
        """Removes the tooltip and enables the 'compute parameters' button."""
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
        model: VPCModel | None = None,
        **kwargs: str | None
    ) -> str:
        """Creates the interpretation string of the user input.

        :param model: Model to be iterpreted, defaults to None.
        :type model: VPCModel, optional
        :param kwargs: Additional keyword arguments, defaults to None.
        :type kwargs: str | None
        :return: A multi-line f-string containing the entered information.
        :rtype: str
        """
        if model is None:
            function = "..."
            var = ["..."]
            consts = ["..."]
            ode_msg = "..."
            vector_msg = "..."
        else:
            function = model.model_string
            var = model.independent_var
            consts = model.constants
            ode_msg = "Yes" if model.is_ode() else "No"
            vector_msg = f"Yes, {model.components} components" if model.is_vector() else "No"
        msg = (
            f"Function:\n"
            f"    {function}\n"
            f"Independent Variable(s):\n"
            f"    {", ".join(str(c) for c in var)}\n"
            f"Constants to be fitted:\n"
            f"    {", ".join(str(c) for c in consts)}\n\n"
            f"ODE:\n"
            f"    {ode_msg}\n"
            f"Vector:\n"
            f"    {vector_msg}"
        )
        if kwargs:
            msg += f"\n\nExtra:"
            for descr, val in kwargs.items():
                msg += f"\n{descr}:\n    {val}\n"
        return msg

    def display_interpreted_input(self, msg: str) -> None:
        """Shows the interpretation of the user input.

        :param msg: interpretation of the user input
        :type msg: str
        """
        # clear text Widget
        self.input_confirmation_textbox.delete("1.0", customtkinter.END)
        # add new text to widget
        self.input_confirmation_textbox.insert("1.0", msg)

    def browse_files(self) -> None:
        """Opens a ``tkinter.filedialog`` to let the user select a file containing fitting data.
        Sets internal variables to the file path and name when a file is successfully selected.
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
        displayed_name = (fn[:11] + "..") if len(fn) > 11 else fn
        self.file_name.set(displayed_name)
        self.file_path = fp.name

    def missing_independent_variables(self) -> list:
        """Returns list of all characters or strings that were entered in the independent
        parameter field that are not present in the model string.
        If the field was left empty 't' is defaulted to.

        :return: List of missing symbols.
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

    def check_inputs_populated(self) -> str:
        """Checks the various fields for missing user input.

        :return: Message with missing or invalid entried, empty if okay.
        :rtype: str
        """
        msg = ""
        if self.equation_entry.get() == "":
            msg += (
                f"No model equation entered.\n\n"
            )
        if (not Path(self.file_path).exists()) or self.file_path == "":
            msg += (
                f"No file path given\n"
                f"or file doesn't exist.\n\n"
            )
        return msg

    def check_inputs_sensible(self) -> str:
        """Checks whether the user input 'makes sense', e.g. if there are unfitted constants in the
        model expression.

        :return: Message with apparent issues in the user's input.
        :rtype: str
        """
        msg = ""
        if not self.model.constants:
            msg += (
                f"No constants to fit."
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
        if (self.file_path != "") and (not FileHandler.is_extension_supported(self.file_path)):
            msg += (
                f"Unsupported file extension.\n"
                f"Use .xlsx or .csv files\n\n"
            )
        return msg

    def confirm_input(self) -> None:
        """Checks inputs and displays any issues. If okay, sets internal variables."""
        logger.info("Confirm button pressed")
        error_msg = ""
        error_msg += self.check_inputs_populated()
        if error_msg:
            self.display_interpreted_input(error_msg)
            return

        ip = self.what_parameter_entry.get().replace(" ", "").split(",")
        indep_param = ["t"] if ip == [""] else ip
        self.model = VPCModel(self.equation_entry.get(), indep_param)

        error_msg += self.check_inputs_sensible()

        try:
            data = FileHandler.read_file(self.file_path)
            data_list = FileHandler.dataframe_tolist(data)
        except Exception as e:
            logger.error(
                f"Error occurred when reading file, see:"
                f"  {e}"
            )
            error_msg += (
                f"Error reading input file.\n"
                f"See logs for more info."
            )
            return

        if error_msg:
            self.display_interpreted_input(error_msg)
            return

        msg = self.create_interpretation_string(self.model)

        self.display_interpreted_input(msg)
        self.remove_compute_tooltip()

        logger.debug(
            f"Dynamic lambda {self.model.model_function} with:\n"
            f"  {inspect.getsource(self.model.model_function).strip()}"
        )
        # set internal vars to validated inputs
        self._model: VPCModel = self.model
        self._data: list[list[int | float]] = data_list
        self._lambda_func: FunctionClass = self.model.model_function
        self._independent_vars: list[str] = indep_param
        self._result_comps: int = self.model.components
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
        """Runs `ModelFitter.fit()` on the model and data, opens a window with the results."""
        logger.info("Compute parameters button pressed")

        try:
            ModelFitter.fit(self._model, self._data)
        except RuntimeError as re:
            logger.error(f"Error occurred in fitting the model. See {re}")
            failed_interface = FailedFitInterface(main_window=self)
            failed_interface.focus_set()
            return

        fitted = VPCModel(self._model.resulting_function, self._independent_vars)

        result_window = ResultInterface(
            main_window=self,
            model=self._model,
            fitted_model=fitted,
            data=self._data
        )
        result_window.focus_set()

    def save_results(self) -> int:
        """Saves relevant inputs and outputs of the program in a file.

        :return: 0 if ``FileHandler.write_file()`` finished normally, 1 otherwise.
        :rtype: int
        """
        model_data = ModelData(
            fitted_model=self._model.resulting_function,
            fitted_consts=self._model.fitted_consts,
            model=self._model.model_string,
            user_input_model=self.equation_entry.get(),
            parameter=self._independent_vars,
            user_input_parameter=self.what_parameter_entry.get(),
            consts=self._parameters_to_fit,
            user_input_consts=self._model.constants,
            user_input_path=self.file_path,
        )
        format = FileExtensions.EXCEL
        data = model_data.create_dataframe_for(format=format)
        try:
            logger.debug(
                f"Attempting to write results file with:\n"
                f"{data.to_string()}"
            )
            FileHandler.write_file(data, file_format=format)
            return 0
        except TypeError as e:
            logger.error(f"Error writing file, {e}", exc_info=True)
            return 1