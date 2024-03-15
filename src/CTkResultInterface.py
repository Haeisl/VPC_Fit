# standard library imports
from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from src.CTkInterface import MainApp

# related third party imports
import customtkinter
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from sympy import FunctionClass

# local imports
from src.VPCModel import VPCModel


logger = logging.getLogger("ResultInterface")


class ResultInterface(customtkinter.CTkToplevel):
    """_summary_

    _extended_summary_

    :param customtkinter: _description_
    :type customtkinter: _type_
    """
    def __init__(self, main_window: MainApp, model: VPCModel, fitted_model: VPCModel, data: list[list[Union[int, float]]]):
        super().__init__(main_window)
        self.main = main_window
        self.model = model
        self.fitted_model = fitted_model
        self.data = data
        self.title_string = customtkinter.StringVar(self, "Virtual Patient Cohorts - Results")

        self.title(self.title_string.get())
        window_width = 425
        window_height = 210
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.resizable(width=False, height=False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        result_font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
        button_font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
        symbol_font = customtkinter.CTkFont(size=25, weight="bold")
        saved_font = customtkinter.CTkFont(family="Arial", size=14, weight="bold", slant="italic")

        # upper frame
        self.results_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid(
            row=0, column=0,
            rowspan=2,
            padx=0, pady=0,
            sticky="nsew"
        )
        self.result_label = customtkinter.CTkTextbox(
            self.results_frame,
            font=result_font,
            #bg_color="gray23"
        )
        self.result_label.grid(
            row=0, column=0,
            ipadx=5, ipady=5,
            padx=10, pady=(10,0),
            sticky="nsew"
        )

        # lower frame
        self.button_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid(
            row=2, column=0,
            padx=0, pady=0,
            sticky="nsew"
        )
        self.reset_button = customtkinter.CTkButton(
            self.button_frame,
            text="\u21BA",
            font=symbol_font,
            command=self.reset_app,
            text_color="white"
        )
        self.reset_button._set_dimensions(width=40, height=30)
        self.reset_button.grid(
            row=0, column=0,
            padx=(20,10), pady=10
        )
        self.save_button = customtkinter.CTkButton(
            self.button_frame,
            text="Save",
            font=button_font,
            command=self.save_as,
            text_color="white"
        )
        self.save_button._set_dimensions(width=120, height=36)
        self.save_button.grid(
            row=0, column=1,
            padx=(20,0), pady=10
        )
        self.saved_message = customtkinter.StringVar(self, "")
        self.saved_label = customtkinter.CTkLabel(
            self.button_frame,
            textvariable=self.saved_message,
            font=saved_font,
            text_color="green"
        )
        self.saved_label.grid(
            row=0, column=2,
            ipadx=5, ipady=5,
            padx=(10,10), pady=7,
            sticky="nsew"
        )
        chart_line_bright = "chart-line-bright.png"
        graph_image = customtkinter.CTkImage(
            dark_image=Image.open(chart_line_bright),
            size=(26,26)
        )
        self.show_graph_button = customtkinter.CTkButton(
            self.button_frame,
            text="",
            image=graph_image,
            anchor="n",
            command=self.graph_residuals
        )
        self.show_graph_button._set_dimensions(width=40, height=30)
        self.show_graph_button.grid(
            row=0, column=3,
            padx=(0,20), pady=10,
            ipady=1,
            sticky="e"
        )

        self.set_result_label_text()

    # def show_graph(self) -> None:
    #     func: FunctionClass = self.fitted_model.model_function
    #     xdata: list[Union[int,float]] = self.data[0]
    #     original_ydata: list[Union[int,float]] = self.data[1]
    #     fitted_y: list[Union[int,float]] = []
    #     for x in self.data[0]:
    #         fitted_y.append(func(x))

    #     plt.scatter(xdata, original_ydata, label="Data Points", color="blue", marker="o")
    #     plt.plot(xdata, fitted_y, label="Fitted Function", color="red")
    #     plt.xlabel("x-axis")
    #     plt.ylabel("y-axis")
    #     plt.legend()
    #     plt.grid(True)
    #     plt.show()

    def process_lists(self, lst: Union[list, list[list]]) -> list:
        if len(lst) == 1 and isinstance(lst[0], list):
            return lst[0]
        elif all(isinstance(sub_lst, list) for sub_lst in lst):
            return list(zip(*lst))
        else:
            raise ValueError("Got invalid input list.")

    def graph_residuals(self) -> None:
        func: FunctionClass = self.fitted_model.model_function
        formatted_func = lambda tuple: func(*tuple)
        num_indep_vars = len(self.model.independent_var)
        xdata: list[list[float]] = self.data[:num_indep_vars]
        formatted_xdata = self.process_lists(xdata)
        ydata: list[list[float]] = self.data[num_indep_vars:]
        formatted_ydata = self.process_lists(ydata)
        predicted_values: list[tuple] = []
        if isinstance(formatted_xdata[0], tuple):
            predicted_values = [formatted_func(formatted_xdata[i]) for i in range(len(formatted_xdata))]
        else:
            predicted_values = [func(formatted_xdata[i]) for i in range(len(formatted_xdata))]
        residuals: list[Union[tuple, float]] = []
        if isinstance(formatted_ydata[0], tuple) and isinstance(predicted_values[0], tuple) and len(formatted_ydata[0]) == len(predicted_values[0]):
            res = dict().fromkeys(range(len(formatted_ydata)))
            for i in range(len(formatted_ydata[0])):
                for j in range(len(formatted_ydata)):
                    res[i] = formatted_ydata[j][i] - predicted_values[j][i]
        print(formatted_xdata)
        print(formatted_ydata)
        print(predicted_values)
        print(res)

    def set_result_label_text(self) -> None:
        result_message = (
            f"Fitted model equation:\n"
            f"  {self.model.resulting_function}\n\n"
            f"Fitted constants:\n"
            f"{"  " + "\n  ".join(
                str(pair[0]) + " = " + str(pair[1]) for pair in self.model.fitted_consts.items()
            )}"
        )
        self.result_label.insert(1.0, result_message)

    def save_as(self) -> None:
        if self.main.save_results() == 0:
            self.saved_message.set("Saved to ./res/ ")
            self.save_button.configure(state="disabled")
        else:
            error_font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
            self.saved_label.configure(text_color="red", font=error_font)
            self.saved_message.set("Something\nwent wrong")

    def reset_app(self) -> None:
        self.main.reset_state()
        self.destroy()