import tkinter
from tkinter import filedialog
from typing import Optional, Tuple, Union
from .FileHandler import FileHandler
from .VPCData import VPCData
from .ModelFitter import ModelFitter
from . import Validator
import customtkinter
from tktooltip import ToolTip
import re
from typing import Tuple

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")

class MainApp(customtkinter.CTk):
    """This is a class to handle the functionality and setup of the interface

    :param customtkinter: tkinter extension to create modern looking user interfaces
    :type customtkinter: CustomTkinter module
    """
    def __init__(self):
        """Constructor method to set up the main application
        """
        super().__init__()

        # window configuration
        self.title("Virtual Patient Cohorts - Fitting App")
        self.geometry(f"{500}x{280}+{1000}+{600}")

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
        self.file_path = ''

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
            values=[str(i) for i in range(1,4)],
            #variable=self.result_components,
            font=font,
            width=80)
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
        self.compute_button_tooltip = ToolTip(
            widget=self.compute_params_button,
            msg="You need to confirm your inputs before computation.",
            delay=0,
            parent_kwargs={"bg": "gray14", "padx": 2, "pady": 2},
            fg="#ffffff", bg="gray17", padx=3, pady=3)

        # set tooltip for model equation entry
        # "LHS will not be regarded and can be omitted.\n"
        # "Set independent variables in 'Additional' tab."
        self.model_entry_tooltip = ToolTip(
            widget=self.equation_entry,
            msg=("Explicitly state mathematical operations."),
            delay=0,
            parent_kwargs={"bg": "gray14", "padx": 2, "pady": 2},
            fg="#ffffff", bg="gray17", padx=3, pady=3)


    def remove_compute_tooltip(self) -> None:
        """removes the tooltip and enables the 'compute parameters' button
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
        function: Optional[str] = "...",
        var: Optional[str] = "...",
        consts: Optional[list[str]] = ["..."],
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

        msg = f"Function:\n\t{function}\nIndependent Variable(s):\n" +\
                f"\t{var}\nConstants to be fitted:\n\t{", ".join(str(c) for c in consts)}"
        if kwargs:
            msg += f"\n\nExtra:"
            for descr, val in kwargs.items():
                msg += f"\n{descr}:\n\t{val}\n"
        return msg


    def display_interpreted_input(self, msg) -> None:
        """shows the interpretation of the user input

        :param msg: interpretation of the user input
        :type msg: str
        """
        # clear text Widget
        self.input_confirmation_textbox.delete("1.0", tkinter.END)
        # add new text to widget
        self.input_confirmation_textbox.insert("1.0", msg)


    def browse_files(self) -> None:
        """opens a filedialog to let the user select a data file
        sets the filepath and filename when selected
        """
        fp = filedialog.askopenfile()
        if fp is None:
            return
        fn = fp.name.split('/')[-1]
        displayed_name = (fn[:12] + '..') if len(fn) > 12 else fn
        self.file_name.set(displayed_name)
        self.file_path = fp.name


    def check_input_validity(self) -> str:
        """checks the user input for errors

        :return: message with errors, if found
        :rtype: str
        """
        msg = ''
        unfound_vars = Validator.are_variables_consistent(
            entered_model=self.equation_entry.get(),
            entered_indep_var=self.what_parameter_entry.get()
        )
        if unfound_vars:
            if len(unfound_vars) == 1:
                msg += (f'The following independent\nparameter was not found in\n'
                        f'the model expression:\n{unfound_vars}\n\n')
            else:
                msg += (f'The following independent\nparameters were not found in\n'
                        f'the model expression:\n{unfound_vars}\n\n')

        if not Validator.are_components_equal(
            given_comps=int(self.result_components_combobox.get()),
            expression=self.equation_entry.get()
        ):
            msg += (
                f'Entered model suggests\n'
                f'different # of components\n'
                f'than # provided in\n'
                f'\'additional\' tab\n\n'
            )

        if not Validator.does_file_path_exist(self.file_path):
            msg += (
                f'No file path given\n'
                f'Or path doesn\'t exist\n\n'
            )

        return msg


    def confirm_input(self) -> None:
        """displays the user's input and removes tooltip
        or displays errors in the input, if any are found
        """
        error_msg = self.check_input_validity()
        if error_msg:
            self.display_interpreted_input(error_msg)
            return

        expression = self.equation_entry.get()
        ip = self.what_parameter_entry.get()
        indep_param = 't' if ip == '' else ip
        all_vars = Validator.extract_variables(expression)
        constants = [c for c in all_vars if c not in indep_param]
        res_comps = int(self.result_components_combobox.get())

        msg = self.create_interpretation_string(
            expression,
            indep_param,
            constants
        )
        self.display_interpreted_input(msg)
        self.remove_compute_tooltip()

        # set internal vars to validated inputs
        self._expression = expression
        self._data = None # TODO
        self._independent_vars = indep_param
        self._result_comps = res_comps
        self._parameters_to_fit = constants
        self._file_path = self.file_path


    def compute_params(self) -> None:
        """starts the calculation process of the parameters to be fitted
        """
        self._expression
        self._data
        self._independent_vars
        self._result_comps
        self._parameters_to_fit
        self._file_path

        # FH = FileHandler.Read_Mode(self.file_path)
        # df = FH.read_file()
        # data = []
        # for name in df.columns.values:
        #     data.append(df[name].to_numpy())

        # MF = ModelFitter()
        # expression = self.equation_entry.get()

        # if not len(self.what_parameter_entry.get()) == 0:
        #     independent_param = [self.what_parameter_entry.get()]

        # fitted_params, variable_names = MF.fit(expression, data, independent_param)