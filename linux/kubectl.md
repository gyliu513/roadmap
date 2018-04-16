
## Replace cert
```
mkdir ~/.kube
cp /var/lib/kubelet/kubelet-config ~/.kube/config
sed -i -e 's/kubelet.crt/kubecfg.crt/' -e 's/kubelet.key/kubecfg.key/g' ~/.kube/config
kubectl -n kube-system get secrets
```

## Use option
```
kubectl --kubeconfig=/var/lib/kubelet/kubelet-config get nodes
```
