FROM python:3.9.13-slim AS poetry-base

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.8.3 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV APP_HOME=/home/wisenut/app


# `builder-base` stage is used to build deps + create our virtual environment
FROM poetry-base AS builder-base

# Install libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    vim \
    jq \
    curl \
    git \
    tzdata \
    net-tools \
    iproute2 \
    htop \
    build-essential \
    strace  \
    apache2-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install


# `development` image is used during development / testing
FROM poetry-base AS development

# Setting home directory and user name
ENV APP_HOME=/home/wisenut/app

# Set the working directory
WORKDIR $APP_HOME

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=$APP_HOME:${PYTHONPATH}

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY pyproject.toml poetry.lock ./

# Copy necessary files and directory
COPY version_info.py .env ./
COPY ./static ./static/
COPY ./tests ./tests/
COPY ./app ./app/

# Expose the port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/home/wisenut/app", "--reload-exclude", "*.log"]