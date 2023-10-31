import tkinter as tk
from tkinter import filedialog
from FileHandler import FileHandler
from VPCData import VPCData
from ModelFitter import ModelFitter


class ResultsWindow(tk.Toplevel):
    def __init__(self, mainWindow, message):
        super().__init__(mainWindow)
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        windowWidth = 320
        windowHeight = 120
        centerX = int(screenWidth/2 - windowWidth/2 + 425/2)
        centerY = int(screenHeight/2 - 240/4)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')

        # labels
        self.finalEquation = tk.StringVar(self)
        self.finalEquation.set(f"f(t) = {message[0]}*t + {message[1]}")
        self.finalEquationLabel = tk.Label(self, textvariable=self.finalEquation)

        # grid
        self.finalEquationLabel.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)


class MainApplication(tk.Tk):
    """
    A class to handle the functionality of the interface

    ...

    Attributes
    ----------

    filePath: str
        path to the file to be read or written
    funcParams: tk.StringVar()
        parameters of the function to be fitted
    numResComps: tk.StringVar()
        number of components of the result
    fileName: tk.StringVar()
        name of the file to be read or written
    modelEquation: tk.StringVar()
        equation of the function to be fitted


    Methods
    -------



    """


    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Virtual Patient Cohort Generator')
        self.filePath = None

        # setting window geometry relative to screen geometry
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        windowWidth = 460
        windowHeight = 260
        centerX = int(screenWidth/2 - windowWidth/2)
        centerY = int(screenHeight/2 - windowHeight/2)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # labels
        self.equationLabel = tk.Label(text="Equation:")
        self.parameterLabel = tk.Label(text="What Parameter:")
        self.resComponentsLabel = tk.Label(text="# Result Components:")
        self.dataInputLabel = tk.Label(text="Data:")

        # entries
        self.equationEntry = tk.Entry()
        self.parameterEntry = tk.Entry()

        vcmd = (self.register(self.validateEntry))
        self.resComponents = tk.IntVar(value=1)
        self.resComponentsEntry = tk.Entry(textvariable=self.resComponents, validate='all', validatecommand= (vcmd, '%P'), width=5)

        # buttons
        self.fileName = tk.StringVar(self, 'Browse...')
        self.dataInputButton = tk.Button(textvariable=self.fileName, command=self.browseFiles)
        self.generateDataButton = tk.Button(text='Compute Parameters', command=self.computeParameters)

        # placement in window
        labelPaddingX = (20,5)

        # 1st row
        self.equationLabel.grid(column=0, row=0, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.equationEntry.grid(column=2, row=0, sticky=tk.W, padx=0, pady=5)

        # 2nd row
        self.parameterLabel.grid(column=0, row=1, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.parameterEntry.grid(column=2, row=1, sticky=tk.W, padx=0, pady=5)

        # 3rd row
        self.resComponentsLabel.grid(column=0, row=2, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.resComponentsEntry.grid(column=2, row=2, sticky=tk.W, padx=(0,20), pady=5)

        # 4th row
        self.dataInputLabel.grid(column=0, row=3, columnspan=2, sticky=tk.W, padx=labelPaddingX, pady=5)
        self.dataInputButton.grid(column=2, row=3, columnspan=4, sticky=tk.W, ipadx=20, padx=(2,20), pady=5)

        # 5th row
        self.generateDataButton.grid(column=2, row=4, columnspan=2, sticky=tk.E, ipadx=20, padx=(5,20), pady=(10,5))

    def openResultsWindow(self, parameters):
        resultsWindow = ResultsWindow(self, parameters)

    def validateEntry(self, P: str):
        """
        Validation method to ensure only digits are entered for #Function Parameters and #Result Components

        Args:
            P (str): character that user tries to enter
        Returns:
            True: if entered character is a digit or empty (e.g. backspace)
            False: otherwise
        """
        return P.isdigit() or P == ''
    
    def browseFiles(self):
        """
        Opens filedialog for user to specify the location of the file.
        Sets fileName and filePath if user did not cancel the dialog.
        """
        fp = filedialog.askopenfile()
        if fp is not None:
            fn = fp.name.split('/')[-1]
            self.fileName.set(fn)
            self.filePath = fp.name
    
    def computeParameters(self):
        self.openResultsWindow([2, 3])


if __name__ == '__main__':
    main = MainApplication()
    main.mainloop()