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
root@k8s001:~/go/src/github.com/gyliu513/jay-work/k8s/example/kube-initializer-tutorial# kubectl get pods
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
NAME                                 READY     STATUS    RESTARTS   AGE
envoy-initializer-3840443721-bjfb4   1/1       Running   0          22m
helloworld-3012526715-zk5kg          2/2       Running   0          31s
```

The second container is the Sidecar container which was injected into the Pod by the Sidecar Initializer.
