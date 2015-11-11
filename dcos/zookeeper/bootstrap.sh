#!/usr/bin/env bash

if [ ! -d $ZK_HOME ]; then
  echo "The ZK_HOME ($ZK_HOME) is not a directory."
  exit 1
fi

TEMP=`getopt -o s:i: --long servers:,id: \
  -n 'zkStart.sh' -- "$@"`

if [ $? != 0 ] ; then
  echo "Terminating..." >&2 ;
  exit 1 ;
fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

while true; do
  case "$1" in
    --servers | -s ) ZK_HOST="$2"; shift 2 ;;
    --id | -i ) ZK_ID="$2"; shift 2 ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

if [ -z $ZK_HOST ]; then
  echo "No ZooKeeper server list."
  exit 1
fi

if [ -z $ZK_ID ]; then
  echo "No ZooKeeper ID for this service"
fi

IFS=';' hosts=($ZK_HOST)

for i in "${hosts[@]}"; do
  IFS=',' serv=($i)
  echo server.${serv[1]}=${serv[0]}:2888:3888 >> $ZK_HOME/conf/zoo.cfg
done

mkdir -p /tmp/zookeeper/

echo $ZK_ID > /tmp/zookeeper/myid

echo "Starting ZooKeeper by following configuration"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ZooKeeper: $ZK_HOME/conf/zoo.cfg <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
cat $ZK_HOME/conf/zoo.cfg

echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ZooKeeper: /tmp/zookeeper/myid <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
cat /tmp/zookeeper/myid

$ZK_HOME/bin/zkServer.sh start-foreground
