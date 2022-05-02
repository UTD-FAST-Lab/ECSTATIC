FROM ubuntu:20.04 as wala-install

USER root
## timezone
RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Chicago /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

## package update
RUN apt-get update && apt-get install -y git openjdk-8-jdk maven

WORKDIR /
RUN git clone https://github.com/amordahl/WALAInterface --depth 1
WORKDIR /WALAInterface
RUN mvn compile package

FROM checkmate/base-image

COPY --from=wala-install /WALAInterface /WALAInterface