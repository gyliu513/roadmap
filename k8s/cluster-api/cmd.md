```
unset http_proxy no_proxy HTTP_PROXY NO_PROXY
```

```
minikube start --vm-driver kvm2
```
```
./generate-yaml.sh ./clouds-gyliu.yaml openstack ubuntu
```
## Run with kube 1.12.3 + minikube
```
./clusterctl create cluster --v 10 --bootstrap-cluster-cleanup false --bootstrap-type minikube \
 --bootstrap-flags kubernetes-version=v1.12.3 --provider openstack \
 -c examples/openstack/out/cluster.yaml -m examples/openstack/out/machines.yaml \
 -p examples/openstack/out/provider-components.yaml
```

## Run with kube 1.13.4 + minikube
```
./clusterctl create cluster --v 10 --bootstrap-cluster-cleanup false --bootstrap-type minikube \
 --bootstrap-flags kubernetes-version=v1.13.4 --provider openstack \
 -c examples/openstack/out/cluster.yaml -m examples/openstack/out/machines.yaml \
 -p examples/openstack/out/provider-components.yaml
```

## Run with kind
```
./clusterctl create cluster --v 10 --bootstrap-cluster-cleanup false \
 --bootstrap-type kind --provider openstack \
 -c examples/openstack/out/cluster.yaml -m examples/openstack/out/machines.yaml \
 -p examples/openstack/out/provider-components.yaml
```

```
minikube stop
```

```
minikube delete
```

Reference https://github.com/kubernetes/minikube/blob/master/docs/drivers.md

```
minikube will upgrade the local cluster from Kubernetes 1.12.3 to 1.13.4
```

## How to use kind
```shell
export KUBECONFIG="$(kind get kubeconfig-path --name="kind")"
kubectl cluster-info
```
