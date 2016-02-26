#!/bin/bash

CLOUD_CONF=$K8S_HOME/mesos-cloud.conf

SUPERVISORD_CONF=/etc/supervisor/conf.d/supervisord.conf
LOG_LEVEL=info

TEMP=`getopt -o l:e:m:s:r: --long log-level:,etcd-servers:,mesos-master:,scheduler-config:,mesos-framework-roles:,enable-revocable:\
  -n 'bootstrap.sh' -- "$@"`

if [ $? != 0 ] ; then
  echo "Terminating..." >&2 ;
  exit 1 ;
fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

while true; do
  case "$1" in
    --log-level | -l ) LOG_LEVEL="$2"; shift 2 ;;
    --etcd-servers | -e ) ETCD_SERV="$2"; shift 2 ;;
    --mesos-master | -m ) MESOS_MASTER="$2"; shift 2 ;;
    --scheduler-config | -s ) SCHED_CONF="$2"; shift 2 ;;
    --mesos-framework-roles | -r ) MESOS_ROLE="$2"; shift 2 ;;
    --enable-revocable | -r ) MESOS_REVOCABLE="$2"; shift 2 ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

if [ -z $ETCD_SERV ] ; then
  echo "--etcd-servers can not be empty."
  exit 1
fi

if [ -z $MESOS_MASTER ] ; then
  echo "--mesos-master can not be empty."
  exit 1
fi

cat > $CLOUD_CONF <<End-Of-CC
[mesos-cloud]
        mesos-master        = $MESOS_MASTER
End-Of-CC

if [ -z $SCHED_CONF ] ; then
  KM_SCHED_ARG=""
else
  KM_SCHED_ARG="--scheduler-config=$SCHED_CONF"
fi

if [ -z $MESOS_ROLE ] ; then
  MESOS_ROLE_ARG=""
else
  MESOS_ROLE_ARG="--mesos-framework-roles=$MESOS_ROLE"
fi

if [ -z $MESOS_REVOCABLE ] ; then
  MESOS_REVOCABLE_ARG=""
else
  MESOS_REVOCABLE_ARG="--enable-revocable=$MESOS_REVOCABLE"
fi

cat > $SUPERVISORD_CONF <<End-Of-SC
[supervisord]
nodaemon=true
loglevel = $LOG_LEVEL
logfile=/var/log/supervisor/supervisord.log
pidfile = /tmp/supervisord.pid

[program:apiserver]
command=$K8S_HOME/km apiserver --address=`hostname -i` --etcd-servers=$ETCD_SERV --service-cluster-ip-range=10.10.10.0/24 --port=8888 --cloud-provider=mesos --cloud-config=mesos-cloud.conf --secure-port=0 --v=4
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log

[program:controller]
command=$K8S_HOME/km controller-manager --master=`hostname -i`:8888 --cloud-provider=mesos --cloud-config=$CLOUD_CONF --v=4
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log

[program:scheduler]
command=$K8S_HOME/km scheduler --address=`hostname -i` $MESOS_REVOCABLE_ARG $KM_SCHED_ARG $MESOS_ROLE_ARG --mesos-master=$MESOS_MASTER --etcd-servers=$ETCD_SERV --mesos-user=root --api-servers=`hostname -i`:8888 --cluster-dns=10.10.10.10 --cluster-domain=cluster.local --v=4
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log

End-Of-SC

/usr/bin/supervisord
