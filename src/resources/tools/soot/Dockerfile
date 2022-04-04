FROM checkmate/base-image

USER root

## package update
RUN apt-get update

## timezone
 RUN apt-get install tzdata
 RUN echo "America/Chicago" > /etc/timezone
 RUN dpkg-reconfigure -f noninteractive tzdata

WORKDIR /
RUN git clone https://github.com/amordahl/SootInterface.git
WORKDIR /SootInterface
RUN mvn compile package
WORKDIR /
