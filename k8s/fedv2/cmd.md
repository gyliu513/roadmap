```
./bin/kubefed2 join cluster1 --cluster-context cluster138.k8s.local --host-cluster-context cluster138.k8s.local --add-to-registry --v=2
  ./bin/kubefed2 unjoin cluster1 --cluster-context cluster138.k8s.local --host-cluster-context cluster138.k8s.local --remove-from-registry --v=2
  ./bin/kubefed2 join cluster2 --cluster-context cluster141.k8s.local --host-cluster-context cluster138.k8s.local --add-to-registry --v=2
  ./bin/kubefed2 unjoin cluster2 --cluster-context cluster141.k8s.local --host-cluster-context cluster138.k8s.local --remove-from-registry --v=2
```
