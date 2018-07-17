```
./bin/kubefed2 join cluster1 --cluster-context cluster138.k8s.local --host-cluster-context cluster138.k8s.local --add-to-registry --v=2
```
```
./bin/kubefed2 unjoin cluster1 --cluster-context cluster138.k8s.local --host-cluster-context cluster138.k8s.local --remove-from-registry --v=2
```
```
./bin/kubefed2 join cluster2 --cluster-context cluster141.k8s.local --host-cluster-context cluster138.k8s.local --add-to-registry --v=2
```
```
./bin/kubefed2 unjoin cluster2 --cluster-context cluster141.k8s.local --host-cluster-context cluster138.k8s.local --remove-from-registry --v=2
```

```
kubectl describe cluster -n kube-multicluster-public
```
```
kubectl edit sts -n federation-system
```
```
kubectl apply -f example/sample1/federatednamespace-template.yaml \
    -f example/sample1/federatednamespace-placement.yaml
```
```
for r in configmaps secrets deploy; do
    for c in cluster138.k8s.local cluster141.k8s.local; do
        echo; echo ------------ ${c} ------------; echo
        kubectl --context=${c} -n test-namespace get ${r}
        echo; echo
    done
done
```
```
for r in deploy; do
    for c in cluster138.k8s.local cluster141.k8s.local; do
        echo; echo ------------ ${c} ------------; echo
        kubectl --context=${c} -n test-namespace get ${r}
        echo; echo
    done
done
```
```
kubectl -n test-namespace patch federatednamespaceplacement test-namespace \
    --type=merge -p '{"spec":{"clusternames": ["cluster1"]}}'
```
```
kubectl -n test-namespace patch federatednamespaceplacement test-namespace \
    --type=merge -p '{"spec":{"clusternames": ["cluster1", "cluster2"]}}'
```

```
go build -o images/federation-v2/controller-manager cmd/controller-manager/main.go
```
```
docker build images/federation-v2 -t gyliu513/federation-v2:test
```
```
docker save -o fed-2.tar gyliu513/federation-v2:test
```
```
kubectl delete pods -n federation-system federation-controller-manager-0
```
