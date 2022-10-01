#!/usr/bin/python
"""This script contains the main entry point for a simple log parser."""

from argparse import ArgumentError
from inspect import Parameter
#from sys import argv
import sys
from typing import Dict, List, Tuple

from log_parser import LogParser
from utils import unformat

# Constants
DEFAULT_LOG_LINE_FORMAT = (
    "{unit}: {hour}:{minutes}:{seconds} {severity_level} {charm_name} {message}\n"
)


def to_process_log(log: Dict[str, str], selected_charm_name: str = None) -> bool:
    """Determine if the parsed log should be processed or not.

    Args:
        log (Dict[str, str]): log entries
        selected_charm_name (str, optional): Single charm to process

    Returns:
        bool: log should be processed or not
    """
    if log is None:
        return False

    if selected_charm_name is not None:
        return log.get("charm_name") == selected_charm_name

    return True


def log_file_reader(
    log_file: str,
    log_line_format: str = DEFAULT_LOG_LINE_FORMAT,
    selected_charm_name: str = None,
):
    """Produce a valid parsed log entry at each call.

    Generator of valid (i.e., that start with a unit name and
    that match the selected charm name if specified) parsed log entry
    (as a dictionary) at each call from the lines of a log file.

    Args:
        log_file (str): Path of the log file to parse
        log_line_format (str, optional): Format of the log line.
            Defaults to DEFAULT_LOG_LINE_FORMAT.
        selected_charm_name (str, optional): Single charm to process
    """
    # Create generator of parsed logs
    logs = (
        unformat(log_line, log_line_format) for log_line in open(log_file, mode="r")
    )

    # Create generator of valid parsed logs
    return (log for log in logs if to_process_log(log, selected_charm_name))


def parse_args(args: List[str]) -> Tuple[str, str]:
    """Parse arguments into a configurations dictionary.

    Args:
        args (List[str]): List of arguments

    Returns:
        Tuple[str, str]: Tuple with the parsed arguments
            (log file path, selected charm name)
    """
    if args is None:
        raise TypeError("Args cannot be None")
    
    argc = len(args)
    if argc < 2:
        raise TypeError("Missing mandatory parameter!")
    elif argc == 2:
        return args[1], None  # file_name, None
    else:
        return args[1], args[2]  # file_name, selected_charm_name


# Main
def main(argv):
    # Process the arguments into variables
    try:
        log_file, charm_name = parse_args(argv)
    except TypeError as ex:
        print(ex)
        print(f"Usage: {argv[0]} FILE [CHARM]")
        return -1

    try:
        # Create a reader for the log file that returns parsed valid logs
        log_reader = log_file_reader(log_file, DEFAULT_LOG_LINE_FORMAT, charm_name)
    except FileNotFoundError as ex:
        print(ex)
        return -1

    # Process the logs provided by the log_reader using a LogParser
    log_parser = LogParser()
    log_parser.process_logs(log_reader)
    print(log_parser)
    return 0

if __name__ == "__main__":
    status = main(sys.argv)
    exit(status)
    
