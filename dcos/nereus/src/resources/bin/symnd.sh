#!/bin/sh

source /opt/cluster_611/profile.platform

VEMKD_PATH=`which vemkd`
SSM_PATH=`which ssm`
VEMKD_LOG=$EGO_TOP/kernel/log/vemkd.log.`hostname`
KAFKA=cua01:9092,cua02:9092,cua03:9092
TOPIC=others
PTN=1

LIB=$LD_LIBRARY_PATH

function send_msg()
{
    unset LD_LIBRARY_PATH
    ./nereus_send -t $TOPIC -b $KAFKA -p $PTN $*
    export LD_LIBRARY_PATH=$LIB
}

while [ 1 -gt 0 ]
do
    vemkd_metrics=`ps -aux | grep $VEMKD_PATH | awk -v vemkd=${VEMKD_PATH} '{if ($11==vemkd) print "cpu:"$3",mem:"$4}'`
    send_msg -m "serie:vemkd_metrics,"$vemkd_metrics",hostname:"`hostname`

    ssm_metrics=`ps -aux | grep $SSM_PATH | awk -v ssm=${SSM_PATH} '{if ($11==ssm) print "cpu:"$3",mem:"$4}'`

    send_msg -p $PTN -m "serie:ssm_metrics,"$ssm_metrics",hostname:"`hostname`

    memory=`free -m | awk '{if ($1 == "Mem:") print $3/$2 * 100}'`
    cpu=`grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}'`
    hostname=`hostname`

    send_msg -m "serie:host_metrics,mem:"$memory",cpu:"$cpu",hostname:"$hostname

    egosh user logon -x Admin -u Admin

    job_metrics=`soamview app symping6.1.1 -l | awk '
        /Running tasks:/{print "run:"$3}
        /Resource summary:/ {print "occupied:"$4}
        /Pending tasks in open sessions:/ {print "pending:"$6}
        /Open sessions:/ {print "openSsn:"$3}
        /Suspended sessions:/ {print "suspSsn:"$3}
    ' | xargs | sed 's/ /,/g'`
    slots_metrics=`egosh rg | grep ComputeHosts | awk '{print "total:"$3",free:"$4",allocate:"$5}'`

    send_msg -m "serie:job_metrics,app:sym6.1.1,"$job_metrics","$slots_metrics

    perftime=`tail -n 1000 $VEMKD_LOG | grep printPerf | tail -n 1 | cut -f 1 -d "."`

    perflog=`cat $VEMKD_LOG | grep "$perftime" | grep printPerf | awk '{
        split($2, t, ".");
        print "ts:"$1"-"t[1]",opCode:"$9",cnt:"$11",totalTime:"$13",fileIO:"$19",func:"$33
    }' | sed 's/<//g' | sed 's/>//g'`

    for line in $perflog
    do
        send_msg -m "serie:vemkd,""$line"
    done

    sleep 30

done
