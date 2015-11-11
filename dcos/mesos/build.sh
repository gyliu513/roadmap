#!/bin/bash


MESOS_VER=0.26.0
BUILD_DATE=`date "+%Y%m%d" --date="yesterday"`
BUILD_TAG="03 19"
BUILD_URL=http://pokgsa.ibm.com/projects/i/ibm-mesos/dailybuild-deb


for i in $BUILD_TAG
do
  MESOS_URL=$BUILD_URL/$BUILD_DATE$i/"mesos_"$MESOS_VER"-"$BUILD_DATE$i"_amd64.deb"
  wget $MESOS_URL
  if [ $? -eq 0 ] ; then
    mv $(basename $MESOS_URL) mesos.deb
    MESOS_TAG="$MESOS_VER"-"$BUILD_DATE$i"_amd64
    break;
  fi
done

if [ ! -f mesos.deb ] ; then
  echo "Failed to download Mesos daily build."
  exit 1
fi


echo "FROM $HUB_USER/mesos" > Dockerfile.slave
cat Dockerfile.slave.template >> Dockerfile.slave

echo "FROM $HUB_USER/mesos" > Dockerfile.master
cat Dockerfile.master.template >> Dockerfile.master

sudo docker build -t $HUB_USER/mesos --no-cache .
sudo docker build -t $HUB_USER/mesos-slave -f Dockerfile.slave --no-cache .
sudo docker build -t $HUB_USER/mesos-master -f Dockerfile.master --no-cache .
