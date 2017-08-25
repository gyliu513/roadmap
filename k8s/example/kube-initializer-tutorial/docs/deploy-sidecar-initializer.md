# Deploy The Sidecar Initializer

The Sidecar Initializer is a [Kubernetes Initializer](https://kubernetes.io/docs/admin/extensible-admission-controllers/#what-are-initializers) that injects asidecar container into Deployments based on containers defined in a [ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap).

## Install

### Create the Sidecar Initializer ConfigMap 

The Sidecar Initializer is configured using a ConfigMap, identified by the `-configmap` flag, which provides the containers and volumes to inject into a Deployment. Create the `sidecar-initializer` ConfigMap:

```
kubectl apply -f configmaps/sidecar-initializer.yaml
```

### Create the ClusterRoleBinding

The `ClusterRoleBinding` is needed to make sure the user `system:serviceaccount:default:default` have permission to get data from configmap `sidecar-initializer`. 

```
kubectl apply -f rbac/bindings.yaml
```

### Create the Sidecar Initializer Deployment

Deploy the `sidecar-initializer` controller:

```
kubectl apply -f deployments/sidecar-initializer.yaml
```

The `sidecar-initializer` Deployment sets pending initializers to an empty list which bypasses initialization. This prevents the Sidecar Initializer from getting stuck waiting for initialization, which can happen if the `sidecar` [Initialization Configuration](initializing-deployments.md#create-the-sidecar-initializer-InitializerConfiguration) is created before the `sidecar-initializer` Deployment.

```
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  initializers:
    pending: []
```

At this point the Sidecar Initializer is ready to initialize new Deployments.

## Tutorial

* [1. Deploy The Sidecar Initializer](docs/deploy-sidecar-initializer.md)
* [2. Initializing Deployments](docs/initializing-deployments.md)
* [3. Initializing Deployments Based On Metadata](docs/initializing-deployments-based-on-metadata.md)
* [4. Cleaning Up](docs/cleanup.md)
* [5. Best Practices](docs/best-practices.md)
