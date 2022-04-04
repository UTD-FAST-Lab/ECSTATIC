FROM ubuntu:20.04 as python-build
SHELL ["/bin/bash", "-c"]
RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y software-properties-common gcc apt-transport-https && \
    add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get install -y cmake z3 python3.10 python3-distutils python3-pip python3-apt python3.10-venv openjdk-11-jdk openjdk-11-jre openjdk-11-jdk-headless git maven wget

FROM python-build AS dep-build

RUN apt-get update -y \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends --assume-yes \
      build-essential \
      libpq-dev

RUN python3.10 -m venv /venv
ENV PATH=/venv/bin:$PATH

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python-build

COPY --from=dep-build /venv /venv

ADD . /checkmate
WORKDIR /checkmate

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m pip install -r requirements.txt
RUN python -m pip install -e .
WORKDIR /
