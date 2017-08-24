# Cleaning Up

The following commands will delete the Kubernetes objects associated with this tutorial.

```
kubectl delete initializerconfiguration sidecar
```

```
kubectl delete deployment sidecar-initializer nginx nginx-with-annotation
```

```
kubectl delete clusterrolebindings cluster-admin-for-configmap
```

```
kubectl delete configmaps sidecar-initializer
```
