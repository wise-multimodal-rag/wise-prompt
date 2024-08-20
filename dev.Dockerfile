FROM python:3.9.13-slim

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/home/wisenut/app:${PYTHONPATH}

# Set the working directory
WORKDIR /home/wisenut/app

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

# Copy installed Python packages from the build stage
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copy necessary files and directory
COPY version_info.py .env ./
COPY ./static ./static/
COPY ./tests ./tests/
COPY ./app ./app/

# Expose the port
EXPOSE 8000

# Run the app
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/home/wisenut/app", "--reload-exclude", "*.log"]