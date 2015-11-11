#!/bin/bash

DCOS_SERV="mesos marathon kubernetes etcd zookeeper swarm dcos-cli"

export HUB_USER=mesostest

TOP_DIR=`pwd`

for i in $DCOS_SERV
do
  cd $TOP_DIR/$i 
  ./build.sh
  cd $TOP_DIR
done

IMAGES="$HUB_USER/mesos-master $HUB_USER/mesos-slave $HUB_USER/swarm $HUB_USER/zookeeper $HUB_USER/etcd $HUB_USER/km $HUB_USER/kubelet $HUB_USER/marathon"

for i in $IMAGES
do
    sudo docker push $i
done

