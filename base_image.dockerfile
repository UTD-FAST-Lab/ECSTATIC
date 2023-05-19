FROM ubuntu:20.04 as python-build
SHELL ["/bin/bash", "-c"]
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y software-properties-common gcc apt-transport-https && \
    add-apt-repository -y ppa:deadsnakes/ppa &&  \
    apt-get install -y cmake z3 python3.10 python3.10-dev python3-distutils python3-pip python3-apt python3.10-venv pkg-config libcairo2-dev libjpeg-dev libgif-dev \
    openjdk-8-jdk git maven wget && \
    DEBIAN_FRONTEND=noninteractive  \
    apt-get install -y --no-install-recommends --assume-yes build-essential libpq-dev unzip
RUN apt-get update && apt-get install -y nodejs npm

FROM python-build AS ecstatic-build

WORKDIR /
RUN python3.10 -m venv /venv
ENV PATH=/venv/bin:$PATH
ADD requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
ADD . /ECSTATIC
WORKDIR ECSTATIC
RUN python -m pip install -e .

FROM python-build AS delta-debugger-build
WORKDIR /
RUN git config --global core.eol lf && \
 git config --global core.autocrlf input

ADD "https://api.github.com/repos/pancax/SADeltaDebugger/commits?per_page=1" latest_debug
RUN git clone https://github.com/Pancax/SADeltaDebugger.git
WORKDIR /SADeltaDebugger
RUN cd ProjectLineCounter/ &&  mvn install && \
    cd ../ViolationDeltaDebugger/ && mvn package -DskipTests
WORKDIR /
FROM python-build
COPY --from=delta-debugger-build /SADeltaDebugger /SADeltaDebugger
COPY --from=ecstatic-build /venv /venv
COPY --from=ecstatic-build /ECSTATIC /ECSTATIC
ENV PATH=/venv/bin:$PATH
ENV DELTA_DEBUGGER_HOME=/SADeltaDebugger
