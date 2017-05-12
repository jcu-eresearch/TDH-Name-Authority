#!/bin/sh

pushd $(cd  $(dirname $0) ; pwd -P) > /dev/null
./tf_harvest.sh $@
popd > /dev/null
