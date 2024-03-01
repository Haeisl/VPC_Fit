import logging

class MultilineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        save_msg = record.msg
        output = ""
        lines = save_msg.splitlines()
        for i, line in enumerate(lines):
            record.msg = line
            output += super().format(record)
            if i < len(lines) - 1:
                output += "\n"
        record.msg = save_msg
        record.message = output
        return output