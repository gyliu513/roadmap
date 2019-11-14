```
oc --config="$KUBECONFIG" get csr --no-headers | grep Pending | \
    awk '{print $1}' | \
    xargs --no-run-if-empty oc --config="$KUBECONFIG" adm certificate approve
```
