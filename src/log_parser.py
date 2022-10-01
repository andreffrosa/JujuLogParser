#!/usr/bin/python
"""LogParser class implementation.

This script contains a class named LogParser that processes logs
and extracts some statistics.
"""

from operator import itemgetter
from typing import Dict, Iterable, Set

# Constants
INITIAL_BASE_STATS = {"INFO": 0, "DEBUG": 0, "WARNING": 0, "ERROR": 0}

DEFAULT_TAB_SPACE = 2


class LogParser:
    """A class used to process logs and extract some statistics."""

    def __init__(self):
        """Create a new LogParser object."""
        self.global_stats = LogParser.__new_stats()
        self.stats_per_charm = {}
        self.processed_messages = set()

    @staticmethod
    def __new_stats() -> Dict[str, Dict[str, str]]:
        """Create new dictionary used to hold global and per charm statistics.

        Returns:
            Dict[str, Dict[str, str]]: dictionary created
        """
        stats = {}
        stats["all"] = INITIAL_BASE_STATS.copy()
        stats["duplicates"] = INITIAL_BASE_STATS.copy()
        return stats

    def get_global_stats(self) -> Dict[str, Dict[str, str]]:
        """
        Get the global statistics calculated.

        Returns:
            Dict[str, Dict[str, str]]: statistics calculated
        """
        return self.global_stats

    def get_stats_for_charm(self, charm_name: str) -> Dict[str, Dict[str, str]]:
        """
        Get the statistics calculated for a given charm.

        Args:
            charm_name (str): selected charm

        Returns:
            Dict[str, Dict[str, str]]: statistics calculated
        """
        return self.stats_per_charm.get(charm_name)

    def get_processed_messages(self) -> Set[str]:
        """
        Get the set of ids of the processed messages.

        Returns:
            Set[str]: Set of ids of the processed messages
        """
        return self.processed_messages

    @staticmethod
    def __update_single_stats(
        stats: Dict[str, Dict[str, str]], severity_level: str, is_duplicate: bool
    ):
        """Update the global statistics or of some charm.

        Args:
            stats (Dict[str, Dict[str, str]]): statistics to update
            severity_level (str): severity level to be updated
            is_duplicate (bool): indicates if this update was triggered by
                a duplicate log message
        """
        stats["all"][severity_level] += 1

        if is_duplicate:
            stats["duplicates"][severity_level] += 1

    @staticmethod
    def __get_message_id(charm_name: str, severity_level: str, message: str) -> str:
        """Get the unique identifier for a message.

        Args:
            charm_name (str): charm that created the log entry
            severity_level (str): log entry's severity level
            message (str): log entry's message

        Returns:
            str: the message id
        """
        return f"{severity_level} {charm_name} {message}"

    def process_log(self, log: Dict[str, str]):
        """Process a single parsed log entry.

        Args:
            log (Dict[str, str]): Log entry to process
        """
        if log is None or not isinstance(log, dict):
            raise TypeError("log is not a Dict[str, str]")
        
        charm_name, severity_level, message = itemgetter(
            "charm_name", "severity_level", "message"
        )(log)

        message_id = LogParser.__get_message_id(charm_name, severity_level, message)
        is_duplicate = message_id in self.processed_messages

        if not is_duplicate:
            self.processed_messages.add(message_id)

        # Update global statistics
        LogParser.__update_single_stats(self.global_stats, severity_level, is_duplicate)

        # Create empty statistics for the charm if they don't exist
        if charm_name not in self.stats_per_charm:
            self.stats_per_charm[charm_name] = LogParser.__new_stats()

        # Update charm's statistics
        LogParser.__update_single_stats(
            self.stats_per_charm[charm_name], severity_level, is_duplicate
        )

    def process_logs(self, logs: Iterable[Dict[str, str]]):
        """Process a batch of parsed log entries.

        Args:
            logs (Iterable[Dict[str, str]]): Batch of parsed logs to process
        """
        for log in logs:
            self.process_log(log)

    @staticmethod
    def __single_stats_to_str(
        title: str,
        stats: Dict[str, Dict[str, str]],
        padding: int = 0,
        tab_space: int = DEFAULT_TAB_SPACE,
    ):
        """Create string representation for a single statistics dictionary.

        Args:
            title (str): title of the summary
            stats (Dict[str, Dict[str, str]]): statistics to stringify
            padding (int, optional): left padding level. Defaults to 0.
            tab_space (int, optional): number of spaces per padding level.
                Default to DEFAULT_TAB_SPACE.

        Returns:
            str: generated string
        """
        tab = " " * padding * tab_space
        txt = f"{tab}{title}:\n"

        all_total = 0
        dup_total = 0

        for severity in stats["all"]:
            tab = " " * (padding + 1) * tab_space

            all_value = stats["all"][severity]
            dup_value = stats["duplicates"][severity]
            all_total += all_value
            dup_total += dup_value

            dup_str = f" ({dup_value} duplicates)" if dup_value > 0 else ""
            txt += f"{tab}{severity}: {all_value}{dup_str}\n"

        dup_str = f" ({dup_total} duplicates)" if dup_total > 0 else ""
        txt += f"{tab}TOTAL: {all_total}{dup_str}\n"

        return txt

    def __str__(self):
        """Generate a string representation for the gathered statistics."""
        n_charms = len(self.stats_per_charm)
        if n_charms == 0:
            return ""
        elif n_charms == 1:
            charm_name = list(self.stats_per_charm.keys())[0]
            return LogParser.__single_stats_to_str(charm_name, self.global_stats)
        else:
            txt = LogParser.__single_stats_to_str("Global", self.global_stats)

            txt += "\nPer Charm:\n"
            for charm_name, charm_stats in self.stats_per_charm.items():
                txt += LogParser.__single_stats_to_str(charm_name, charm_stats, 1)

            return txt


__all__ = ["DEFAULT_TAB_SPACE", "INITIAL_BASE_STATS", "LogParser"]
