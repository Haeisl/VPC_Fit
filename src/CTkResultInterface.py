# standard library imports
from __future__ import annotations
import logging
from collections.abc import Callable
from itertools import cycle
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.CTkInterface import MainApp

# related third party imports
import customtkinter
import matplotlib.pyplot as plt
from PIL import Image
from sympy import FunctionClass

# local imports
from src.VPCModel import VPCModel


logger = logging.getLogger("ResultInterface")


class FailedFitInterface(customtkinter.CTkToplevel):
    """Intereface for displaying a message for a failed fit."""
    def __init__(self, main_window: MainApp):
        """Initialize the failed fit interface.
        :param main_window: Parent window.
        :type main_window: MainApp
        """
        super().__init__(main_window)
        self.main = main_window
        self.title("Fit Unsuccessful")

        window_width = 425
        window_height = 210
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.resizable(width=False, height=False)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        text_font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
        symbol_font = customtkinter.CTkFont(size=25, weight="bold")

        self.message_label = customtkinter.CTkLabel(
            self,
            text="Fitting process was unsuccessful.",
            font=text_font,
            text_color="red"
        )
        self.message_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.reset_button = customtkinter.CTkButton(
            self,
            text="\u21BA",
            font=symbol_font,
            command=self.reset_app,
            text_color="white",
        )
        self.reset_button._set_dimensions(width=40, height=30)
        self.reset_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def reset_app(self) -> None:
        """Reset the parent application's state and close this window."""
        self.main.reset_state()
        self.destroy()


class ResultInterface(customtkinter.CTkToplevel):
    """Interface for results created by ``ModelFitter``.

    Provides a way to save results locally and view a plot of the residuals of the fit if possible.

    Uses a ``tkinter`` extension called ``customtkinter`` to achieve a modern look.
    """
    def __init__(
        self,
        main_window: MainApp,
        model: VPCModel,
        fitted_model: VPCModel,
        data: list[list[int | float]]
    ) -> None:
        """Setup of the result interface window, arranging widgets and setting values.

        :param main_window: Parent window.
        :type main_window: MainApp
        :param model: Model that was fitted to the sample data.
        :type model: VPCModel
        :param fitted_model: Fitted model as a means to get easy access to the fitted model's lambda function.
        :type fitted_model: VPCModel
        :param data: The data the input was fitted to.
        :type data: list[list[int | float]]
        """
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
        self.grab_set()

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
        chart_disabled = "chart-line-disabled.png"
        graph_image = customtkinter.CTkImage(
            dark_image=Image.open(chart_line_bright),
            size=(26,26)
        )
        disabled_image = customtkinter.CTkImage(
            dark_image=Image.open(chart_disabled),
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

        if self.fitted_model.is_ode():
            self.show_graph_button.configure(state="disabled", image=disabled_image)
            self.main.create_tooltip_for(self.show_graph_button, "Can't show graph for ODE models")

        self.set_result_label_text()

    def process_lists(self, lst: list[list[float]]) -> list[float] | list[tuple[float, ...]]:
        """Converts a list of lists of floats into a list of floats,
        if there is only a single sub-list.

        If there are multiple sub-lists inside the input list, will zip them
        and return a list of tuples of floats.

        :param lst: List that is to be converted, typically the data the model was fitted to, or part of it.
        :type lst: list[list[float]]
        :raises ValueError: If there are types other than ``list`` in the outer list.
        :return: List of floats or list of tuples of floats.
        :rtype: list[float] | list[tuple[float, ...]]
        """
        if len(lst) == 1 and isinstance(lst[0], list):
            return lst[0]
        elif all(isinstance(sub_lst, list) for sub_lst in lst):
            return list(zip(*lst))
        else:
            raise ValueError("Got invalid input list.")

    def create_difference_dict(
        self,
        list_actual: list[tuple[float, ...]],
        list_predicted: list[tuple[float, ...]]
        ) -> dict[int,list[float]]:
        """Used to compute the differences (residuals) of two input lists created by ``process_lists()``.
        Stores the differences at each index in a dictionary with index:difference pairs.

        :param list_actual: list of the actual values.
        :type list_actual: list[tuple[float, ...]]
        :param list_predicted: list of the predicted values.
        :type list_predicted: list[tuple[float, ...]]
        :raises ValueError: If the input lists somehow have different lengths.
        :raises ValueError: If a pair of tuples somehow have different lengths.
        :return: Dictionary with the differences at their corresponding index.
        :rtype: dict[int,list[float]]
        """
        if len(list_actual) != len(list_predicted):
            raise ValueError("Input lists must have the same length.")

        diff_dict: dict[int,list] = {}

        for i, (tuple1, tuple2) in enumerate(zip(list_actual, list_predicted)):
            if len(tuple1) != len(tuple2):
                raise ValueError(f"Tuples at index {i} have different lengths.")
            for j, (elem1, elem2) in enumerate(zip(tuple1, tuple2)):
                if j not in diff_dict:
                    diff_dict[j] = []
                diff_dict[j].append(elem2 - elem1)

        return diff_dict

    def graph_residuals(self) -> None:
        """Method that uses matplotlib to graph the residuals of the fitted model against
        the input data after the graph button is pressed.
        """
        func: FunctionClass = self.fitted_model.model_function
        num_indep_vars: int = len(self.model.independent_var)
        xdata: list[list[float]] = self.data[:num_indep_vars]
        ydata: list[list[float]] = self.data[num_indep_vars:]
        formatted_func: Callable = lambda tuple: func(*tuple)
        formatted_xdata: list[float] | list[tuple[float, ...]] = self.process_lists(xdata)
        formatted_ydata: list[float] | list[tuple[float, ...]] = self.process_lists(ydata)
        if all(isinstance(xdata, tuple) for xdata in formatted_xdata):
            predicted_values: list[float] | list[tuple[float, ...]] = [
                formatted_func(xdata) for xdata in formatted_xdata
            ]
        else:
            predicted_values = [func(xdata) for xdata in formatted_xdata]

        if self.fitted_model.is_vector():
            diff_dict: dict[int,list[float]] = self.create_difference_dict(formatted_ydata, predicted_values) # type: ignore
            n = len(diff_dict[0]) # assuming all lists have the same length (they should)
            colors = ["b", "g", "r", "c", "m", "y", "k"]
            color_cycle = cycle(colors)
            for key, values in diff_dict.items():
                color = next(color_cycle)
                plt.scatter(range(n), values, label=f"Residuals of Component {key}", color=color)
                plt.xticks(range(n), [str(label) for label in formatted_xdata], rotation="vertical")
                plt.xlabel("X Data")
                plt.ylabel("Residuals")
        else:
            n = len(formatted_ydata)
            residuals = [y - p for y, p in zip(formatted_ydata, predicted_values)] # type: ignore
            plt.scatter(predicted_values, residuals, label="Residuals")
            plt.xlabel("Predicted Values")
            plt.ylabel("Residuals")
        plt.axhline(y=0, color="black", linestyle="--")
        plt.title("Residual Plot")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def set_result_label_text(self) -> None:
        """Method that sets the text inside the results textbox."""
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
        """Method that calls the parent's ``save_results()`` method and
        sets the saved_message_label's value accordingly after the save button is pressed.
        """
        if self.main.save_results() == 0:
            self.saved_message.set("Saved to ./res/ ")
            self.save_button.configure(state="disabled")
        else:
            error_font = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
            self.saved_label.configure(text_color="red", font=error_font)
            self.saved_message.set("Something\nwent wrong")

    def reset_app(self) -> None:
        """Method that calls the parent's ``reset_state()`` method to reset the app to an
        initial state after the reset button is pressed.
        """
        self.main.reset_state()
        self.destroy()