# Initializing Deployments Based On Metadata

It's possible to select which objects are initialized using metadata. In this section the Sidecar Initializer will be redeployed and configured to only initialize Deployments with an `initializer.kubernetes.io/sidecar` annotation set to a non-empty value.

## Prerequisites

Delete the existing `nginx` and `sidecar-initializer` Deployments:

```
kubectl delete deployments nginx sidecar-initializer
```

## Deploy the Sidecar Initializer

Deploy the Sidecar Initializer with the `-require-annotation` flag set. This will ensure the Sidecar container is only injected into Deployments with an `initializer.kubernetes.io/sidecar` annotation set to a non-empty value.

```
kubectl apply -f deployments/sidecar-initializer-with-annotation.yaml
```

Create the `nginx` Deployment:

```
kubectl apply -f deployments/nginx.yaml 
```

Notice the `nginx` Deployment has been initialized without injecting the Envoy proxy container:

```
kubectl get pods
```
```
NAME                                   READY     STATUS    RESTARTS   AGE
nginx-3993514419-k9wjp                 1/1       Running   0          2s
sidecar-initializer-1632551338-lg4hf   1/1       Running   0          13s
```

### Create the nginx-with-annotation Deployment

```
kubectl apply -f deployments/nginx-with-annotation.yaml
```

Notice the `nginx-with-annotation` Deployment has been initialized with the sidecar container:

```
kubectl get pods
```
```
NAME                                          READY     STATUS    RESTARTS   AGE
envoy-initializer-460025406-f56d4             1/1       Running   0          7m
helloworld-3116035291-6nl6x                   1/1       Running   0          6m
helloworld-with-annotation-3482720967-8b2qr   2/2       Running   0          6s
```
