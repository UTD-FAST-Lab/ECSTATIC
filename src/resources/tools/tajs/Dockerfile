FROM ecstatic/base-image

USER root

RUN apt-get -y update
RUN apt-get -y install openjdk-8-jdk git ant nodejs

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/

WORKDIR /
RUN git clone https://github.com/cs-au-dk/TAJS.git
WORKDIR /TAJS/
RUN git submodule update --init --recursive
RUN ant