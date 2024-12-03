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
RUN apt-get update && apt-get install --no-install-recommends -y build-essential

# Install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev --without test,lint,gunicorn


# `production` image used for runtime
FROM poetry-base AS production

# Setting home directory and user name
ENV APP_HOME=/home/wisenut/app
ENV GROUP_NAME=wisenut
ENV APP_USER=wisenut

# Create a non-root user and group
RUN groupadd -r $GROUP_NAME && useradd -r -g $GROUP_NAME -d $APP_HOME $APP_USER

# Set the working directory
WORKDIR $APP_HOME
RUN chown -R $APP_USER:$GROUP_NAME $APP_HOME

# Switch to the non-root user
USER $APP_USER

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY pyproject.toml version_info.py .env ./
COPY ./static ./static/
COPY ./app ./app/

# Expose the port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/home/wisenut/app", "--reload-exclude", "*.log"]