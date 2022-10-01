"""This file contains the implementation of a tester class for log_parser.py."""

from unittest import TestCase, main

from utils import unformat

# Constants
DEFAULT_LOG_LINE_FORMAT = (
    "{unit}: {hour}:{minutes}:{seconds} {severity_level} {charm_name} {message}\n"
)

TEST_STR_1 = "Hello, my name is John and I'm 25 years old."

TEST_PATTERN_1 = "Hello, my name is {name} and I'm {age} years old."


class UnformatTester(TestCase):
    """Tester class used for testing the unformat utility function."""

    # Should I use instance vars or instantiate inside the functions?

    def test_none_string_exception(self):
        """Raise TypeError when the string parameter is None."""
        kwargs = {"string": None, "pattern": ""}
        self.assertRaises(TypeError, unformat, **kwargs)

    def test_none_pattern_exception(self):
        """Raise TypeError when the pattern parameter is None."""
        kwargs = {"string": "", "pattern": None}
        self.assertRaises(TypeError, unformat, **kwargs)

    def test_none_params_exception(self):  # unnecessary?
        """Raise TypeError when both parameters are None."""
        kwargs = {"string": None, "pattern": None}
        self.assertRaises(TypeError, unformat, **kwargs)

    def test_empty_string(self):
        """Return None when string parameter is empty."""
        result = unformat("", TEST_PATTERN_1)
        self.assertIsNone(result)

    def test_empty_pattern(self):
        """Return None when pattern parameter is empty."""
        result = unformat(TEST_STR_1, "")
        self.assertIsNone(result)

    def test_4_unformat(self):  # What name give this?
        """TODO."""
        expected = {"name": "John", "age": "25"}
        result = unformat(TEST_STR_1, TEST_PATTERN_1)
        self.assertDictEqual(result, expected)

    def test_no_match(self):
        """Return None when there is not a match between the string and the pattern."""
        pattern = "Today it was {temperature}ºC!"  # Convert to const?
        result = unformat(TEST_STR_1, pattern)
        self.assertIsNone(result)

    def test_6_unformat(self):  # What name give this?
        """TODO."""
        string = "machine-0: 01:56:55 INFO juju.cmd running jujud [2.8.1 0 16439b3d1c528b7a0e019a16c2122ccfcf6aa41f gc go1.14.4]\n"  # Convert to const?
        result = unformat(string, DEFAULT_LOG_LINE_FORMAT)
        expected = {
            "unit": "machine-0",
            "hour": "01",
            "minutes": "56",
            "seconds": "55",
            "severity_level": "INFO",
            "charm_name": "juju.cmd",
            "message": "running jujud [2.8.1 0 16439b3d1c528b7a0e019a16c2122ccfcf6aa41f gc go1.14.4]",
        }
        self.assertDictEqual(result, expected)


if __name__ == "__main__":
    main()

__all__ = ["DEFAULT_LOG_LINE_FORMAT", "TEST_PATTERN_1", "TEST_STR_1", "UnformatTester"]
