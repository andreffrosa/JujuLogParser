# Define Python image to use
ARG PYTHON_IMG=python:3.10-alpine
# ARG PYTHON_IMG=python:3.8-slim

# Define App configurations
ARG APP_NAME=JujuLogParser
ARG APP_VERSION=1.0.0

###############################################################################

# Create base image stage
FROM $PYTHON_IMG AS base

# Export App configurations into environment variables
ARG APP_NAME
ARG APP_VERSION
ENV APP_NAME=$APP_NAME
ENV APP_VERSION=$APP_VERSION

# Prevent Python from generating .pyc files in the container
# For more info, please refer to https://stackoverflow.com/questions/59732335/is-there-any-disadvantage-in-using-pythondontwritebytecode-in-docker
ENV PYTHONDONTWRITEBYTECODE=1

# Define __pycache__ location
ENV PYTHONPYCACHEPREFIX="/$APP_NAME/__pycache__"

# Turn off buffering for easier container logging
# For more info, please refer to https://stackoverflow.com/questions/59812009/what-is-the-use-of-pythonunbuffered-in-docker-file
ENV PYTHONUNBUFFERED=1

# Define Python virtual environment future location
ENV VIRTUAL_ENV="/$APP_NAME/.venv"

WORKDIR "/$APP_NAME"

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser "/$APP_NAME"
USER appuser

# Upgrade pip
#RUN python -m pip install --upgrade pip

###############################################################################

# Build stage
FROM base AS builder

# Create Python virtual environment
RUN python -m venv $VIRTUAL_ENV

# Activate virtual environment
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install wheel
RUN python -m pip install wheel

# Install pip requirements
COPY prod-requirements.txt .
RUN python -m pip install -r prod-requirements.txt

###############################################################################

# Final stage
FROM base

# Copy the virtual environment from the build stage
COPY --from=builder "$VIRTUAL_ENV" "$VIRTUAL_ENV"

# Activate virtual environment
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy Python source files to workdir
COPY ./src .

# Define image entrypoint
ENTRYPOINT ["python", "main.py"]
