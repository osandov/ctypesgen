# In order to avoid issue https://github.com/KhronosGroup/SPIR/issues/78
# GCC version 7 is required; Ubuntu 20.04 (focal) is the last version to
# provide gcc-7 out of the box.
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y python2 perl cmake ninja-build wget \
                       bison flex libexplain-dev autoconf automake libtool \
                       m4 zlib1g-dev libtinfo-dev libc6-dev g++-7 pep8

ENV LLVM_VER=3.8.1

# Download and install LLVM+Clang ${LLVM_VER} (https://stackoverflow.com/a/53159552)
RUN cd /tmp && wget -O llvm.tar.xz https://releases.llvm.org/${LLVM_VER}/llvm-${LLVM_VER}.src.tar.xz && \
	tar -xJf llvm.tar.xz && mkdir /opt/llvm-${LLVM_VER} && mv llvm-${LLVM_VER}.src/* /opt/llvm-${LLVM_VER} && \
	wget -O clang.tar.xz https://releases.llvm.org/${LLVM_VER}/cfe-${LLVM_VER}.src.tar.xz && tar -xJf clang.tar.xz && \
	mkdir /opt/llvm-${LLVM_VER}/tools/clang && mv cfe-${LLVM_VER}.src/* /opt/llvm-${LLVM_VER}/tools/clang
WORKDIR /opt/llvm-${LLVM_VER}
RUN mkdir build && cd build && cmake -G "Ninja" .. \
	-DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_RTTI=ON -DCMAKE_CXX_COMPILER=g++-7 -DLLVM_TARGETS_TO_BUILD=host && \ 
	ninja
RUN cd build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/llvm -P cmake_install.cmake 	
ENV PATH="/usr/local/llvm/bin:${PATH}"

# Link the libraries for LLVM+Clang
RUN cd /usr/local/llvm && echo /usr/local/llvm/lib > /etc/ld.so.conf.d/libs.conf && ldconfig

RUN mkdir /app
COPY ctypesgen.py /app
COPY run_tests.sh /app
COPY tests /app/tests

ENV PYTHONPATH=/opt/llvm-${LLVM_VER}/tools/clang/bindings/python

WORKDIR /app
RUN ./run_tests.sh

ENTRYPOINT ["/app/ctypesgen.py"]
