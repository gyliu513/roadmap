### To install and start etcd, issue the following command:

```
sudo docker run --privileged --net=host -d mesostest/etcd --listen-client-urls http://0.0.0.0:4001 -advertise-client-urls http://$host_name:4001
```

### Where:
* $host_name – is the host name of your local host.

Please refer to following links for more documentations.
* https://github.com/coreos/etcd/blob/master/Documentation/configuration.md
* https://github.com/coreos/etcd/blob/master/Documentation/clustering.md
* https://github.com/coreos/etcd/blob/master/Documentation/admin_guide.md
