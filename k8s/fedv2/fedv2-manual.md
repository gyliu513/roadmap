## Manual Deployment

If you'd like to understand what the script is automating for you, then proceed
by manually running the commands below.

### Deploy the Cluster Registry CRD

First you'll need to create the reserved namespace for registering clusters
with the cluster registry:

```bash
kubectl create ns kube-multicluster-public
```

Using this repo's vendored version of the [Cluster
Registry](https://github.com/kubernetes/cluster-registry), run the
following:

```bash
kubectl apply --validate=false -f vendor/k8s.io/cluster-registry/cluster-registry-crd.yaml
```

### Deploy Federation

First you'll need to create a permissive rolebinding to allow federation
controllers to run. This will eventually be made more restrictive, but for now
run:

```bash
kubectl create clusterrolebinding federation-admin --clusterrole=cluster-admin \
    --serviceaccount="federation-system:default"
```

If you do not have a namespace named as `federation-system`, create it as follows:

```bash
kubectl create ns federation-system
```

Now you're ready to deploy federation v2 using the existing YAML config. This
config creates RBAC resources, all the CRDs supported, along with the service
and statefulset for the federation-controller-manager.

```bash
kubectl -n federation-system apply --validate=false -f hack/install-latest.yaml
```

**NOTE:** The validation fails for harmless reasons on kube >= 1.11 so ignore validation
until `kubebuilder` generation can pass validation.

Verify that the deployment succeeded and is available to serve its API by
seeing if we can retrieve one of its API resources:

```bash
kubectl -n federation-system get federatedcluster
```

It should successfully report that no resources are found.

### Enabling Push Propagation

Configuration of push propagation is via the creation of
FederatedTypeConfig resources. To enable propagation for default
supported types, run the following command:

```bash
for f in ./config/federatedtypes/*.yaml; do
    kubectl -n federation-system apply -f "${f}"
done
```

Once this is complete, you now have a working federation-v2 control plane and
can proceed to join clusters.

### Join Clusters

Next, you'll want to use the `kubefed2` tool to join all your
clusters that you want to test against.

1. Build kubefed2
    ```bash
    go build -o bin/kubefed2 cmd/kubefed2/kubefed2.go

    ```
1. Join Cluster(s)
    ```bash
    ./bin/kubefed2 join cluster1 --cluster-context cluster1 \
        --host-cluster-context cluster1 --add-to-registry --v=2
    ./bin/kubefed2 join cluster2 --cluster-context cluster2 \
        --host-cluster-context cluster1 --add-to-registry --v=2
    ```
You can repeat these steps to join any additional clusters.

**NOTE:** `cluster-context` will default to use the joining cluster name if not
specified.

#### Check Status of Joined Clusters

Check the status of the joined clusters until you verify they are ready:

```bash
kubectl -n federation-system describe federatedclusters
```
