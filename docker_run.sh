#!/bin/bash

docker build -t ctypesgen-ng .

PROJECT_PATH=$1

echo docker run -v "$PROJECT_PATH:$PROJECT_PATH" -w $PROJECT_PATH ctypesgen-ng ${@:2}
docker run -v "$PROJECT_PATH:$PROJECT_PATH" -w $PROJECT_PATH ctypesgen-ng ${@:2}