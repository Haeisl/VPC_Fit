import tkinter
from tkinter import filedialog
from typing import Optional, Tuple, Union
from .FileHandler import FileHandler
from .VPCData import VPCData
from .ModelFitter import ModelFitter
import customtkinter
from tktooltip import ToolTip

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")

class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # window configuration
        self.title("Virtual Patient Cohorts - Fitting App")
        self.geometry(f"{500}x{250}+{1000}+{600}")

        # grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        # self.resizable(width=False, height=False)

        # font that is used
        font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
        button_font = customtkinter.CTkFont(family="Arial", size=14)

        # variables that change through user interaction
        self.file_name = customtkinter.StringVar(self, "Browse...")

        # main frame tabview
        self.tabview = customtkinter.CTkTabview(self, width=100, height=300, corner_radius=0)
        self.tabview.grid(row=0, column=0, padx=(5,2), pady=(5,0), sticky="nsew")
        self.tabview.add("Basic")
        self.tabview.add("Additional")
        self.tabview._segmented_button.configure(font=button_font)
        self.tabview.tab("Basic").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Basic").grid_columnconfigure(1, weight=1)
        self.tabview.tab("Additional").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Additional").grid_columnconfigure(1, weight=1)
        self.tabview.tab("Basic").grid_rowconfigure(2, weight=1)
        self.tabview.tab("Additional").grid_rowconfigure(2, weight=1)
        # self.tabview.tab("Basic").grid_propagate(False)

        # tabview "Basic"
        self.equation_label = customtkinter.CTkLabel(self.tabview.tab("Basic"),
                                                     text="Model:",
                                                     font=font,
                                                     compound="left")
        self.equation_label.grid(row=0, column=0, padx=(20,5), pady=(10,5), sticky="w")
        self.equation_entry = customtkinter.CTkEntry(self.tabview.tab("Basic"),
                                                     placeholder_text="f(t) = ...",
                                                     font=font,
                                                     width=118)
        self.equation_entry.grid(row=0, column=1, padx=(0,20), pady=(10,5), sticky="ew")
        self.data_input_label = customtkinter.CTkLabel(self.tabview.tab("Basic"),
                                                       text="Data:",
                                                       font=font,
                                                       compound="left")
        self.data_input_label.grid(row=1, column=0, padx=(20,5), pady=(5,10), sticky="w")
        self.data_input_button = customtkinter.CTkButton(self.tabview.tab("Basic"),
                                                         textvariable=self.file_name,
                                                         font=button_font,
                                                         width=80)
        self.data_input_button.grid(row=1, column=1, padx=(0,20), pady=(5,10), sticky="w")

        # tabview "Additional"
        self.what_parameter_label = customtkinter.CTkLabel(self.tabview.tab("Additional"),
                                                           text="IndParam:",
                                                           font=font,
                                                           compound="left")
        self.what_parameter_label.grid(row=0, column=0, padx=(20,2), pady=(10,5), sticky="w")
        self.what_parameter_entry = customtkinter.CTkEntry(self.tabview.tab("Additional"),
                                                              placeholder_text="t",
                                                              font=font,
                                                              width=80)
        self.what_parameter_entry.grid(row=0, column=1, padx=(0,20), pady=(10,5), sticky="ew")
        self.result_components_label = customtkinter.CTkLabel(self.tabview.tab("Additional"),
                                                              text="#ResComps:",
                                                              font=font,
                                                              compound="left")
        self.result_components_label.grid(row=1, column=0, padx=(20,5), pady=(5,10), sticky="w")
        self.result_components_combobox = customtkinter.CTkComboBox(self.tabview.tab("Additional"),
                                                                    values=[str(i) for i in range(1,4)],
                                                                    #variable=self.result_components,
                                                                    font=font,
                                                                    width=80)
        self.result_components_combobox.grid(row=1, column=1, padx=(0,20), pady=(5,10), sticky="ew")

        # confirm frame | background_corner_colors=("gray17","gray17","gray14","gray14")
        self.confirm_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.confirm_frame.grid(row=1, column=0, padx=(5,2), pady=(0,5), sticky="nsew")
        self.confirm_frame.grid_columnconfigure(0, weight=1)
        self.confirm_frame.grid_rowconfigure(0, weight=1)
        self.confirm_inputs_button = customtkinter.CTkButton(self.confirm_frame,
                                                             text="Confirm",
                                                             font=button_font,
                                                             width=80,
                                                             command=self.confirm_input)
        self.confirm_inputs_button.grid(row=0, column=0, padx=(0,0), pady=20)

        # compute frame
        self.compute_frame = customtkinter.CTkFrame(self, height=300, corner_radius=0)
        self.compute_frame.grid(row=0, column=1, rowspan=2, padx=(3,5), pady=(10,5), sticky="nsew")
        self.compute_frame.grid_columnconfigure(0, weight=1)
        self.compute_frame.grid_rowconfigure((2), weight=1)
        # self.compute_frame.grid_propagate(False)
        self.input_confirmation_label = customtkinter.CTkLabel(self.compute_frame,
                                                               text="Interpreted Input:",
                                                               font=font)
        self.input_confirmation_label.grid(row=0, column=0, padx=10, pady=(10,0))
        self.input_confirmation_textbox = customtkinter.CTkTextbox(self.compute_frame,
                                                                   height=120,
                                                                   font=font)
        self.input_confirmation_textbox.grid(row=1, column=0, padx=10, pady=(10,0), sticky="nsew")
        self.compute_params_button = customtkinter.CTkButton(self.compute_frame,
                                                             text="Compute Parameters",
                                                             font=button_font,
                                                             command=self.compute_params)
        self.compute_params_button.grid(row=3, column=0, pady=(0,25))


        # set default values
        msg = self.create_interpretation_string()
        self.input_confirmation_textbox.insert("1.0", msg)
        self.compute_params_button.configure(state="disabled")

        # set tooltip for compute button
        self.compute_button_tooltip = ToolTip(widget=self.compute_params_button,
                          msg="You need to confirm your inputs before computation.", delay=0,
                          parent_kwargs={"bg": "gray14", "padx": 2, "pady": 2},
                          fg="#ffffff", bg="gray17", padx=3, pady=3)


    def remove_tooltip(self) -> None:
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


    def create_interpretation_string(self,
                                     function: Optional[str] = "...",
                                     var: Optional[str] = "...",
                                     consts: Optional[str] = "...",
                                     **kwargs: Optional[str]) -> str:

        msg = f"Function: {function}\nIndependent Variable(s): {var}\nConstants to be fitted: {consts}"
        if kwargs is not None:
            for descr, val in kwargs.items():
                msg += f"\n{descr}: {val}"
        return msg


    def display_interpreted_input(self, msg) -> None:
        # clear text Widget
        self.input_confirmation_textbox.delete("1.0", tkinter.END)
        # add new text to widget
        self.input_confirmation_textbox.insert("1.0", msg)


    def confirm_input(self) -> None:
        msg = self.create_interpretation_string(function=self.equation_entry.get(),
                                                var=self.what_parameter_entry.get(),
                                                consts="a,b",
                                                hello="world",
                                                bye="sanity")
        self.display_interpreted_input(msg)
        self.remove_tooltip()

        # self.equation_entry.get()
        # self.file_name.get()
        # self.what_parameter_entry.get()
        # self.result_components_combobox.get()



    def compute_params(self) -> None:
        print(self.geometry())