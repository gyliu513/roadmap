# Docker as a Service

The Docker images to build a DaaS environment.

	nohup sudo docker daemon -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2375 &

	sudo docker run --privileged --net=host -d mesostest/zookeeper --servers "ma1demo1,1" --id 1
	sudo docker run --privileged --net=host -d mesostest/etcd --listen-client-urls http://ma1demo1:4001 -advertise-client-urls http://ma1demo1:4001
	
	sudo docker run --privileged --net=host -d mesostest/mesos-master --zk=zk://ma1demo1:2181/mesos --quorum=1
	sudo docker run --privileged --net=host -d -v /sys:/sys -v /cgroup:/cgroup -v /var/run/docker.sock:/var/run/docker.sock -v `which docker`:/usr/bin/docker mesostest/mesos-slave --master=zk://ma1demo1:2181/mesos --isolation=cgroups --resources="cpus:16;mem:24576;disk:409600;ports:[10000-90000]" 
	
	sudo docker run --privileged --net=host -d mesostest/marathon --master zk://ma1demo1:2181/mesos

	sudo docker run --privileged --net=host -d mesostest/km --etcd-servers http://ma1demo1:4001 --mesos-master ma1demo1:5050
	
	sudo docker run --privileged --net=host  mesostest/swarm --debug manage -c mesos-experimental \
	    --cluster-opt mesos.address=0.0.0.0 \
	    --cluster-opt mesos.tasktimeout=10m \
	    --cluster-opt mesos.offertimeout=1m \
	    --cluster-opt mesos.port=3375 --host 0.0.0.0:4375 zk://ma1demo1:2181/mesos

