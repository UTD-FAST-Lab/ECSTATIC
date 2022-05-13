FROM ubuntu:20.04 as python-build
SHELL ["/bin/bash", "-c"]
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y software-properties-common gcc apt-transport-https && \
    add-apt-repository -y ppa:deadsnakes/ppa &&  \
    apt-get install -y cmake z3 python3.10 python3-distutils python3-pip python3-apt python3.10-venv  \
    openjdk-8-jdk git maven wget && \
    DEBIAN_FRONTEND=noninteractive  \
    apt-get install -y --no-install-recommends --assume-yes build-essential libpq-dev unzip

FROM python-build AS dep-build

RUN python3.10 -m venv /venv
ENV PATH=/venv/bin:$PATH

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

FROM python-build AS ecstatic-build

COPY --from=dep-build /venv /venv
ENV PATH=/venv/bin:$PATH
WORKDIR /
RUN git clone --depth 1 https://github.com/amordahl/ECSTATIC.git
WORKDIR ECSTATIC
RUN python -m pip install -e .

FROM python-build AS delta-debugger-build

WORKDIR /
RUN git config --global core.eol lf && \
 git config --global core.autocrlf input

RUN git clone https://github.com/Pancax/SADeltaDebugger.git
RUN cd SADeltaDebugger/ProjectLineCounter && git checkout 7b9404ca3906822ba4cf55c1851b0cd98bc8812d && mvn install && \
    cd ../ViolationDeltaDebugger && mvn package

FROM python-build

COPY --from=delta-debugger-build /SADeltaDebugger /SADeltaDebugger
COPY --from=ecstatic-build /venv /venv
COPY --from=ecstatic-build /ECSTATIC /ECSTATIC
ENV PATH=/venv/bin:$PATH
ENV DELTA_DEBUGGER_HOME=/SADeltaDebugger
