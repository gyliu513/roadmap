```
root@gyliu-dev1:~/.kube# kind create cluster --name kubeflow
Creating cluster "kubeflow" ...
 ✓ Ensuring node image (kindest/node:v1.13.4) 🖼
 ✓ Preparing nodes 📦
 ✓ Creating kubeadm config 📜
 ✓ Starting control-plane 🕹️
Cluster creation complete. You can now use the cluster with:

export KUBECONFIG="$(kind get kubeconfig-path --name="kubeflow")"
kubectl cluster-info
```
