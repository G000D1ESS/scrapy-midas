# syntax=docker/dockerfile:1
FROM debian:bullseye

# Setup Rust
RUN apt-get update && apt-get install -y build-essential curl \
&& curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Setup Python
COPY requirements.txt .
RUN apt-get install python3-pip libssl-dev libffi-dev python-dev -y && pip3 install -r requirements.txt

# Setup project
COPY . /code/
WORKDIR /code/
