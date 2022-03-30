FROM ubuntu:20.04 as python-build
RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get update && apt-get install -y cmake z3 python3.10 python3-distutils python3-pip python3-apt python3.10-venv

FROM python-build AS dep-build

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get install --no-install-recommends --assume-yes \
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
