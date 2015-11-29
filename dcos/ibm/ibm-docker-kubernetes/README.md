### To install and start Kubernetes services, issue the following command:
```
sudo docker run --privileged --net=host -v=$LOG_DIR:/var/log/supervisor:rw -d mesostest/km --etcd-servers http://$host1_name:4001 --mesos-master $host2_name:5050
```
### Where:
* $LOG_DIR – is the location on your local host where you want to copy the Kubernetes logs. These logs are copied from the /var/log/supervisor directory in the Kubernetes container.
* $host1_name – is the location where the etcd cluster is running.
* $host2_name – is the location where the Mesos master cluster is running.
### TODO
The image has not support tuning Kubernetes by parameters mentioned as following link. We will add such support later.
https://github.com/mesosphere/kubernetes-mesos/blob/master/TUNING.md

### To create Kubernetes application in Marathon, issue the following command
```
curl -X POST -H "Content-Type: application/json" http://$host_name:8080/v2/apps -d@k8s.json | python -m json.tool
```
### Where:
* $host_name – is the location where Marathon is running
