#!/bin/bash
#docker run  -i -t --name="mn01" --hostname="mn01" --dns=172.17.0.38  sequenceiq/hadoop-cluster-docker:2.4.1 9001 50010 N 1 -bash 192.168.1.4
#docker run  -i -t --name="dn01" --hostname="dn01" --dns=172.17.0.38 --link=mn01:mn01 sequenceiq/hadoop-cluster-docker:2.4.1 9001 50010 D 1 -bash 172.17.0.39
#docker run  -i -t --name="dn02" --hostname="dn02" --dns=172.17.0.38 --link=mn01:mn01 sequenceiq/hadoop-cluster-docker:2.4.1 9001 50010 D 1 -bash 172.17.0.39

env

: ${HADOOP_PREFIX:=/usr/local/hadoop}

$HADOOP_PREFIX/etc/hadoop/hadoop-env.sh

rm /tmp/*.pid

# installing libraries if any - (resource urls added comma separated to the ACP system variable)
cd $HADOOP_PREFIX/share/hadoop/common ; for cp in ${ACP//,/ }; do  echo == $cp; curl -LO $cp ; done; cd -



# print the params
echo "Namenode or datanode:$1"
echo "Number of hdfs replication:$2"
echo "Default command:$3"
echo "Master ip:$4"
echo "Master host:$5"

# IFC=$(ifconfig | grep '^[a-z0-9]' | awk '{print $1}' | grep -e ns -e eth0)
# IP_ADDRESS=$(ifconfig $IFC | grep 'inet addr' | awk -F : {'print $2'} | awk {'print $1'})
IP_ADDRESS=`ifconfig eth0 |grep "inet addr"| cut -f 2 -d ":"|cut -f 1 -d " "`
HOST_NAME=`hostname`
echo "ipaddress=$IP_ADDRESS"
echo "hostname=$HOST_NAME"
# altering the core-site,yarn-site,hdfs-site configuration
sed -i s/__HDFS_REP__/1/ /usr/local/hadoop/etc/hadoop/hdfs-site.xml


#start NameNode and DataNode

cd $HADOOP_HOME
service sshd start

if [ $1 = "N" ] ; then
    sed -i s/__MASTER__/$HOST_NAME/ /usr/local/hadoop/etc/hadoop/core-site.xml
    sed -i s/__MASTER__/$HOST_NAME/ /usr/local/hadoop/etc/hadoop/yarn-site.xml
    echo "starting Hadoop Namenode,resourcemanager,datanode,nodemanager"
    
    #rm -rf  /tmp/hadoop-root
    #$HADOOP_PREFIX/bin/hdfs namenode -format> /dev/null 2>&1
    $HADOOP_PREFIX/sbin/hadoop-daemon.sh  start namenode > /dev/null 2>&1
    echo "Succeed to start namenode"
    
    $HADOOP_PREFIX/sbin/yarn-daemon.sh  start resourcemanager > /dev/null 2>&1
    echo "Succeed to start resourcemanager"


    $HADOOP_PREFIX/sbin/hadoop-daemon.sh  start datanode > /dev/null 2>&1
    echo "Succeed to start datanode"

    $HADOOP_PREFIX/sbin/yarn-daemon.sh  start nodemanager > /dev/null 2>&1
    echo "Succeed to start nodemanager"

    $HADOOP_PREFIX/bin/hadoop dfsadmin -safemode leave
else
    sed -i s/__MASTER__/$5/ /usr/local/hadoop/etc/hadoop/core-site.xml
    sed -i s/__MASTER__/$5/ /usr/local/hadoop/etc/hadoop/yarn-site.xml
    echo "starting Hadoop Datanode,nodemanager"
    echo "$4 $5" >> /etc/hosts
    ssh $4 "echo \"$IP_ADDRESS $HOST_NAME\" >> /etc/hosts"
    rm -rf  /tmp/hadoop-root
    $HADOOP_PREFIX/sbin/hadoop-daemon.sh  start datanode > /dev/null 2>&1
    echo "Succeed to start datanode"

    $HADOOP_PREFIX/sbin/yarn-daemon.sh  start nodemanager > /dev/null 2>&1
    echo "Succeed to start nodemanager"
fi

if [[ $3 == "-d" ]]; then
  while true; do sleep 1000; done
fi

if [[ $3 == "-bash" ]]; then
  /bin/bash
fi


