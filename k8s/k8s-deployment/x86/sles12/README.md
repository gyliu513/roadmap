
#Note: this procedure has been deprecated, use the generic procedure at k8s-deployment/README.md

#Set up Kubernete Cluster on SLES 12


The procedure in this README is for a cluster with the following nodes and ip addresses, replace the nodenames and ip addresses with your own configuration.

```
c910f04x35k04 10.4.35.4 - Kubernetes master & worker
c910f04x35k05 10.4.35.5 - Kubernetes worker
c910f04x35k06 10.4.35.6 - Kubernetes worker
c910f04x35k07 10.4.35.7 - Kubernetes worker
c910f04x35k08 10.4.35.8 - Kubernetes worker
c910f04x35k09 10.4.35.9 - Kubernetes worker
```


##Install docker on all nodes

```
zypper addrepo --no-gpgcheck http://download.opensuse.org/repositories/Virtualization:containers/SLE_12/Virtualization:containers.repo
zypper refresh
zypper --non-interactive install  docker
systemctl enable docker
systemctl start docker
```
To use xCAT:

```
Paste the steps above into /install/postscripts/kubernetes/install_docker_on_SLES12.x86_64 on the xCAT management node

updatenode c910f04x35k04-c910f04x35k09 kubernetes/install_docker_on_SLES12.x86_64
```

##Copy the binaries to the nodes:

The binaries could be downloaded from https://yktgsa.ibm.com/home/l/i/liguangc/kubernetes/x86_64/1.4.6/

```
xdsh c910f04x35k04-c910f04x35k09 "mkdir /opt/bin/"
```

### Kubernetes master:

```
scp etcd etcdctl flanneld kube-apiserver kube-controller-manager kubectl kube-scheduler kubelet kube-proxy c910f04x35k04:/opt/bin/
```

###Kubernetes workers:

```
xdcp c910f04x35k05-c910f04x35k09 flanneld kubelet kube-proxy /opt/bin/
```

##Copy configuration files to the nodes:

```
git clone git@github.ibm.com:liguangc/k8s-deployment.git
cd k8s-deployment/x86/sles12
```

### Kubernetes master:

```
scp -rp usr etc c910f04x35k04:/
```

### Kubernetes workers:

```
xdcp c910f04x35k05-c910f04x35k09 etc/sysconfig/flanneld* /etc/sysconfig/
xdsh c910f04x35k05-c910f04x35k09 "mkdir /etc/kubernetes"
xdcp c910f04x35k05-c910f04x35k09 etc/kubernetes/config etc/kubernetes/kubelet etc/kubernetes/proxy /etc/kubernetes/
xdcp c910f04x35k05-c910f04x35k09 usr/lib/systemd/system/kubelet.service usr/lib/systemd/system/kube-proxy.service usr/lib/systemd/system/flanneld.service usr/lib/systemd/system/docker.service /usr/lib/systemd/system/
```

##Update the configuration files:

```
xdsh c910f04x35k04 "sed -i 's/127.0.0.1:2379/10.4.35.4:2379/' /etc/kubernetes/apiserver"
xdsh c910f04x35k04-c910f04x35k09 "sed -i 's/127.0.0.1:8080/10.4.35.4:8080/' /etc/kubernetes/kubelet"
xdsh c910f04x35k04-c910f04x35k09 "sed -i 's/127.0.0.1:8080/10.4.35.4:8080/' /etc/kubernetes/config"
xdsh c910f04x35k04-c910f04x35k09 "sed -i 's/127.0.0.1/10.4.35.4/' /etc/sysconfig/flanneld"

xdsh c910f04x35k04-c910f04x35k09 "systemctl daemon-reload"
```

##Start etcd on the Kubernetes master

```
c910f04x35k04:/etc/sysconfig # systemctl daemon-reload
c910f04x35k04:/etc/sysconfig # systemctl stop etcd
c910f04x35k04:/etc/sysconfig # systemctl start etcd
```

## Start flanneld on all nodes:

```
xdsh c910f04x35k04 "/opt/bin/etcdctl set /coreos.com/network/config < /etc/sysconfig/flanneld.netconfig.json"

xdsh c910f04x35k04-c910f04x35k09 "systemctl daemon-reload; systemctl stop flanneld; systemctl start flanneld"
```

## Configure dockerd on all nodes:

```
xdcp c910f04x35k04-c910f04x35k09 usr/lib/systemd/system/docker.service  /usr/lib/systemd/system/
xdsh c910f04x35k04-c910f04x35k09 "systemctl daemon-reload; systemctl stop docker; systemctl start docker" 
```

## Start kubernetes services on the nodes:

```
xdsh c910f04x35k04-c910f04x35k09 "mkdir /var/log/kubernetes; mkdir /var/lib/kubelet"

xdsh c910f04x35k04  "for i in kube-apiserver kube-controller-manager kube-scheduler kubelet kube-proxy; do systemctl enable \$i; systemctl stop \$i; systemctl start \$i; done"

xdsh c910f04x35k05-c910f04x35k09   "for i in kubelet kube-proxy; do systemctl enable \$i; systemctl stop \$i; systemctl start \$i; done"
```


## Configure kube-dns:

```
c910f04x35k04:~/yaml/kube-dns # sed -i 's/10.4.35.3:8080/10.4.35.4:8080/' kubedns-deployment.yaml
c910f04x35k04:~/yaml/kube-dns # kubectl create -f kubedns-deployment.yaml -f kubedns-svc.yaml
```
 

## Configure dashboard:

```
c910f04x35k04:~/yaml/dashboard # sed -i 's/10.4.35.3:8080/10.4.35.4:8080/' dashboard-controller.yaml
c910f04x35k04:~/yaml/dashboard # kubectl create -f dashboard-controller.yaml -f dashboard-service.yaml
```

## Run the sample nginx application 

To verify the cluster is setup correctly:

```
c910f04x35k04:~/yaml/nginx # kubectl create -f nginx.yaml
```

 When the PODs are up and running, kubectl exec into a POD, verify:


	* Could resolve the my-nginx service name
	* Could access internet
	* Verify the nginx service could be accessed at http://10.4.35.4:8080/api/v1/proxy/namespaces/default/services/my-nginx/


Here is an example:
```
root@my-nginx-873447256-c5o9v:/# getent hosts my-nginx
20.254.155.72   my-nginx.default.svc.cluster.local
root@my-nginx-873447256-c5o9v:/# ping www.google.com -c 1
PING www.google.com (172.217.0.164): 56 data bytes
64 bytes from 172.217.0.164: icmp_seq=0 ttl=50 time=36.878 ms
--- www.google.com ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss
round-trip min/avg/max/stddev = 36.878/36.878/36.878/0.000 ms
root@my-nginx-873447256-c5o9v:/#
```

