### To install and start Swarm, issue the following command:
```
sudo docker run --privileged --net=host -v=$LOG_DIR:/var/log/supervisor:rw -d mesostest/swarm \
  --debug manage -c mesos-experimental \
  --cluster-opt mesos.address=0.0.0.0  \
  --cluster-opt mesos.tasktimeout=10m  \
  --cluster-opt mesos.offertimeout=1m  \
  --cluster-opt mesos.user=root        \
  --cluster-opt mesos.port=3375 --host 0.0.0.0:4375 zk://$host_name:2181/mesos
```
### Where:
* $LOG_DIR – is the location on your local host where you want to copy the Swarm logs. These logs are copied from the /var/log/supervisor directory in the Swarm container.
* $hostname – is the location where the Zookeeper cluster is running.

Please refer to following for all the parameters swarm manage supports. 
```
Arguments:
   <discovery>    discovery service to use [$SWARM_DISCOVERY]
                   * token://<token>
                   * consul://<ip>/<path>
                   * etcd://<ip1>,<ip2>/<path>
                   * file://path/to/file
                   * zk://<ip1>,<ip2>/<path>
                   * <ip1>,<ip2>

Options:
   --rootdir "/.swarm"
   --strategy "spread"                      placement strategy to use [spread, binpack, random]
   --filter, -f [--filter option --filter option]       filter to use [affinity, health, constraint, port, dependency]
   --host, -H [--host option --host option]         ip/socket to listen on [$SWARM_HOST]
   --replication                        Enable Swarm manager replication
   --advertise, --addr                      Address of the swarm manager joining the cluster. Other swarm manager(s) MUST be able to reach the swarm manager at this address. [$SWARM_ADVERTISE]
   --tls                            use TLS; implied by --tlsverify=true
   --tlscacert                          trust only remotes providing a certificate signed by the CA given here
   --tlscert                            path to TLS certificate file
   --tlskey                             path to TLS key file
   --tlsverify                          use TLS and verify the remote
   --heartbeat "20s"                        period between each heartbeat
   --api-enable-cors, --cors                    enable CORS headers in the remote API
   --cluster-driver, -c "swarm"                 cluster driver to use [swarm, mesos-experimental]
   --cluster-opt [--cluster-opt option --cluster-opt option]    cluster driver options
                                 * swarm.overcommit=0.05    overcommit to apply on resources
                                                     * mesos.address=       address to bind on [$SWARM_MESOS_ADDRESS]
                                                     * mesos.port=          port to bind on [$SWARM_MESOS_PORT]
                                                     * mesos.offertimeout=10m   timeout for offers [$SWARM_MESOS_OFFER_TIMEOUT]
                                                     * mesos.tasktimeout=5s     timeout for task creation [$SWARM_MESOS_TASK_TIMEOUT]
                                                     * mesos.user=          framework user [$SWARM_MESOS_USER]
```
### To create Swarm application in Marathon, issue the following command
```
curl -X POST -H "Content-Type: application/json" http://$host_name:8080/v2/apps -d@swarm.json | python -m json.tool
```
### Where:
* $host_name – is the location where Marathon is running 
