## Next-generation ctypesgen tool
 
Automatically generate ctypes bindings using libclang.


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
bash -c 'docker run -v "$PWD:$PWD" -w "$PWD" ctypesgen-ng <add arguments here>'
```

