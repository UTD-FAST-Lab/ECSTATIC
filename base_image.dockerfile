FROM ubuntu:20.04 as python-build
SHELL ["/bin/bash", "-c"]
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y software-properties-common gcc apt-transport-https && \
    add-apt-repository -y ppa:deadsnakes/ppa &&  \
    apt-get install -y cmake z3 python3.10 python3-distutils python3-pip python3-apt python3.10-venv  \
    openjdk-11-jdk openjdk-11-jre openjdk-11-jdk-headless git maven wget && \
    DEBIAN_FRONTEND=noninteractive  \
    apt-get install -y --no-install-recommends --assume-yes build-essential libpq-dev unzip


FROM python-build AS dep-build

RUN python3.10 -m venv /venv
ENV PATH=/venv/bin:$PATH

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

FROM python-build

COPY --from=dep-build /venv /venv

WORKDIR /
COPY . /checkmate
WORKDIR /checkmate

ENV PATH=/venv/bin:$PATH
RUN python -m pip install -e .
WORKDIR /

# Copy SSH key for git private repos
ADD .ssh/id_docker_key /root/.ssh/id_docker_key
RUN chmod 600 /root/.ssh/id_docker_key && \
    echo "Host github.com" > /root/.ssh/config && \
    echo " HostName github.com" >> /root/.ssh/config && \
    echo " IdentityFile /root/.ssh/id_docker_key" >> /root/.ssh/config && \
    echo "StrictHostKeyChecking no" >> /root/.ssh/config && \
    chmod 600 /root/.ssh/config

# Use git with SSH instead of https
# RUN echo "[url \"git@github.com:\"]\n\tinsteadOf = https://github.com/" >> /root/.gitconfig

# Skip Host verification for git
#RUN echo "StrictHostKeyChecking no " >> /root/.ssh/config
