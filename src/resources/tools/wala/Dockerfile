FROM checkmate/base-image

USER root

## package update
RUN apt-get update

## timezone
RUN apt-get install tzdata
RUN echo "America/Chicago" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get update && apt-get install -y openjdk-11-jdk openjdk-11-jre openjdk-11-jdk-headless git gcc g++ maven

WORKDIR /
RUN git clone https://github.com/amordahl/WALAInterface
WORKDIR /WALAInterface
RUN mvn compile package
