# standard library imports
import argparse
import json
import logging
import logging.config
import logging.handlers
from pathlib import Path
from tkinter import Event, Widget

# local imports
from src.CTkInterface import MainApp


def setup_logging(debug: bool = False):
    """Logging setup for the program.

    Logs are saved in a ``./logs/`` directory relative to the current working directory,
    which will be created if it's not present.
    Logging config uses a 'logging_config.json' file in this module's directory.

    :param debug: flag that gets passed through by argparse to enable logging on ``debug`` level,\
    defaults to False
    :type debug: bool, optional
    """

    log_folder = Path("./logs")
    log_folder.mkdir(exist_ok=True)

    log_file = log_folder / "logs.log"

    config_file = Path("logging_config.json")
    with open(config_file) as json_file:
        config = json.load(json_file)

    config["handlers"]["fileHandler"]["filename"] = log_file

    if debug:
        for handler in config["handlers"]:
            config["handlers"][handler]["level"] = "DEBUG"

    logging.config.dictConfig(config)


def handle_leftclick(event: Event) -> None:
    """Helper function to set the focus to the widget associated with the current event ``event``.

    Is used to set the focus to whatever widget is clicked by the user.

    :param event: The event, i.e. left mouse click.
    :type event: Event
    """
    widget: Widget = event.widget
    if not widget:
        pass
    elif isinstance(widget, str):
        pass
    else:
        widget.focus_set()


def main():
    """Main function.

    Setting up ``argparse`` to catch the ``--debug`` flag on startup, running ``setup_logging()``
    and finally running the program, i.e. its ``mainloop()``.
    """
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