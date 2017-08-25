# Initializing Deployments

In this section you will create an [InitializerConfiguration](https://kubernetes.io/docs/admin/extensible-admission-controllers/#configure-initializers-on-the-fly) that force new Deployments to be initialized by the Sidecar Initializer.

### Create the nginx deployment

```
kubectl apply -f deployments/nginx.yaml
```

Notice only one container is running in the `nginx` Pod:

```
kubectl get pods
```
```
NAME                                  READY     STATUS    RESTARTS   AGE
nginx-3993514419-k5z4z                1/1       Running   0          5s
sidecar-initializer-570644194-njmzb   1/1       Running   0          24s
```

### Create the Sidecar Initializer InitializerConfiguration

```
kubectl apply -f initializer-configurations/sidecar.yaml
```

At this point new Deployments will be initialized by the `sidecar-initializer`.

#### Test the Sidecar Initializer

Recreate the `nginx` Deployment:

```
kubectl delete deployment nginx
```

```
kubectl apply -f deployments/nginx.yaml
```

Notice there are now two containers running in the `nginx` Pod:

```
kubectl get pods
```
```
NAME                                   READY     STATUS    RESTARTS   AGE
nginx-91950620-jbfz2                   2/2       Running   0          2s
sidecar-initializer-3903237336-7whn6   1/1       Running   0          47s
```

The second container is the Sidecar container which was injected into the Pod by the Sidecar Initializer.

## Tutorial

* [1. Deploy The Sidecar Initializer](docs/deploy-sidecar-initializer.md)
* [2. Initializing Deployments](docs/initializing-deployments.md)
* [3. Initializing Deployments Based On Metadata](docs/initializing-deployments-based-on-metadata.md)
* [4. Cleaning Up](docs/cleanup.md)
* [5. Best Practices](docs/best-practices.md)
