#!/bin/sh

MESOS_MASTER=9.21.58.21:5050

export JAVA_HOME=/root/jdk
#export JAVA_HOME=/usr/local/jdk1.8.0_60/
#export LD_LIBRARY_PATH=/root/lib:/root/usrlib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

echo $JAVA_HOME
echo $LD_LIBRARY_PATH
#export SPARK_HOME=/root/spark

export HADOOP_HOME=/root/hadoop

bash -x /root/spark/sbin/start-mesos-dispatcher.sh --master mesos://$MESOS_MASTER
#/home/yfeng/workshop/spark/sbin/start-mesos-dispatcher.sh --master mesos://$MESOS_MASTER

