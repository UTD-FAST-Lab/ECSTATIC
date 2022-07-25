FROM ubuntu:20.04 as wala-install

USER root
## timezone
RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Chicago /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

## package update
RUN apt-get update && apt-get install -y git openjdk-11-jdk maven

WORKDIR /
RUN git clone https://github.com/egsch/WalaJSCallgraph --depth 1
WORKDIR /WalaJSCallgraph
ADD "https://api.github.com/repos/egsch/walajscallgraph/commits?per_page=1" latest_commit
RUN git pull
RUN mvn compile package

FROM ecstatic/base-image

RUN apt-get install -y openjdk-11-jdk
COPY --from=wala-install /WalaJSCallgraph /WalaJSCallgraph
