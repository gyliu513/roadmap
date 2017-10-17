## Table of Contents

- [Set up Kubernete Cluster](#set-up-kubernete-cluster)
  * [Install docker on all nodes](#install-docker-on-all-nodes)
  * [Get Kubernetes binaries:](#get-kubernetes-binaries)
  * [Get docker images](#get-docker-images)
  * [Clone this git repo](#clone-this-git-repo)
  * [Generate the Kubernetes certificate keys](#generate-the-kubernetes-certificate-keys)
  * [Make the necessary directories on all nodes:](#make-the-necessary-directories-on-all-nodes)
  * [Add /opt/bin in the PATH](#add-optbin-in-the-path)
  * [Setup etcd cluster](#setup-etcd-cluster)
  * [(Optional)Setup flanneld on all nodes](#optionalsetup-flanneld-on-all-nodes)
  * [(Optional)Configure dockerd to work with flannel](#optionalconfigure-dockerd-to-work-with-flannel)
  * [Start kubernetes services on the master nodes](#start-kubernetes-services-on-the-master-nodes)
  * [(Optional) Setup haproxy and keepalived on the masters](#optional-setup-haproxy-and-keepalived-on-the-masters)
    + [Install haproxy and keepalived on the masters](#install-haproxy-and-keepalived-on-the-masters)
    + [Update the configuration files](#update-the-configuration-files)
  * [Setup kubectl on the master nodes:](#setup-kubectl-on-the-master-nodes)
  * [Start kubernetes on one worker node](#start-kubernetes-on-one-worker-node)
  * [Setup Calico](#setup-calico)
    + [(Optional) configure docker with etcd cluster-store](#optional-configure-docker-with-etcd-cluster-store)
    + [Run calico node on the worker node](#run-calico-node-on-the-worker-node)
    + [(Optional) Update kubelet configuration](#optional-update-kubelet-configuration)
  * [Add the other worker nodes](#add-the-other-worker-nodes)
  * [(Optional) Load the docker images on the worker nodes](#optional-load-the-docker-images-on-the-worker-nodes)
  * [Run calico-kube-policy-controller](#run-calico-kube-policy-controller)
  * [Setup kube-dns](#setup-kube-dns)
  * [Configure dashboard:](#configure-dashboard)
  * [Run the sample nginx application to verify the cluster is setup correctly:](#run-the-sample-nginx-application-to-verify-the-cluster-is-setup-correctly)
  * [Setup nginx ingress controller](#setup-nginx-ingress-controller)
  * [Setup helm](#setup-helm)
  * [Setup Prometheus & Grafana](#setup-prometheus--grafana)
  * [Setup cluster-level logging architectures](#setup-cluster-level-logging-architectures)


# Set up Kubernete Cluster 

The procedure is a generic procedure that should work for all the hardware platforms and operating systems, there might be minor differences for different combinations, but the basic work flow should be the same.

## Install docker on all nodes

Install docker 1.12.x or above on all the nodes. The docker 1.11.x or lower might also work, but was not verified.

After docker is installed, run the following commands:

```
systemctl enable docker
systemctl start docker
docker version
```

## Get Kubernetes binaries:

The binaries could be downloaded from http://bejgsa.ibm.com/home/l/i/liguangc/kubernetes/, download the binaries to a directory, say /root/k8s-repo/kubernetes-binaries/, on all the nodes, could use NFS mounts for simplicity.

**Note:** the binaries might not be the latest version, could get the latest version from the following links:

* kubernetes: https://github.com/kubernetes/kubernetes/releases
* etcd: https://github.com/coreos/etcd/releases
* calico-node: https://hub.docker.com/r/calico/node/
* calico kube-policy-controller: https://hub.docker.com/r/calico/kube-policy-controller/
* calicoctl: https://github.com/projectcalico/calicoctl/releases
* calico cni plugin: https://github.com/projectcalico/cni-plugin/releases
* loopback cni plugin: https://github.com/containernetworking/cni/releases
* flannel: https://github.com/coreos/flannel/releases

## Get docker images

Various docker images will be needed to setup different components, if the setup is in a disconnected environment or the internet access speed is a concern, it is a good idea to fetch these docker images ahead of time, you could either upload the images to a private registry or load these images manually when necessary. Here is the list:

* calico/kube-policy-controller
* calico/node
* gcr.io/kubernetes-helm/tiller
* gcr.io/google_containers/kubernetes-dashboard-amd64
* gcr.io/google_containers/kube-dnsmasq-amd64
* gcr.io/google_containers/defaultbackend
* gcr.io/google_containers/kubedns-amd64
* gcr.io/google_containers/exechealthz-amd64
* gcr.io/google_containers/nginx-ingress-controller
* gcr.io/google_containers/pause-amd64
* gcr.io/google_containers/nginx-ingress-controller
* nginx:1.8.1
* prom/alertmanager
* jimmidyson/configmap-reload
* gcr.io/google_containers/kube-state-metrics
* prom/node-exporter
* grafana/grafana

## Clone this git repo

This repo includes all the scripts and configuration files for configuring the Kubernetes cluster, clone this git repo on all the nodes, say /root/k8s-repo/k8s-deployemnt, could use NFS mounts for simplicity.

```

cd /root/k8s-repo
git clone git@github.ibm.com:liguangc/k8s-deployment.git

```

## Generate the Kubernetes certificate keys

```
mkdir /root/kube
cp /root/k8s-repo/k8s-deployment/scripts/{easy-rsa.tar.gz,make-ca-cert.sh} /root/kube
cd /root/kube
CERT_GROUP=root KUBE_CERT_KEEP_CA=true ./make-ca-cert.sh 9.12.246.195 IP:9.12.246.195,IP:10.91.0.195,IP:20.254.0.1,DNS:kubernetes,DNS:kubernetes.default,DNS:kubernetes.default.svc,DNS:kubernetes.default.svc.cluster.local

```
Where the 9.12.246.195 is the main ip address of the node on which the command is being run, the other IP addresses are configured on the all the other network interfaces. 20.254.0.1 is the first ip address in the Kubernetes service ip pool, which will be used by the "kubernetes" service. If this is a HA configuration, include the ip addresses of all the Kuernetes masters and the virtual ip address in the IP list.

Here is an example of the HA configuration:

```
CERT_GROUP=root ./make-ca-cert.sh 172.18.1.20 IP:192.168.32.20,IP:172.18.1.21,IP:192.168.32.21,IP:172.18.1.22,IP:192.168.32.22,IP:172.18.1.23,IP:10.254.0.1,DNS:kubernetes,DNS:kubernetes.default,DNS:kubernetes.default.svc,DNS:kubernetes.default.svc.cluster.local
```

After the script is run, the keys and certificates will be in /srv/kubernetes/, here is an example:

```
root@kube-master:~# ls /srv/kubernetes/ -l
total 28
-rw-rw---- 1 root root 1220 Dec 21 04:00 ca.crt
-rw------- 1 root root 4417 Dec 21 04:00 kubecfg.crt
-rw------- 1 root root 1704 Dec 21 04:00 kubecfg.key
-rw-rw---- 1 root root 4904 Dec 21 04:00 server.cert
-rw-rw---- 1 root root 1708 Dec 21 04:00 server.key
root@kube-master:~# 
```

Copy the /srv/kubernetes directory to all the Kubernetes master nodes


## Make the necessary directories on all nodes:

Not all the directories are needed on all the nodes, but the missing directories will cause various issues, let's create these directories on all nodes.

```
mkdir -p /opt/bin
mkdir -p /etc/kubernetes
mkdir -p /var/log/kubernetes
mkdir -p /var/lib/kubelet
mkdir -p /etc/sysconfig
mkdir -p /var/lib/etcd
mkdir -p /opt/cni/bin
mkdir -p /etc/cni/net.d
mkdir -p /var/lib/etcd/default.etcd
```
Could run /root/k8s-repo/k8s-deployment/scripts/make_k8s_dirs on all nodes  

## Add /opt/bin in the PATH

All the kubernetes, flannel/calico and etcd binaries will be put to /opt/bin directory, so add /opt/bin into the PATH

```
echo "export PATH=\$PATH:/opt/bin" >> ~/.profile
source ~/.profile
```

## Setup etcd cluster

It is not a must, but is a common practice to run the etcd cluster on the Kubernetes masters

On all the Kubernetes masters:

```
cp /root/k8s-repo/kubernetes-binaries/x86_64/etcdv3/3.1.6/* /opt/bin/
chmod 755 /opt/bin/etcd*
cp /root/k8s-repo/k8s-deployment/systemd-files/etc/sysconfig/etcd /etc/sysconfig/
cp /root/k8s-repo/k8s-deployment/systemd-files/systemd/system/etcd.service /lib/systemd/system/
```

**Review and update** the /etc/sysconfig/etcd, mainly update the ip addresses, in the HA configuration, the /etc/sysconfig/etcd is different on each etcd member node, refer to /root/k8s-repo/k8s-deployment/systemd-files/etc/sysconfig/etcd.ha as an example. 

Do not use 127.0.0.1 or localhost as the etcd options, especially when Calico will be used, Calico will need to communicate with the etcd from all the nodes.

```
systemctl enable etcd
systemctl start etcd
```

Use etcdctl to verify etcd is working:

```
etcdctl member list

etcdctl set /foo bar

etcdctl get /foo

etcdctl rm /foo
```

You may also run "etcdctl cluster-health" to verify the cluster health status.

```
root@c910f03c01p04:~# etcdctl cluster-health
member b2939073ebf22046 is healthy: got healthy result from http://10.3.1.4:2379
cluster is healthy
root@c910f03c01p04:~# 

```

## (Optional)Setup flanneld on all nodes

If Calico will be used, skip this step.

On all the nodes:

```
cp /root/k8s-repo/kubernetes-binaries/x86_64/flannel/0.7.1/flanneld /opt/bin/
cp /root/k8s-repo/k8s-deployment/systemd-files/etc/sysconfig/flanneld* /etc/sysconfig/
cp /root/k8s-repo/k8s-deployment/systemd-files/systemd/system/flanneld.service /lib/systemd/system/flanneld.service
```

Review /etc/sysconfig/flanneld to update the FLANNEL_ETCD_ENDPOINTS and iface in FLANNEL_OPTIONS

On one of the etcd node, review /etc/sysconfig/flanneld.netconfig.json to update Network and Backend Type:

```
/opt/bin/etcdctl set /coreos.com/network/config < /etc/sysconfig/flanneld.netconfig.json
```


On all the nodes:

```
systemctl daemon-reload
systemctl enable flanneld
systemctl start flanneld
```

 
## (Optional)Configure dockerd to work with flannel

If Calico will be used, skip this step.

On all nodes, review /lib/systemd/system/docker.service to make the flannel related updates:

* add EnvironmentFile=-/run/flannel/subnet.env
* add --bip=${FLANNEL_SUBNET} --mtu=${FLANNEL_MTU} --ip-masq=false in ExecStart

Note: for docker 1.13+, you need to add one line to docker.service, see https://github.com/kubernetes/kubernetes/issues/40182 for more details

```
ExecStartPost=iptables -P FORWARD ACCEPT
```

Refer to  /root/k8s-repo/k8s-deployment/systemd-files/systemd/system/docker.service.flannel  as an example

```
systemctl daemon-reload
systemctl stop docker
systemctl start docker
```

## Start kubernetes services on the master nodes

```
root@kube-master:~/k8s-repo/kubernetes-binaries/1.5.0# cp kubectl kube-apiserver kube-controller-manager  kube-scheduler /opt/bin/
chmod 755 /opt/bin/kube*
root@kube-master:~/k8s-repo/k8s-deployment/systemd-files/etc/kubernetes# cp config apiserver controller-manager scheduler /etc/kubernetes/
root@kube-master:~/k8s-repo/k8s-deployment/systemd-files/systemd/system# cp kube-apiserver.service kube-controller-manager.service kube-scheduler.service /lib/systemd/system/
```

**Review and update** the kubernetes configuration files under /etc/kubernetes/. At least, the following attributes need to be updated:

**KUBE_MASTER** in config

**KUBE_SERVICE_ADDRESSES** in apiserver

```
systemctl daemon-reload
for i in kube-apiserver kube-controller-manager kube-scheduler; do systemctl enable $i; systemctl stop $i; systemctl start $i; done
```

## (Optional) Setup haproxy and keepalived on the masters

This is required for HA configuration.

### Install haproxy and keepalived on the masters

```
On Ubuntu: apt-get -y install haproxy keepalived

On SLES: rpm -Uvh cluster-network-kmp-default-1.4_k3.12.28_4-25.10.x86_64.rpm haproxy-1.5.14-1.4.x86_64.rpm keepalived-1.2.12-3.1.12.x86_64.rpm

```
### Update the configuration files

```
cp /root/k8s-repo/k8s-deployment/ha/haproxy.cfg /etc/haproxy/haproxy.cfg
cp /root/k8s-repo/k8s-deployment/ha/keepalived.conf /etc/keepalived/keepalived.conf
cp /root/k8s-repo/k8s-deployment/ha/check_haproxy.sh /etc/keepalived/check_haproxy.sh
```

**Review and update** the configuration files /etc/haproxy/haproxy.cfg and /etc/keepalived/keepalived.conf, for the keepalived.conf, there is one MASTER and several BACKUP nodes, and the router_id is different for each node.

```
systemctl enable haproxy
systemctl start haproxy
systemctl enable keepalived
systemctl start keepalived
```

## Setup kubectl on the master nodes:

```
kubectl --server=http://9.12.246.195:8080  config set-cluster default-cluster --server=http://9.12.246.195:8080 --insecure-skip-tls-verify=true

kubectl config set-context default-context --cluster=default-cluster

kubectl config set current-context default-context
```

## Start kubernetes on one worker node

Select one worker node as the "template" for the other worker nodes, setup kubernetes on this selected worker node, then "clone" the configuration to the other worker nodes.

Copy the kubernetes binaries to the worker node

```
root@kube-master:~/k8s-repo/kubernetes-binaries/x86_64/1.6.2/kubernetes/server/bin# scp kubectl kube-proxy kubelet kube-worker1:/opt/bin/
root@kube-master:~/k8s-repo/kubernetes-binaries/x86_64/1.6.2/kubernetes/server/bin# ssh kube-worker1 "chmod 755 /opt/bin/kube*"
```

Copy the kubernetes configuration files to the worker node

```
root@kube-master:~/k8s-repo/k8s-deployment/systemd-files/etc/kubernetes#scp config kubelet proxy kube-worker1:/etc/kubernetes/
root@kube-master:~/k8s-repo/k8s-deployment/systemd-files/systemd/system#scp kube-proxy.service kubelet.service kube-worker1:/lib/systemd/system/
```

Setup kubectl on the worker node:

```
kubectl --server=http://9.12.246.195:8080  config set-cluster default-cluster --server=http://9.12.246.195:8080 --insecure-skip-tls-verify=true

kubectl config set-context default-context --cluster=default-cluster

kubectl config set current-context default-context
```

Review and update the kubernetes configuration files under /etc/kubernetes/ on the worker node. At least, the following attributes need to be updated:

**KUBE_MASTER** in config

**cluster_dns** in kubelet

**KUBE_PROXY_MASTER** in proxy


```
systemctl daemon-reload
for i in kubelet kube-proxy; do systemctl enable $i; systemctl stop $i; systemctl start $i; done
```

## Setup Calico

If flanned will be used, skip this step

### (Optional) configure docker with etcd cluster-store

This is required only when you will create docker containers outside of Kubernetes and need docker multi-host networking for these non-Kubernetes-managed containers.

As indicated at http://docs.projectcalico.org/v2.0/getting-started/docker/installation/requirements, to use Calico as a Docker network plugin, the Docker daemon must be configured with a cluster store. If using etcd as a cluster store, configure the cluster-store on the Docker daemon to etcd://<ETCD_IP>:<ETCD_PORT>, replacing <ETCD IP> and with the appropriate address and client port for your etcd cluster. 

Here is an example on Ubuntu:

```
root@c910f03c01p04:~# cat /etc/default/docker | grep DOCKER_OPTS
DOCKER_OPTS="--cluster-store etcd://10.3.1.4:2379
root@c910f03c01p04:~# 
```

### Run calico node on the worker node

```
docker load -i /root/k8s-repo/kubernetes-binaries/x86_64/calico/1.1.3/calico-node-v1.1.3-x86.tar
cp /root/k8s-repo/kubernetes-binaries/x86_64/calico/1.1.3/calicoctl /opt/bin/calicoctl
chmod 755 /opt/bin/calicoctl
cp /root/k8s-repo/kubernetes_binaries/calico/opt/cni/bin/{calico,calico-ipam,loopback} /opt/cni/bin/
chmod 755 /opt/cni/bin/*

cp /root/k8s-repo/k8s-deployment/systemd-files/etc/sysconfig/calico /etc/sysconfig/calico
cp /root/k8s-repo/k8s-deployment/systemd-files/systemd/system/calico.service /lib/systemd/system/calico.service
cp /root/k8s-repo/k8s-deployment/systemd-files/etc/cni/net.d/10-calico.conf /etc/cni/net.d/10-calico.conf
```

Review and update /etc/sysconfig/calico and /etc/cni/net.d/10-calico.conf, mainly the ETCD_ENDPOINTS
Review /lib/systemd/system/calico.service to make sure the image calico node image name and version are correct

```
systemctl daemon-reload
systemctl enable calico
systemctl start calico
```

To verify calico is working, use the calicoctl get nodes command. If the etcd is not running at 127.0.0.1:2379, use ETCD_ENDPOINTS to override. Here is an example:

```
root@x5:~# ETCD_ENDPOINTS="http://10.0.189.4:2379" calicoctl get nodes
NAME   
x5     

root@x5:~# 

```

**Note:** when no Kubernetes POD is launched, the ip route does not show the calico routes, the calico routes are added on-demand and only when required.

### (Optional) Update kubelet configuration

If the /etc/kubernetes/kubelet does not include the cni configuration, modify /etc/kubernetes/kubelet on all worker nodes

```
KUBELET_ARGS="--cluster_dns=20.254.0.10 --cluster-domain=cluster.local --network-plugin=cni --cni-conf-dir=/etc/cni/net.d --cni-bin-dir=/opt/cni/bin"

systemctl restart kubelet
```

## Add the other worker nodes

"Clone" the kubernetes/calico configuration on the "template" worker node to all the other worker nodes. See the /root/k8s-repo/k8s-deployment/scripts/setup_k8s_worker for more details about the steps, or, you could review and update the setup_k8s_worker and run it on all the other worker nodes.
  
**Note**: it is strongly recommended to run calico on the master node(s), a simple way is to add the master node(s) as worker node(s) and set the unschedulable node lable to the worker nodes, here is an example:

```
/root/k8s-repo/k8s-deployment/scripts/setup_k8s_worker
kubectl patch nodes kube-master -p '{"spec": {"unschedulable": true}}'
```
## (Optional) Load the docker images on the worker nodes

If the kubernetes cluster runs in a disconnected environment without internet access, you could either upload the kubernetes infrastructure images like pause, kube-dns, etc. to a local private registry or load the images on the workers nodes manually before running any kubernetes PODs. Here is an example of loading the docker images manually on the worker nodes:

```
docker load -i /root/k8s-repo/dockerimages/pause-amd64-3.0.tar
docker load -i /root/k8s-repo/dockerimages/calico-kube-policy-controller-0.6.0-amd64.tar
docker load -i /root/k8s-repo/dockerimages/kube-dnsmasq-amd64-1.4.1.tar
docker load -i /root/k8s-repo/dockerimages/kubedns-amd64-1.9.tar
docker load -i /root/k8s-repo/dockerimages/exechealthz-amd64-1.2.tar
docker load -i /root/k8s-repo/dockerimages/kubernetes-dashboard-amd64-v1.6.0.tar
docker load -i /root/k8s-repo/dockerimages/nginx-1.8.1.tar
docker load -i /root/k8s-repo/dockerimages/kubernetes-dashboard-amd64-v1.6.0.tar
docker load -i /root/k8s-repo/dockerimages/defaultbackend-amd64-1.3.tar
docker load -i /root/k8s-repo/dockerimages/nginx-ingress-controller-amd64-0.8.3.tar
```
## Run calico-kube-policy-controller

**Note**: the calico-kube-policy-controller needs to be run before the kube-dns or any other Kubernetes infrastructure PODs, it is required for the networking between PODs on differnet nodes

Modify the ETCD_ENDPOINTS in /root/k8s-repo/k8s-deployment/yaml-files/calico/policy-controller.yaml

```
kubectl create -f /root/k8s-repo/k8s-deployment/yaml-files/calico/policy-controller.yaml
```


## Setup kube-dns

```
kubectl create -f /root/k8s-repo/k8s-deployment/yaml-files/kube-dns/kubedns-deployment.yaml -f /root/k8s-repo/k8s-deployment/yaml-files/kube-dns/kubedns-svc.yaml
```

Make sure the kube-dns deployment is up and running correctly. Here is an example:

```
root@kube-master:~# kubectl get pods --namespace=kube-system | grep kube-dns
kube-dns-v20-1695022368-3fnd8                  3/3       Running   0          1h
root@kube-master:~# 
```

## Configure dashboard:

```
kubectl create -f /root/k8s-repo/k8s-deployment/yaml-files/dashboard/dashboard-controller.yaml -f /root/k8s-repo/k8s-deployment/yaml-files/dashboard/dashboard-service.yaml
```

## Run the sample nginx application to verify the cluster is setup correctly:

```
kubectl create -f /root/k8s-repo/k8s-deployment/yaml-files/nginx/nginx-nodeport.yaml
```

When the PODs are up and running:

* kubectl exec into one POD, verify:
  1) Could resolve the my-nginx service name
  2) Could access internet
* Verify the nginx service could be accessed at http://<kube-master-ip>:8080/api/v1/proxy/namespaces/default/services/my-nginx/
* Verify the port 30016 on all the worker nodes are accessible

## Setup nginx ingress controller

Please follow the instructions k8s-deployment/yaml-files/ingress/README.md to setup nginx ingress controller

## Setup helm

Download the helm release from https://github.com/kubernetes/helm/releases, for example, https://storage.googleapis.com/kubernetes-helm/helm-v2.4.0-linux-amd64.tar.gz

```
tar zxvf helm-v2.4.0-linux-amd64.tar.gz -C /usr/local/bin/ linux-amd64/helm --strip-components=1
```

Install socat on the node:

```
apt-get install socat
```

Initialize the helm environment

```
helm init
```

To verify helm is working correctly:

```
helm version
helm repo list
helm search
helm install stable/mysql --set persistence.enabled=false
helm list
```

## Setup Prometheus & Grafana

The kubernetes community already released helm charts for Prometheus and Grafana, so could use helm to install Prometheus and Grafana, here is an example without persistent volumes enabled:

```
helm install stable/prometheus --set alertmanager.persistentVolume.enabled=false,server.persistentVolume.enabled=false
helm install stable/grafana --set server.persistentVolume.enabled=false
```

## Setup cluster-level logging architectures

The proposal for cluster-level logging architectures include Elasticsearch, Logstash, Kibana, FileBeat, Kafka, Sysdig. The detailed procedure of setting up these components is on its way...
