### To install and start Marathon, issue the following command:
```
sudo docker run --privileged --net=host -v=$LOG_DIR:/opt/marathon-0.11.1/log:rw -d mesostest/marathon --master zk://host_name:2181/mesos --zk zk://host_name:2181/marathon
```
#### Where:
* $LOG_DIR - is the location on your local host where you want to copy the Marathon logs. These logs are copied from the /opt/marathon-0.11.1/log directory in the Marathon container.
* The --master option – specifies how to connect to a master or a quorum of masters.

