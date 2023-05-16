FROM ecstatic/base-image AS setup-deps
ARG platform

USER root
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install git maven openjdk-8-jdk android-sdk

ENV JAVA_HOME=/lib/jvm/java-8-openjdk-$platform
WORKDIR /
RUN git clone https://github.com/secure-software-engineering/FlowDroid.git && \
    cd FlowDroid && git checkout 72734bd629dfae2aacaf6e6973abfe73d035c979 && mvn clean compile package -DskipTests

WORKDIR /
RUN git clone https://github.com/amordahl/AQL-System.git && cd AQL-System && git checkout no_gui && \
    mvn clean compile package -DskipTests && \
    mkdir -p target/build/data/storage && mkdir -p target/build/answers
WORKDIR /

RUN wget https://dl.google.com/android/repository/commandlinetools-linux-8092744_latest.zip && \
    unzip commandlinetools-linux-8092744_latest.zip && \
    cd cmdline-tools && \
    yes | ./bin/sdkmanager --sdk_root=/lib/android-sdk --update && \
    ./bin/sdkmanager --sdk_root=/lib/android-sdk --install "platforms;android-25"

WORKDIR /
ENV ANDROID_SDK_ROOT=/lib/android-sdk
ENV ANDROID_SDK_HOME=/lib/android-sdk