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
RUN git clone https://github.com/amordahl/WALAInterface
WORKDIR /WALAInterface
RUN git checkout developer_config_space
RUN mvn compile package

FROM ecstatic/base-image

RUN apt-get install -y openjdk-11-jdk
COPY --from=wala-install /WALAInterface /WALAInterface