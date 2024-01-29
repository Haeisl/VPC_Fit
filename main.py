from src.CTkInterface import MainApp


def handle_leftclick(event):
    widget = event.widget
    if not widget:
        pass
    elif isinstance(widget, str):
        pass
    else:
        widget.focus_set()


def main():
    app = MainApp()
    app.bind_all("<Button-1>", lambda event: handle_leftclick(event))
    app.mainloop()


if __name__ == '__main__':
    main()