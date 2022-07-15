FROM ecstatic/base-image

USER root

RUN apt-get -y update && apt-get -y install openjdk-8-jdk git ant nodejs npm

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/

WORKDIR /
RUN git clone https://github.com/egsch/TAJS.git
WORKDIR /TAJS/
RUN git submodule update --init --recursive && ant
WORKDIR /