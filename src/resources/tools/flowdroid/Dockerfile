FROM checkmate/base-image AS setup-deps

USER root
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install git maven

FROM checkmate/base-image AS flowdroid-build
WORKDIR /
RUN git clone https://github.com/secure-software-engineering/FlowDroid.git && \
    cd FlowDroid && git checkout 72734bd629dfae2aacaf6e6973abfe73d035c979 && mvn clean compile package -DskipTests


FROM checkmate/base-image AS aql-build
WORKDIR /
RUN git clone https://github.com/amordahl/AQL-System.git && cd AQL-System && mvn clean compile package
