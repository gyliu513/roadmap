#!/bin/bash

MESOS_MASTER=http://ma1demo1:5050
MARATHON_MASTER=http://ma1demo1:8080

TOP_DIR=`pwd`

curl -O https://downloads.mesosphere.io/dcos-cli/install.sh
bash install.sh $TOP_DIR $MARATHON_MASTER

source $TOP_DIR/bin/env-setup && dcos help
dcos config set core.mesos_master_url $MESOS_MASTER
dcos config set marathon.url $MARATHON_MASTER

