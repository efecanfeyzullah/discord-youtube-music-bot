# Start from golang base image
FROM debian:latest

WORKDIR /app

COPY . .
# Install the package
RUN apt-get update -y && apt install python3.11-venv -y
RUN python3 -m venv venv && venv/bin/pip install -r requirements.txt