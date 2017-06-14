#!/bin/bash


HOST_IP=`ifconfig enp0s3 | grep inet | head -n 1 | awk '{print $2}' | awk -F ':' '{print $2}'`

if [ -z "$TIME_INTERVAL" ]; then
    TIME_INTERVAL=10
fi

#check if the directory has created
etcdctl --endpoints=$ETCD_ENDPOINTS ls /container/hostports/$HOST_IP/

if [ $? -ne 0 ]; then
	etcdctl --endpoints=$ETCD_ENDPOINTS mkdir /container/hostports/$HOST_IP/
fi

#remove the un-used data.
remove_data() {

for etcddata in `etcdctl  --endpoints=$ETCD_ENDPOINTS ls /container/hostports/$HOST_IP/`
do
        container_id=`basename $etcddata`
        running_container=`docker ps | grep $container_id| wc -l`
        if [ $running_container -eq 0 ]; then
                application_name=`etcdctl  --endpoints=$ETCD_ENDPOINTS get /container/hostports/$HOST_IP/$container_id | awk -F ':' '{print $1}'`
		if [ "x$applicaiton_name" != "x" ]; then
			etcdctl  --endpoints=$ETCD_ENDPOINTS rm /container/applications/$application_name/$container_id
			etcdctl  --endpoints=$ETCD_ENDPOINTS rm /container/hostports/$HOST_IP/$container_id
		fi
        fi
done

}

#update the etcddata with the latest port info
update_data() {

echo start to update data
for container in `docker ps --format "{{.Names}}+{{.ID}}+{{.Ports}}" |sed 's/, /,/g'`
do
	echo container is $container
	container_name=`echo $container | awk -F '+' '{print $1}'`
	echo container name is $container_name
        container_id=`echo $container | awk -F '+' '{print $2}'`
	echo container id is $container_id
        ports=`echo $container | awk -F '+' '{print $3}'`
	echo ports are $ports
	port_data=""
        if [ "x$ports" != "x" ]; then
		port_data=""
		ports=`echo $ports | sed 's/,/, /g'`
		for port in $ports
			do
				port_data=$port_data`echo $port | awk -F '->' '{print $2}'`
			done
		etcdctl  --endpoints=$ETCD_ENDPOINTS set /container/hostports/$HOST_IP/$container_id $container_name:$port_data
		
		etcdctl  --endpoints=$ETCD_ENDPOINTS ls /container/applications/$container_name
		
		if [$? -ne 0 ]; then
			etcdctl  --endpoints=$ETCD_ENDPOINTS mkdir /container/applications/$container_name
		fi
		
		value=$HOST_IP:$port_dat
		etcdctl  --endpoints=$ETCD_ENDPOINTS set /container/applications/$container_name/$container_id $value
        else
		echo no host port, just ignore.......
	fi
done
}

update_data
remove_data
# while :
# do 
#  	remove_data
# 	sleep $TIME_INTERVAL
# 	update_data
# 	sleep $TIME_INTERVAL
# done
