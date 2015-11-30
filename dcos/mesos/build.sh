#!/bin/bash

MESOS_VER=0.27.0
BUILD_DATE=$(date "+%Y%m%d" --date="yesterday")
BUILD_TAG="03 19"
BUILD_URL=http://pokgsa.ibm.com/projects/i/ibm-mesos/dailybuild-deb
BUILD_RELEASE=http://pokgsa.ibm.com/projects/i/ibm-mesos/releases-deb/0.25.0/mesos_0.25.0-2015110105_amd64.deb
TOP_DIR=$(pwd)

if [ ! -z $BUILD_RELEASE ];
then
#  wget $BUILD_RELEASE
#  mv $(basename $BUILD_RELEASE) mesos.deb
#else
  for i in $BUILD_TAG
  do
    MESOS_URL=$BUILD_URL/$BUILD_DATE$i/"mesos_"$MESOS_VER"-"$BUILD_DATE$i"_amd64.deb"
#    wget $MESOS_URL
    if [ $? -eq 0 ] ; then
#      mv $(basename $MESOS_URL) mesos.deb
      break;
    fi
  done
fi

# get dailybuild
wget $BUILD_URL/last -O index.html

BUILD_PACKAGE=`cat index.html|grep mesos_${MESOS_VERSION}| awk '{print $5}' | cut -c7- | cut -f1 -d '"'`
rm -rf index.html
wget $BUILD_URL/last/$BUILD_PACKAGE -O $TOP_DIR/files/mesos.deb

if [ ! -f mesos.deb ] ; then
  echo "Failed to download Mesos daily build."
  exit 1
fi


#cat Dockerfile.template > Dockerfile 
#cat Dockerfile.master >> Dockerfile

#sudo docker build -t $HUB_USER/mesos-master --no-cache .

cat Dockerfile.template > Dockerfile 
cat Dockerfile.slave >> Dockerfile

sudo docker build -t mesostest/mesos-slave:$MESOS_VER --no-cache .
