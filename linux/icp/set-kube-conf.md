
## Set with credential data
```
kubectl config set-cluster cluster.2103.2 --server=https://9.111.255.121:8001 --insecure-skip-tls-verify=true
kubectl config set-context cluster.2103.2-context --cluster=cluster.2103.2
kubectl config set-credentials admin --client-certificate=$(cat /var/lib/kubelet/kubecfg.crt | base64 | tr -d '\n') --client-key==$(cat /var/lib/kubelet/kubecfg.key | base64 | tr -d '\n')
kubectl config set-context cluster.2103.2-context --user=admin --namespace=default
kubectl config use-context cluster.2103.2-context
```
