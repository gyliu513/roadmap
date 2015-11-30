#!/bin/bash
MESOS_VER=0.26.0
BUILD_DATE=$(date "+%Y%m%d" --date="yesterday")
BUILD_TAG="03 19"
BUILD_URL=http://pokgsa.ibm.com/projects/i/ibm-mesos/dailybuild-deb
#BUILD_RELEASE=http://pokgsa.ibm.com/projects/i/ibm-mesos/releases-deb/0.25.0/mesos_0.25.0-2015110105_amd64.deb
BUILD_RELEASE=http://pokgsa.ibm.com/projects/i/ibm-mesos/releases-deb/0.25.0/mesos-2015110105.tar.gz


if [ ! -z $BUILD_RELEASE ]
then
  rm -rf mesos $BUILD_RELEASE
  wget $BUILD_RELEASE
  #mv $(basename $BUILD_RELEASE) mesos.deb
  tar zxvf $(basename $BUILD_RELEASE) 

if [ ! -d mesos ] ; then
  echo "Failed to download Mesos daily build."
  exit 1
fi

else
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

fi
cat Dockerfile.template > Dockerfile
cat Dockerfile.marathon >> Dockerfile 

sudo docker build -t $HUB_USER/marathon --no-cache .
