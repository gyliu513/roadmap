#!/bin/bash

SUPERVISORD_CONF=/etc/supervisor/conf.d/supervisord.conf
LOG_LEVEL=debug

cat > $SUPERVISORD_CONF <<End-Of-SC
[supervisord]
nodaemon=true
loglevel = $LOG_LEVEL
logfile=/var/log/supervisor/supervisord.log
pidfile = /tmp/supervisord.pid
autorestart=false

[program:etcd]
command=$ETCD_HOME/etcd $@
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log

End-Of-SC

/usr/bin/supervisord
