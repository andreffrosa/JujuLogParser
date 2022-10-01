# Juju Log Parser

## Project Description

The objective of this project was to develop a small command line tool that processes log files produced by Juju and extracts some statistics. Each log entry in these files is comprised of a unit name, a timestamp, a severity level, and the log message itself. Lines that are not prefixed with a unit name are ignored. The tool accepts two parameters: the filename of the log file to process (mandatory) and the selected charm name to consider (optional). If the charm name is specified, the tool ignores the logs of the other charms. 
Usage syntax:
```
$ ./main.py FILE [CHARM]
```


### Docker

In alternative to running natively, you can use Docker.

Build image:
```
docker build --network=host --rm --pull -f "./Dockerfile" -t juju-log-parser:latest .
```

Run container:
```
docker run --rm -it \
--mount type=bind,source=LOCAL_FILE,target=FILE \
juju-log-parser:latest FILE [CHARM]

```


## Project Architecture

The project was developed in Python 3 and is comprised of three files: [main.py](./src/main.py), [utils.py](./src/utils.py), and [log_parser.py](./src/log_parser.py).

The [main.py](./src/main.py) file contains the entry point of the tool. Overall, it creates a generator of parsed log entries from the specified file. This generator only produces logs that are prefixed with a unit name and, when the optional parameter is specified, logs produced by the selected charm. This generator is then passed as to a LogParser object (described later) to extract the statistics. Lastly, the tool prints a summary of the gathered statistics. This print starts with the number of messages for each severity type and in total across all charms and then is followed by a list of the same information for each charm. The number of messages of a given type is followed by the number of duplicates of that message inside parenthesis. When there are no duplicates, this information is omitted. Example of the output:
```
$ ./main.py juju-debug.log juju.network
juju.network:
  INFO: 0
  DEBUG: 73 (65 duplicates)
  WARNING: 0
  ERROR: 0
  TOTAL: 73 (65 duplicates)
```

The [utils.py](./src/utils.py) file contains one simple auxiliary function, called unformat, that parses a string into a dictionary given a pattern to match the string against. This function is used to parse the log lines so that they can be easily queried by the tool during processing. 

Finally, the [log_parser.py](./src/log_parser.py) file contains the implementation of a LogParser class that covers the core functionality of this tool. This class has a method called process_logs that receives a generator of valid logs as parameter. By passing a generator as parameter, the LogParser implementation and testing is decoupled from reading files, becoming easier to test this class and to modify the tool to fetch logs from other sources (e.g., the network).  This method makes use of the process_log method that verifies if it is a duplicated log and updates the global statistics and the statistics of the charm that created the current log.

