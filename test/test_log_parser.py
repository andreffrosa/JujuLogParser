"""This file contains the implementation of a tester class for log_parser.py."""

from unittest import TestCase, main

from log_parser import LogParser


# Auxiliary Function
def new_log(
    unit: str = "",
    hour: str = "00",
    minutes: str = "00",
    seconds: str = "00",
    severity_level: str = "DEBUG",
    charm_name: str = "DEFAULT_CHARM",
    message: str = "EMPTY MESSAGE",
):
    return {
        "unit": unit,
        "hour": hour,
        "minutes": minutes,
        "seconds": seconds,
        "severity_level": severity_level,
        "charm_name": charm_name,
        "message": message,
    }


# Constants
SAMPLE_LOGS = [
    new_log("unit-1", severity_level="INFO", charm_name="juju.network"),
    new_log("unit-2", severity_level="ERROR", charm_name="juju.network"),
    new_log("unit-3", severity_level="WARNING", charm_name="juju.api"),
]


class LogParserTester(TestCase):
    """Tester class used for testing the LogParser class."""

    #    @staticmethod
    #    def __create_log(
    #        unit: str = "",
    #        hour: str = "00",
    #        minutes: str = "00",
    #        seconds: str = "00",
    #        severity_level: str = "DEBUG",
    #        charm_name: str = "DEFAULT_CHARM",
    #        message: str = "EMPTY MESSAGE",
    #    ):
    #        return {
    #            "unit": unit,
    #            "hour": hour,
    #            "minutes": minutes,
    #            "seconds": seconds,
    #            "severity_level": severity_level,
    #            "charm_name": charm_name,
    #            "message": message,
    #        }

    def test_none_log(self):
        """Raise TypeError on None log."""
        log_parser = LogParser()
        self.assertRaises(TypeError, log_parser.process_log, None)

    def test_wrong_type_log(self):
        """Raise TypeError on log which is not of type Dict[str, str]."""
        log_parser = LogParser()
        self.assertRaises(TypeError, log_parser.process_log, "log")

    def test_single_log(self):  # name?
        """Process a single valid log entry."""
        log = SAMPLE_LOGS[0]
        expected = LogParser._LogParser__new_stats()
        expected["all"][log["severity_level"]] += 1

        log_parser = LogParser()
        log_parser.process_log(log)

        global_stats = log_parser.get_global_stats()
        charm_stats = log_parser.get_stats_for_charm(log["charm_name"])

        self.assertDictEqual(global_stats, expected)
        self.assertDictEqual(charm_stats, expected)

    def test_multiple_diff_logs(self):  # name?
        """Process a multiple valid different log entries."""
        global_expected = LogParser._LogParser__new_stats()
        global_expected["all"]["INFO"] = 1
        global_expected["all"]["ERROR"] = 1
        global_expected["all"]["WARNING"] = 1

        # separate into different tests?
        juju_network_expected = LogParser._LogParser__new_stats()
        juju_network_expected["all"]["INFO"] = 1
        juju_network_expected["all"]["ERROR"] = 1

        # separate into different tests?
        juju_api_expected = LogParser._LogParser__new_stats()
        juju_api_expected["all"]["WARNING"] = 1

        log_parser = LogParser()

        for log in SAMPLE_LOGS:
            log_parser.process_log(log)

        global_stats = log_parser.get_global_stats()
        self.assertDictEqual(global_stats, global_expected)

        juju_network_stats = log_parser.get_stats_for_charm("juju.network")
        self.assertDictEqual(juju_network_stats, juju_network_expected)

        juju_api_stats = log_parser.get_stats_for_charm("juju.api")
        self.assertDictEqual(juju_api_stats, juju_api_expected)

    def test_multiple_logs_with_duplicates(self):  # name?
        """Process a multiple valid log entries with duplicates."""
        logs = [log for log in SAMPLE_LOGS]
        logs.append(SAMPLE_LOGS[0])

        global_expected = LogParser._LogParser__new_stats()
        global_expected["all"]["INFO"] = 2
        global_expected["all"]["ERROR"] = 1
        global_expected["all"]["WARNING"] = 1
        global_expected["duplicates"]["INFO"] = 1

        # separate into different tests?
        juju_network_expected = LogParser._LogParser__new_stats()
        juju_network_expected["all"]["INFO"] = 2
        juju_network_expected["all"]["ERROR"] = 1
        juju_network_expected["duplicates"]["INFO"] = 1

        # separate into different tests?
        juju_api_expected = LogParser._LogParser__new_stats()
        juju_api_expected["all"]["WARNING"] = 1

        log_parser = LogParser()

        for log in logs:
            log_parser.process_log(log)

        global_stats = log_parser.get_global_stats()
        self.assertDictEqual(global_stats, global_expected)

        juju_network_stats = log_parser.get_stats_for_charm("juju.network")
        self.assertDictEqual(juju_network_stats, juju_network_expected)

        juju_api_stats = log_parser.get_stats_for_charm("juju.api")
        self.assertDictEqual(juju_api_stats, juju_api_expected)

    # Necessário testar o process_logs ? --> é só um ciclo a chamar o process_log para cada log


if __name__ == "__main__":
    main()

__all__ = ["LogParserTester", "SAMPLE_LOGS", "new_log"]
