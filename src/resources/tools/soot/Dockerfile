FROM ubuntu:20.04 as soot-build
SHELL ["/bin/bash", "-c"]

USER root

## timezone \
RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Chicago /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

## package update
RUN apt-get update && apt-get upgrade -y && apt-get install -y apt-utils git openjdk-8-jdk maven


WORKDIR /
RUN git clone https://github.com/amordahl/SootInterface.git --depth 1
WORKDIR /SootInterface
RUN mvn compile package
WORKDIR /

FROM checkmate/base-image

COPY --from=soot-build /SootInterface /SootInterface
