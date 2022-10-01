"""This file contains the implementation of a tester class for main.py."""

import errno
import os
from io import StringIO
from unittest import TestCase, main
from unittest.mock import mock_open, patch

from main import DEFAULT_LOG_LINE_FORMAT, log_file_reader
from main import main as app_main
from main import parse_args, to_process_log

# Constants
LOG_FILE_1 = """controller-0: 01:47:48 INFO juju.worker.logger logger worker started
machine-0: 01:56:55 INFO juju.cmd running jujud [2.8.1 0 16439b3d1c528b7a0e019a16c2122ccfcf6aa41f gc go1.14.4]
"""

LOG_SAMPLE_0 = {
    "unit": "controller-0",
    "hour": "01",
    "minutes": "47",
    "seconds": "48",
    "severity_level": "INFO",
    "charm_name": "juju.worker.logger",
    "message": "logger worker started",
}

LOG_SAMPLE_1 = {
    "unit": "machine-0",
    "hour": "01",
    "minutes": "56",
    "seconds": "55",
    "severity_level": "INFO",
    "charm_name": "juju.cmd",
    "message": "running jujud [2.8.1 0 16439b3d1c528b7a0e019a16c2122ccfcf6aa41f gc go1.14.4]",
}

OUT_0 = """Missing mandatory parameter!
Usage: path/to/main FILE [CHARM]
"""

OUT_1 = """Global:
  INFO: 2
  DEBUG: 0
  WARNING: 0
  ERROR: 0
  TOTAL: 2

Per Charm:
  juju.worker.logger:
    INFO: 1
    DEBUG: 0
    WARNING: 0
    ERROR: 0
    TOTAL: 1
  juju.cmd:
    INFO: 1
    DEBUG: 0
    WARNING: 0
    ERROR: 0
    TOTAL: 1

"""

OUT_2 = """juju.cmd:
  INFO: 1
  DEBUG: 0
  WARNING: 0
  ERROR: 0
  TOTAL: 1

"""

OUT_3 = """[Errno 2] No such file or directory: '%s'
"""


class ToProcessLogTester(TestCase):
    """Tester class used for testing the to_process_log function."""

    def test_none_log(self):
        """Return False on None log."""
        result = to_process_log(None)
        self.assertFalse(result)

    def test_empty_string_log(self):  # What name give this?
        """Return False on empty string log."""
        result = to_process_log("")  # Should throw error because it is not a dict?
        self.assertTrue(result)

    def test_empty_log(self):
        """Return False on empty log."""
        result = to_process_log({})
        self.assertTrue(result)

    def test_simple_log(self):  # What name give this?
        """Return True on valid log."""
        result = to_process_log(LOG_SAMPLE_1)
        self.assertTrue(result)

    def test_log_with_selected_charm(self):  # What name give this?
        """Return True on valid log with selected charm."""
        result = to_process_log(LOG_SAMPLE_1, LOG_SAMPLE_1["charm_name"])
        self.assertTrue(result)

    def test_log_with_unselected_charm(self):
        """Return False on valid log with unselected charm."""
        result = to_process_log(LOG_SAMPLE_1, "juju.network")
        self.assertFalse(result)


class LogFileReader(TestCase):
    """Tester class used for testing the log_file_reader function."""

    def test_mock_file(self):
        """Read two valid log entries from a mock file."""
        mock_file = mock_open(read_data=LOG_FILE_1)

        log_file_path = "path/to/open"
        expected = [LOG_SAMPLE_0, LOG_SAMPLE_1]

        with patch("builtins.open", mock_file):
            log_reader = log_file_reader(log_file_path, DEFAULT_LOG_LINE_FORMAT)
            result = [log for log in log_reader]

            self.assertListEqual(result, expected)
            mock_file.assert_called_with(log_file_path, mode="r")


class ParseArgsTester(TestCase):
    """Tester class used for testing the parse_args function."""

    def test_none_args(self):
        """Raise TypeError when the args are None."""
        self.assertRaises(TypeError, parse_args, None)

    def test_empty_args(self):
        """Raise TypeError when the args are Empty."""
        self.assertRaises(TypeError, parse_args, [])

    def test_less_args(self):
        """Raise TypeError when the args are less than required."""
        self.assertRaises(TypeError, parse_args, ["arg0"])

    def test_mandatory_parameter(self):
        """Return first argument."""
        args = ["arg0", "arg1"]
        expected = ("arg1", None)
        result = parse_args(args)
        self.assertTupleEqual(result, expected)

    def test_optional_parameter(self):
        """Return both arguments as a Tuple."""
        args = ["arg0", "arg1", "arg2"]
        expected = ("arg1", "arg2")
        result = parse_args(args)
        self.assertTupleEqual(result, expected)


class MainTester(TestCase):
    """Tester class used for testing the main function."""

    def test_no_args(self):
        """Launch main with no arguments, returns an error."""
        argv = ["path/to/main"]

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            status = app_main(argv)
            out = mock_out.getvalue()

            self.assertEqual(status, -1)
            self.assertEqual(out, OUT_0)

    def test_non_existing_file(self):
        """Try to process a file that does not exit."""
        mock_file = mock_open(read_data=LOG_FILE_1)

        log_file_path = "path/to/open"
        argv = ["path/to/main", log_file_path]

        mock_file.side_effect = FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), log_file_path
        )

        with patch("builtins.open", mock_file):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                status = app_main(argv)
                out = mock_out.getvalue()

                self.assertEqual(status, -1)
                self.assertEqual(out, OUT_3 % (log_file_path))
            mock_file.assert_called_with(log_file_path, mode="r")

    def test_simple_file(self):
        """Process a mock file with two log entries."""
        mock_file = mock_open(read_data=LOG_FILE_1)

        log_file_path = "path/to/open"
        argv = ["path/to/main", log_file_path]

        with patch("builtins.open", mock_file):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                status = app_main(argv)
                out = mock_out.getvalue()

                self.assertEqual(status, 0)
                self.assertEqual(out, OUT_1)
            mock_file.assert_called_with(log_file_path, mode="r")

    def test_simple_file_with_charm(self):
        """Process a mock file with two log entries."""
        mock_file = mock_open(read_data=LOG_FILE_1)

        log_file_path = "path/to/open"
        argv = ["path/to/main", log_file_path, "juju.cmd"]

        with patch("builtins.open", mock_file):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                status = app_main(argv)
                out = mock_out.getvalue()

                self.assertEqual(status, 0)
                self.assertEqual(out, OUT_2)
            mock_file.assert_called_with(log_file_path, mode="r")


if __name__ == "__main__":
    main()

__all__ = ["LOG_SAMPLE_1", "ToProcessLogTester"]
