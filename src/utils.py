#!/usr/bin/python
"""This script contains a set of utility functions."""

from typing import Dict, Optional

from parse import parse as parse_string


def unformat(string: str, pattern: str) -> Optional[Dict[str, str]]:
    """Parse a string into a dictionary according to a pattern.

    Parse a string into a dictionary according to the matches with
    the provided pattern, i.e., does the inverse of format().

    Args:
        string (str): string to parse
        pattern (str): pattern to match string against

    Raises:
        TypeError: string cannot be None
        TypeError: pattern cannot be None

    Returns:
        Optional[Dict]: dictionary containing the found matches
            or None if there was no match
    """
    if string is None:
        raise TypeError("string cannot be None")

    if pattern is None:
        raise TypeError("pattern cannot be None")

    result = parse_string(pattern, string, evaluate_result=True)

    return result.named if result is not None else None


__all__ = ["unformat"]
