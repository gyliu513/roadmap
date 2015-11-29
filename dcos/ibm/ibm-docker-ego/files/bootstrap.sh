#!/bin/bash

#Configure ASC and start the service
if [ -z $MASTER_HOST ];then 

    source /opt/ibm/platform/profile.platform
    egosetsudoers.sh
    echo "1" >> ~/.ASCConfigued
    MASTER_HOST=`hostname`
    source /opt/ibm/platform/profile.platform
    egoconfig join ${MASTER_HOST} -f
    egoconfig setentitlement /opt/ibm/platform_asc_entitlement.dat
    rm -rf /opt/ibm/platform_asc_entitlement.dat
    egosh ego start
    while [ 1 ];
    do
        tail -f /opt/ibm/platform/kernel/log/*.log
        sleep 5
    done

else
    source /opt/ibm/platform/profile.platform
    egosetsudoers.sh
    echo "1" >> ~/.ASCConfigued
    source /opt/ibm/platform/profile.platform
    egoconfig join $MASTER_HOST -f
    egosh ego start
    while [ 1 ];
    do
        tail -f /opt/ibm/platform/kernel/log/*.log
        sleep 5
    done

fi
