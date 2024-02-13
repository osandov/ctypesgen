FROM ubuntu:24.04

ENV DEBIAN_FRONTEND noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip \
    python3-clang python3-autopep8 clang llvm gcc-mingw-w64

RUN mkdir /app
COPY ctypesgen.py /app
COPY run_tests.sh /app
COPY tests /app/tests

WORKDIR /app

RUN CLANG_LIBRARY_PATH=$(llvm-config --libdir) && \
    echo "CLANG_LIBRARY_PATH=${CLANG_LIBRARY_PATH}" >> ~/.profile

RUN CLANG_LIBRARY_PATH=$(llvm-config --libdir) && ln -s $CLANG_LIBRARY_PATH/libclang-17.so.1 /usr/lib/libclang-17.so

RUN ./run_tests.sh

ENTRYPOINT ["/app/ctypesgen.py"]
