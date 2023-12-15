import os
import tkinter as tk
from tkinter import filedialog
from typing import Optional, Tuple, Union
from .FileHandler import FileHandler
from .VPCData import VPCData
from .ModelFitter import ModelFitter
import customtkinter

class MainApplication(customtkinter.CTk):
    def __init__(self, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)


def main():
    app = MainApplication()
    MainApplication.mainloop()

if __name__ == "__main__":
    main()