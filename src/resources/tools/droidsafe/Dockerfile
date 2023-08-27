FROM ecstatic/base-image

USER root
RUN wget -q -O - "https://download.bell-sw.com/pki/GPG-KEY-bellsoft" | apt-key add -
RUN echo "deb [arch=amd64] https://apt.bell-sw.com/ stable main" | tee /etc/apt/sources.list.d/bellsoft.list
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install git ant bellsoft-java8-full android-sdk

ENV JAVA_HOME=/lib/jvm/bellsoft-java8-full-amd64

WORKDIR /
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-8092744_latest.zip && \
    unzip commandlinetools-linux-8092744_latest.zip && \
    cd cmdline-tools && \
    yes | ./bin/sdkmanager --sdk_root=/lib/android-sdk --update && \
    ./bin/sdkmanager --sdk_root=/lib/android-sdk --install "platforms;android-19"
WORKDIR /
ENV ANDROID_SDK_HOME=/lib/android-sdk
ENV ANDROID_SDK_ROOT=/lib/android-sdk

WORKDIR /
RUN git clone https://github.com/MIT-PAC/droidsafe-src.git

ENV DROIDSAFE_SRC_HOME=/droidsafe-src
ENV DROIDSAFE_MEMORY=32
ENV JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8

WORKDIR /
RUN cd droidsafe-src && ant compile
WORKDIR /
