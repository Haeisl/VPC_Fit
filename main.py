from src.Interface import MainApplication
from src.ModelFitter import ModelFitter
from sympy import sympify

from src.ctkInterface import MainApp

def main():
    # app = MainApplication()
    # app.mainloop()
    app = MainApp()
    app.bind_all("<1>", lambda event:event.widget.focus_set())
    app.mainloop()

if __name__ == '__main__':
    main()