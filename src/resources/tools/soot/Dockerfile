FROM checkmate/base-image

USER root

## package update
RUN apt-get update

## timezone
 RUN apt-get install tzdata
 RUN echo "America/Chicago" > /etc/timezone
 RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get install -y openjdk-11-jdk openjdk-11-jre openjdk-11-jdk-headless wget

RUN mkdir /soot
WORKDIR /soot
RUN wget https://repo1.maven.org/maven2/org/soot-oss/soot/4.3.0/soot-4.3.0-jar-with-dependencies.jar
