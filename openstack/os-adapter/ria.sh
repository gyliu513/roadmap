#!/bin/sh
 
# Copyright Platform Computing Inc., an IBM company, 2012 
 
# $Id: ria.sh,v 1.1.2.2 2012/06/15 14:38:12 gyliu Exp $

# =============================================================
# ria.sh
# 
# Call the EC2 adapter 
#
# Return
#   - Exit Code: 0 if successful
#                -1 otherwise
#
# =============================================================
ARGS=$*

if [ "x_$PYTHONPATH" == "x_" ]; then
    export PYTHONPATH=../rialib
else
   export PYTHONPATH=$PYTHONPATH:../rialib
fi

# Java and EC2 home/command directories
export JAVA_HOME=/opt/gyliu/ae0607/jre/linux-x86_64

export RI_OPENSTACK_CMDS=/usr/bin/
export PATH=$PATH:$RI_OPENSTACK_CMDS

# unset CLASSPATH since commons-cli-1.0.jar from perf conflict with EC2 jar file
export CLASSPATH="" 

echo "$ARGS" >> /tmp/openstackarg.log

echo "$ARGS" |grep provision > /dev/null
if [ "$?" != "0" ]; then
    python openstackria.py $ARGS
else
    WRAPPER=""
    MYARGS=""
    for opt in $ARGS
    do
        case $opt in
            --wrapscriptpath=* )
                WRAPPER=`echo $opt|awk -F "=" '{print $2}'`
                MYARGS="$MYARGS $opt"
                ;;
            provision )
		ACT=provision
                ;;
            *)
                MYARGS="$MYARGS $opt"
                ;;
        esac
    done
    if [ "$WRAPPER" != "" ]; then
        SKIP=Y
        for i in `cat $WRAPPER |grep "isf_script"` ; do
            if [ "$SKIP" = "Y" ]; then
                SKIP=N
                continue
            fi
            export $i
        done
	cp $WRAPPER /tmp/ec2wraper.sh
    fi
    python openstackria.py $MYARGS provision
    exit $?
fi
