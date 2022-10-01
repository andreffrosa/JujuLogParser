
SHELL := /bin/bash

#PROJECT_NAME := $(shell basename "$(PWD)")
ENV_DIR := ./.venv/ #$(PROJECT_NAME)

# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
THIS_FILE := $(lastword $(MAKEFILE_LIST))

.PHONY: init install dump clean test build

#init:
#	if [ ! -d $(ENV_DIR) ]; then python -m venv $(ENV_DIR); fi
#	if [ ! -d "./src" ]; then mkdir src; fi
#	if [ ! -d "./test" ]; then mkdir test; fi
#
#	# TODO: add extras to activate script
#
##	echo -e "\n\nPYTHONPYCACHEPREFIX=\"$(PWD)/__pycache__\"\n" >> $(ENV_DIR)/bin/activate
#	source $(ENV_DIR)/bin/activate
#	@$(MAKE) -f $(THIS_FILE) install # invoke install it needs to activate the environmet

install:
	pip install -r dev-requirements.txt

dump:
	pip freeze > dev-requirements.txt

clean:
	rm -rf __pycache__ .pytest_cache

test:
	pytest -v --cov=./src/ --cov-branch --cov-report=term-missing ./test/ 

build:
	@$(MAKE) -f $(THIS_FILE) test # invoke test
	docker build --network=host -t juju-log-parser:latest .

run:
	python ./src/main.py juju-debug.log

launch:
	docker-compose up # --build

