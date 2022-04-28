FROM checkmate/base-image AS setup-deps

USER root
RUN wget -q -O - "https://download.bell-sw.com/pki/GPG-KEY-bellsoft" | apt-key add -
RUN echo "deb [arch=amd64] https://apt.bell-sw.com/ stable main" | tee /etc/apt/sources.list.d/bellsoft.list
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install git maven bellsoft-java8-full android-sdk

ENV JAVA_HOME=/lib/jvm/bellsoft-java8-full-amd64
WORKDIR /
RUN git clone https://github.com/secure-software-engineering/FlowDroid.git && \
    cd FlowDroid && git checkout 72734bd629dfae2aacaf6e6973abfe73d035c979 && mvn clean compile package -DskipTests

WORKDIR /
RUN git clone https://github.com/amordahl/AQL-System.git && cd AQL-System && mvn clean compile package -DskipTests && \
    mkdir -p target/build/data/storage && mkdir -p target/build/answers
WORKDIR /

RUN wget https://dl.google.com/android/repository/commandlinetools-linux-8092744_latest.zip && \
    unzip commandlinetools-linux-8092744_latest.zip && \
    cd cmdline-tools && \
    yes | ./bin/sdkmanager --sdk_root=/lib/android-sdk --update && \
    ./bin/sdkmanager --sdk_root=/lib/android-sdk --install "platforms;android-25"
WORKDIR /