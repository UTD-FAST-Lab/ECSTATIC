FROM ubuntu:20.04

ARG PHASAR=/phasar
ARG PHASAR_INSTALL_DIR=/usr/local/phasar
ARG LLVM_INSTALL_DIR=/usr/local/llvm-12
ADD include/llvm-12 ${LLVM_INSTALL_DIR}

RUN mkdir -p ${PHASAR}

ENV CC="/usr/local/llvm-12/bin/clang" \
CXX="/usr/local/llvm-12/bin/clang++" \
CFLAGS="" \
CXXFLAGS=""

RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive TZ="America/New_York" apt-get -y install tzdata && \
apt-get install wget sudo -y && \
apt-get install git make cmake -y && \
apt-get install zlib1g-dev sqlite3 libsqlite3-dev bear python3 doxygen graphviz python3-pip libxml2 libxml2-dev libncurses5-dev libncursesw5-dev swig build-essential g++ cmake libz3-dev libedit-dev python3-sphinx libomp-dev libcurl4-openssl-dev ninja-build -y && \
apt-get install libboost-all-dev -y

RUN git clone https://github.com/secure-software-engineering/phasar.git ${PHASAR}
WORKDIR ${PHASAR}
RUN git checkout aed66c04e6dbb3f6ef1bed4ad69b29aa0017bd9a
RUN git submodule init && git submodule update

RUN mkdir -p ${PHASAR}/build
WORKDIR ${PHASAR}/build
RUN export PATH=${LLVM_INSTALL_DIR}:$$PATH
RUN cmake -G Ninja -DCMAKE_BUILD_TYPE=Release ..
RUN cmake --build .
RUN cmake -DCMAKE_INSTALL_PREFIX=${PHASAR_INSTALL_DIR} -P cmake_install.cmake
RUN ldconfig
RUN ${PHASAR}/utils/setEnvironmentVariables.sh ${LLVM_INSTALL_DIR} ${PHASAR_INSTALL_DIR}

RUN mkdir -p ${PHASAR}/external/json/build
WORKDIR ${PHASAR}/external/json/build
RUN cmake .. && make -j20 && make install

RUN mkdir -p ${PHASAR}/external/json-schema-validator/build
WORKDIR ${PHASAR}/external/json-schema-validator/build
RUN cmake .. && make -j20 && make install
RUN ldconfig

RUN pip3 install wllvm

ENV LLVM_COMPILER=clang \
    LLVM_COMPILER_PATH=${LLVM_INSTALL_DIR}/bin

WORKDIR $PHASAR
