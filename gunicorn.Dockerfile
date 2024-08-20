FROM python:3.9.13-slim as requirements

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=test,lint --with=gunicorn

FROM python:3.9.13-slim as build

# Copy requirements.txt install libraries
COPY --from=requirements /requirements.txt ./requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:3.9.13-slim as gunicorn-runtime

# Set the working directory
WORKDIR /home/wisenut/app

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/home/wisenut/app:${PYTHONPATH}

# Copy installed Python packages from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=build /usr/local/bin /usr/local/bin

# Make gunicorn worker process temp file directory
RUN mkdir -p /tmp/shm && mkdir /.local

# Copy necessary files and directory
COPY pyproject.toml version_info.py .env gunicorn.conf.py ./
COPY ./static ./static/
COPY ./app ./app/

# Expose the port
EXPOSE 8000

# Run the app: gunicorn (config: gunicorn.conf.py)
ENTRYPOINT ["gunicorn", "app.main:app"]