from src.Interface import MainApplication
from src.ModelFitter import ModelFitter
from sympy import sympify

from src.ctkInterface import MainApp

def main():
    # app = MainApplication()
    # app.mainloop()
    app = MainApp()
    app.mainloop()

if __name__ == '__main__':
    main()