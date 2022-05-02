FROM ubuntu:20.04 as wala-install

USER root
## package update
RUN apt-get update && apt-get install -y openjdk-11-jdk

## timezone
RUN apt-get install tzdata
RUN echo "America/Chicago" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get update && apt-get install -y gcc g++

WORKDIR /
RUN git clone https://github.com/amordahl/WALAInterface --depth 1
WORKDIR /WALAInterface
RUN mvn compile package

FROM checkmate/base-image

COPY --from=wala-install /WALAInterface /WALAInterface