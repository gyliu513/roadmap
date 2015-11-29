#!/bin/bash

if [ $# -eq 2 ] ; then
  TAG=$1
else
  TAG=swarm
fi

GO_URL=https://storage.googleapis.com/golang/go1.5.1.linux-amd64.tar.gz
TOP_DIR=`pwd`

sudo apt-get install -y wget

#Install Go 
if  [ ! -d $TOP_DIR/go ] ; then
  wget $GO_URL
  tar zxvf $(basename $GO_URL)
fi


export GOROOT=$TOP_DIR/go
export GOPATH=$TOP_DIR/godep
export PATH=$GOROOT/bin:$PATH

mkdir -p $GOPATH

go get github.com/tools/godep

mkdir -p $GOPATH/src/github.com/docker
cd $GOPATH/src/github.com/docker

git clone https://github.com/docker/swarm
cd swarm
git checkout v1.0.0-rc2 

sudo docker build -t $HUB_USER/swarm --no-cache .
