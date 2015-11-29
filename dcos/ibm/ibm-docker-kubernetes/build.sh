#!/bin/bash

#GO_URL=https://storage.googleapis.com/golang/go1.5.1.linux-amd64.tar.gz
GO_URL=https://storage.googleapis.com/golang/go1.4.linux-amd64.tar.gz

TOP_DIR=`pwd`

sudo apt-get install -y wget

#Install Go 
if  [ ! -d $TOP_DIR/go ] ; then
  curl -O -L $GO_URL
  tar zxvf $(basename $GO_URL)
fi


export GOROOT=$TOP_DIR/go
export GOPATH=$TOP_DIR/godep
export PATH=$GOROOT/bin:$PATH

mkdir -p $GOPATH

git clone https://github.com/GoogleCloudPlatform/kubernetes

cd kubernetes
git checkout -b release-1.1 -t remotes/origin/release-1.1

export KUBERNETES_CONTRIB=mesos

make

cd $TOP_DIR

cat Dockerfile.kubernetes > Dockerfile.km
cat Dockerfile.km.template >> Dockerfile.km

cat Dockerfile.kubernetes > Dockerfile.kubelet
cat Dockerfile.kubelet.template >> Dockerfile.kubelet

sudo docker build -t $HUB_USER/km -f Dockerfile.km --no-cache .
sudo docker build -t $HUB_USER/kubelet -f Dockerfile.kubelet --no-cache .
