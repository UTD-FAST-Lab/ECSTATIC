FROM checkmate/base-image

USER root

## package update
RUN apt-get update

## timezone
RUN apt-get install tzdata
RUN echo "America/Chicago" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get update && apt-get install -y gcc g++

WORKDIR /
RUN git clone https://github.com/amordahl/WALAInterface
WORKDIR /WALAInterface
RUN mvn compile package
