# Federation DNS for Ingress and Service
This tutorial describes how to set up a federation cluster DNS with [ExternalDNS](https://github.com/kubernetes-incubator/external-dns/) based on [CoreDNS](https://github.com/coredns/coredns) in [minikube](https://github.com/kubernetes/minikube) clusters. You need to:
* install ExternalDNS with etcd enabled CoreDNS as a provider
* To support Ingress, enable [ingress controller](https://github.com/kubernetes/ingress-nginx) for your minikube clusters
* To support Service, install [metallab](https://github.com/google/metallb) for your minikube clusters  

You can support either Ingress or Service, or both of them in your clusters.


For related conceptions of Muilti-cluster Ingress and Service, you can refer to [ingressdns-with-externaldns.md](https://github.com/kubernetes-sigs/federation-v2/blob/master/docs/ingressdns-with-externaldns.md) and [servicedns-with-externaldns.md](https://github.com/kubernetes-sigs/federation-v2/blob/master/docs/servicedns-with-externaldns.md).

## Creating federation clusters
Install Federation-v2 with minikube in [User Guide](https://github.com/kubernetes-sigs/federation-v2/blob/master/docs/userguide.md)

## Installing ExternalDNS
Install ExternalDNS with CoreDNS as backend in your host cluster. You can follow the [tutorial](https://github.com/kubernetes-incubator/external-dns/blob/master/docs/tutorials/coredns.md)

To make it work for federation resources, you need to use below ExternalDNS deployment instead of the tutorial one.  
**Note**: You should replace value of ETCD_URLS with your own etcd client service IP address.
```
$ cat external-dns.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
  namespace: kube-system
spec:
  strategy:
    type: Recreate
  selector:
    matchLabels:                                                                 
      app: external-dns
  template:
    metadata:
      labels:
        app: external-dns
    spec:
      containers:
      - name: external-dns
        image: registry.opensource.zalan.do/teapot/external-dns:latest
        args:
        - --source=crd
        - --crd-source-apiversion=multiclusterdns.federation.k8s.io/v1alpha1
        - --crd-source-kind=DNSEndpoint
        - --registry=txt
        - --provider=coredns
        - --log-level=debug # debug only
        env:
        - name: ETCD_URLS
          value: http://10.102.147.224:2379

$ kubectl apply -f external-dns.yaml
```
## Enable DNS for federation resource
### Installing metellb for Service
Install metallb in each member clusters to make LoadBanlancer type Service work.
```
$ helm --kube-context cluster1 install --name metallb stable/metallb
$ helm --kube-context cluster2 install --name metallb stable/metallb
```
Apply federation configmap to configure metallb in each cluster.
```
$ cat federatedconfigmap-placement.yaml
apiVersion: core.federation.k8s.io/v1alpha1
kind: FederatedConfigMapPlacement
metadata:
  name: metallb-config
spec:
  clusterNames:
  - cluster2
  - cluster1
$ cat federatedconfigmap-template.yaml
apiVersion: core.federation.k8s.io/v1alpha1
kind: FederatedConfigMap
metadata:
  name: metallb-config
spec:
  template:
    data:
      config: |
        peers:
        - peer-address: 10.0.0.1
          peer-asn: 64501
          my-asn: 64500
        address-pools:
        - name: default
          protocol: bgp
          addresses:
          - 192.168.20.0/24

$ kubectl apply -f federatedconfigmap-template.yaml -f federatedconfigmap-placement.yaml
```
### Creating service resources
After metallb works, create sample deployment and service from [sample](https://github.com/kubernetes-sigs/federation-v2/blob/master/docs/ingressdns-with-externaldns.md). Make service as LoadBalancer type.
```
sed -i 's/NodePort/LoadBalancer/' example/sample1/federatedservice-template.yaml
```

Create ServiceDNSRecord to make DNS work for service.
```
$ cat <<EOF | kubectl create -f -
apiVersion: multiclusterdns.federation.k8s.io/v1alpha1
kind: Domain
metadata:
  # Corresponds to <federation> in the resource records.
  name: test-domain
  # The namespace running federation-controller-manager.
  namespace: federation-system
# The domain/subdomain that is setup in your externl-dns provider.
domain: example.org
---
apiVersion: multiclusterdns.federation.k8s.io/v1alpha1
kind: ServiceDNSRecord
metadata:
  # The name of the sample service.
  name: test-service
  # The namespace of the sample deployment/service.
  namespace: test-namespace
spec:
  # The name of the corresponding `Domain`.
  domainRef: test-domain
  recordTTL: 300
EOF
```
### Enable the ingress controller
```
$ minikube -p cluster1 addons enable ingress
$ minikube -p cluster2 addons enable ingress
```

After enable ingress, create sample deployment, service and ingress from [sample](https://github.com/kubernetes-sigs/federation-v2/blob/master/docs/ingressdns-with-externaldns.md). Make ingress with "example.org" for this tutorial example.
```
sed -i 's/example.com/example.org/' example/sample1/federatedingress-template.yaml
```

### Creating ingress resources
Create IngressDNSRecord to make DNS work for ingress.
```
$ cat <<EOF | kubectl create -f -
apiVersion: multiclusterdns.federation.k8s.io/v1alpha1
kind: IngressDNSRecord
metadata:
  name: test-ingress
  namespace: test-namespace
spec:
  hosts:
  - ingress.example.org
  recordTTL: 300
EOF
```

## DNS Example
Wait a moment until DNS has the ingress/service IP. The DNS service IP is from CoreDNS service. It is "my-coredns-coredns" in this example.
```
$ kubectl get svc my-coredns-coredns
NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
my-coredns-coredns   ClusterIP   10.100.4.143   <none>        53/UDP    12m

$ kubectl run -it --rm --restart=Never --image=infoblox/dnstools:latest dnstools
dnstools# dig @10.104.68.86 test-service.test-namespace.test-domain.svc.example.org +short
192.168.19.0
dnstools# dig @10.104.68.86 ingress.example.org +short
10.0.2.15
dnstools#
```
