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

FROM python-build AS checkmate-build

COPY --from=dep-build /venv /venv

WORKDIR /
COPY . /checkmate

# Copy SSH key for git private repos
RUN if [ -e "/checkmate/.ssh/id_docker_key" ]; then \
    mkdir -p -m 0700 /root/.ssh && mv /checkmate/.ssh/id_docker_key /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    chmod 600 /root/.ssh/id_docker_key && \
    echo "Host github.com" > /root/.ssh/config && \
    echo " HostName github.com" >> /root/.ssh/config && \
    echo " IdentityFile /root/.ssh/id_docker_key" >> /root/.ssh/config && \
    chmod 600 /root/.ssh/config; fi

# Use git with SSH instead of https
# RUN echo "[url \"git@github.com:\"]\n\tinsteadOf = https://github.com/" >> /root/.gitconfig

# Skip Host verification for git
#RUN echo "StrictHostKeyChecking no " >> /root/.ssh/config

FROM python-build AS delta-debugger-build

COPY --from=checkmate-build /root/.ssh /root/.ssh
WORKDIR /
RUN git clone git@github.com:Pancax/SADeltaDebugger.git
RUN cd SADeltaDebugger/ProjectLineCounter && mvn install && \
    cd ../ViolationDeltaDebugger && mvn package

FROM python-build

COPY --from=delta-debugger-build /SADeltaDebugger /SADeltaDebugger
COPY --from=dep-build /venv /venv
COPY --from=checkmate-build /checkmate /checkmate
COPY --from=checkmate-build /root/.ssh /root/.ssh

WORKDIR /checkmate

ENV PATH=/venv/bin:$PATH
RUN python -m pip install -e .
WORKDIR /
