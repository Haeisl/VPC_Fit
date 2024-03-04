import json
import logging
import logging.config
import logging.handlers
import os
import pathlib
import argparse
from src.CTkInterface import MainApp
from tkinter import Event, Widget


def setup_logging(debug: bool = False):
    """logging should look like:
        logger_name.level(
            f"message {variable}"
            f"  message {variable}"
        )
    including all those indentations
    """

    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    filename = "logs.log"

    log_filename = os.path.join(log_folder, filename)

    config_file = pathlib.Path("logging_config.json")
    with open(config_file) as json_file:
        config = json.load(json_file)

    config["handlers"]["fileHandler"]["filename"] = log_filename

    if debug:
        for handler in config["handlers"]:
            config["handlers"][handler]["level"] = "DEBUG"

    logging.config.dictConfig(config)



def handle_leftclick(event: Event) -> None:
    widget: Widget = event.widget
    if not widget:
        pass
    elif isinstance(widget, str):
        pass
    else:
        widget.focus_set()


def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A GUI application for fitting a user-provided model to data.",
        epilog=(
            "Note:\n"
            "  This program was developed as part of a bachelor's degree project\n"
            "  and may have arbitrary limitations and/or room for improvement.\n"
            "  Use at your own discretion."
        ),
        usage="py %(prog)s    [-h]    [--debug]"
    )
    parser.add_argument("--debug", action="store_true", help="enable debug level logging")

    args = parser.parse_args()

    setup_logging(debug=bool(args.debug))
    root_logger = logging.getLogger()

    root_logger.info("Starting App")
    app = MainApp()
    app.bind_all("<Button-1>", lambda event: handle_leftclick(event))
    app.mainloop()
    root_logger.info("App closed")

if __name__ == "__main__":
    main()