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

## Tutorial

* [1. Deploy The Sidecar Initializer](docs/deploy-sidecar-initializer.md)
* [2. Initializing Deployments](docs/initializing-deployments.md)
* [3. Initializing Deployments Based On Metadata](docs/initializing-deployments-based-on-metadata.md)
* [4. Cleaning Up](docs/cleanup.md)
* [5. Best Practices](docs/best-practices.md)
