## Next-generation ctypesgen tool
 
Automatically generate ctypes bindings using libclang.

The newest LLVM version which ctypegen runs fine with is `3.8.1`, therefore ctypegen is shipped as a Docker container.


## Building

```
docker build -t ctypesgen-ng .
```


## Usage

```
bash -c 'docker run -v "$PWD:$PWD" -w "$PWD" ctypesgen-ng -v'
usage: ctypesgen.py [-h] [--clang-path PATH] [--clang-flags FLAGS]
                    [--ignore-included] [--std {c89,c99,c11}]
                    LIBRARY HEADER [HEADER ...]
```

Add your own arguments instead of `-v`, according the the usage above:

```
./docker_run.sh absolutePathToProject --library library.so --headers headers.h --ignore-included --output library.py
```

How to pass clang args

```
./ctypesgen-ng.py --library libtest.so --header test1.h test2.h --clang-flags \"-Wno-error=implicit-int\" \"-std=c99\"
```
