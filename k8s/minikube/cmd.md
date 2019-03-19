```
unset http_proxy no_proxy HTTP_PROXY NO_PROXY
```

```
minikube start --vm-driver kvm2
```
```
./generate-yaml.sh ./clouds-gyliu.yaml openstack ubuntu
```
```
./clusterctl create cluster --bootstrap-type minikube --bootstrap-flags kubernetes-version=v1.12.3 --provider openstack -c examples/openstack/out/cluster.yaml -m examples/openstack/out/machines.yaml -p examples/openstack/out/provider-components.yaml
```
```
minikube stop
```

```
minikube delete
```

Reference https://github.com/kubernetes/minikube/blob/master/docs/drivers.md
