FROM python:3.9.13-slim

# Set environment variables
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/home/wisenut/app:${PYTHONPATH}

# Install libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    vim \
    tzdata

# Set the working directory
WORKDIR /home/wisenut/app

# Copy necessary files and directory
COPY pyproject.toml poetry.lock version_info.py .env gunicorn.conf.py ./
COPY ./static ./static/
COPY ./app ./app/

# Install Requirements
RUN pip install poetry
RUN poetry install --no-root

# Expose the port
EXPOSE 8000

# Run the app
CMD ["poetry", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]