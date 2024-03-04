from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.CTkInterface import MainApp

import customtkinter

import logging
logger = logging.getLogger("ResultInterface")

class ResultInterface(customtkinter.CTkToplevel):

    def __init__(self, main_window: MainApp):
        super().__init__(main_window)
        self.main = main_window
        self.title_string = customtkinter.StringVar(self, "Virtual Patient Cohorts - Results")

        self.title(self.title_string.get())
        window_width = 350
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.resizable(width=False, height=False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        result_font = customtkinter.CTkFont(family="Arial", size=16, weight="bold")
        button_font = customtkinter.CTkFont(family="Arial", size=14)
        symbol_font = customtkinter.CTkFont(size=25)
        saved_font = customtkinter.CTkFont(family="Arial", size=16, weight="bold", slant="italic")

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
        self.result_label = customtkinter.CTkLabel(
            self.results_frame,
            text="Werbung\nWerbung\nWerbung\nWerbung\nWerbung\nWerbung",
            font=result_font,
            bg_color="gray23"
        )
        self.result_label.grid(
            row=0, column=0,
            ipadx=5, ipady=5,
            padx=10, pady=(10,0),
            sticky="nsew"
        )

        # lower frame
        self.button_frame = customtkinter.CTkFrame(self, corner_radius=0)
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
            padx=(10,20), pady=10
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
            padx=(20,10), pady=10
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
            padx=(0,10), pady=10,
            sticky="nsew"
        )


    def save_as(self) -> None:
        if self.main.save_results() != 1:
            self.saved_message.set("Saved to ./res/ ")
            self.save_button.configure(state="disabled")
        else:
            error_font = customtkinter.CTkFont(family="Arial", size=16, weight="bold")
            self.saved_label.configure(text_color="red", font=error_font)
            self.saved_message.set("Something\nwent wrong")


    def reset_app(self) -> None:
        self.main.reset_state()
        self.destroy()