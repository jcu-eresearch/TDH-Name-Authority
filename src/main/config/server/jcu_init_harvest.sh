#!/bin/sh

BASEDIR=$(cd  $(dirname $0) ; pwd -P)

cd $BASEDIR

for i in ANZSRC_FOR.json ANZSRC_SEO.json Languages.json Software_Services_TDH.json
do
    ./tf_harvest.sh ../home/harvest/$i
done
