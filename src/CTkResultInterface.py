# standard library imports
from __future__ import annotations
import logging
import matplotlib.pyplot as plt
from PIL import Image
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.CTkInterface import MainApp

# related third party imports
import customtkinter

# local imports
from src import VPCModel


logger = logging.getLogger("ResultInterface")


class ResultInterface(customtkinter.CTkToplevel):
    """_summary_

    _extended_summary_

    :param customtkinter: _description_
    :type customtkinter: _type_
    """
    def __init__(self, main_window: MainApp, model: VPCModel, fitted_model: VPCModel, data):
        super().__init__(main_window)
        self.main = main_window
        self.title_string = customtkinter.StringVar(self, "Virtual Patient Cohorts - Results")
        # self.model = model
        # self.fitted_model = fitted_model
        # self.data = data


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
            command=self.reset_app
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
            command=self.save_as
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
        # chart_bright = "chart-simple-solid-white.png"
        # chart_dark = "chart-simple-solid-black.png"
        # chart_line_bright = "chart-line-bright.png"
        # chart_line_dark = "chart-line-dark.png"
        # signal_dark = "signal-solid.png"
        signal_bright = "signal-solid-bright.png"
        graph_image = customtkinter.CTkImage(
            dark_image=Image.open(signal_bright),
            size=(35,28)
        )
        self.show_graph_button = customtkinter.CTkButton(
            self.button_frame,
            #text="\U0001F4C8",
            text="",
            image=graph_image,
            anchor="n",
            command=self.show_graph
        )
        self.show_graph_button._set_dimensions(width=40, height=30)
        self.show_graph_button.grid(
            row=0, column=3,
            padx=(0,20), pady=10,
            sticky="e"
        )

    # def set_vars(self, data, function):
    #     self.data = data
    #     self.function = function

    def show_graph(self):
        y = []
        for x in self.data[0]:
            y.append(self.function(x))
        plt.scatter(self.data[0], self.data[1], label="Data Points", color="blue", marker="o")
        plt.plot(self.data[0], y, label='Fitted Function', color='red')
        plt.xlabel('x-axis')
        plt.ylabel('y-axis')
        plt.legend()
        plt.grid(True)
        plt.show()

    def set_result_label_text(self, message: str) -> None:
        self.result_label.insert(1.0, message)

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