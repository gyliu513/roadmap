### To install and start Mesos master and slave, issue the following command:
#### On master nodes
```
sudo docker run --privileged --net=host -v=$LOG_DIR:/opt/ibm/mesos/log:rw -d mesostest/mesos-master --zk=zk://host_name:2181/mesos --quorum=1
```
#### On slave nodes
```
sudo docker run --privileged=true --net=host --pid=host -volume=/:/rootfs:ro --volume=/sys:/sys:ro --volume=/dev:/dev --volume=/var/lib/docker/:/var/lib/docker:rw --volume=/var/run:/var/run:rw --volume=$LOG_DIR:/opt/ibm/mesos/log:rw -d mesostest/mesos-slave --master=zk://host_name:2181/mesos --isolation=cgroups --resources="cpus:16;mem:24576;disk:409600;ports:[10000-90000]" 
```
#### Where:
* $LOG_DIR – is the location on your local host where you want to copy the Mesos logs. These logs are copied from the /opt/ibm/mesos/log directory in the Zookeeper container. 
* The –-zk option – specifies the name and port for all nodes serving as master. The format is zk:host_name:port/mesos
* The --quorum option – specifies the number of hosts needed for the cluster to be in a functional state. This value is approximated at 50% of the total masters available. In practice, quorum is calculated at (number of masters/2).
* The --master option – specifies how to connect to a master or a quorum of masters. 

Please refer to http://mesos.apache.org/documentation/latest/configuration/ for more mesos configuration parameters.