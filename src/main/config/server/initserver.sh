#!/bin/sh

sleep 120
wget --header="Host: $1" http://localhost:$2/$3/default/home -O /dev/null
