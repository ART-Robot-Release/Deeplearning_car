#!/bin/bash
MOD_NAME="racingcar"
TAR="$MOD_NAME.tar.gz"
STATIC="static-$MOD_NAME.tar.gz"
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export PATH=/home/fis/node/v8/bin:/home/fis/v8/npm/bin:/home/fis/npm/bin:$NODEJS_BIN_V8:$PATH
npm install --registry=http://registry.npm.baidu-int.com

mkdir /output
echo "build end"