### To install and start Zookeeper, issue the following command:

```
sudo docker run --privileged --net=host -v=$LOG_DIR:/var/log/supervisor:rw -d mesostest/zookeeper --servers "host1_name,host1_id;host2_name,host2_id" --id host_id
```

### Where:
* $LOG_DIR – is the location on your local host where you want to copy the Zookeeper logs. These logs are copied from the /var/log/supervisor directory in the Zookeeper container. 
* $HUB_USER - is the namespace of the Zookeeper docker image.
* The --servers option – specifies the name and id of all the hosts in the Zookeeper cluster. The format is “host1_name,host1_id;host2_name,host2_id”
* The –-id option – specifies the id of the current host.

Please refer to https://zookeeper.apache.org/doc/trunk/zookeeperAdmin.html for admin guide of zookeeper. 
