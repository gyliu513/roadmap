# How to federate kubernetes application
[Kubefed](https://github.com/kubernetes-sigs/kubefed) allows you to coordinate the configuration of multiple Kubernetes clusters from a single set of APIs in a hosting cluster.

Kuberenetes [application](https://github.com/kubernetes-sigs/application)
is an CRD to describe an application metadata for a set of Kubernetes objects of one applicaiton.

Here is an example to federate an application object and its managed kubernetes objects to member clusters.
The `application` manages `statefulsets` and `services` for an wordpress application. The `application` controller will create `controllerrevisions.apps` for the application.
## Deploy kubefed
Follow up Kubefed [user guide](https://github.com/kubernetes-sigs/kubefed/blob/master/docs/userguide.md) to deploy kubefed control plane.
## Deploy application
Follow up Application [readme](https://github.com/kubernetes-sigs/application) to deploy kubernetes application CRD and controller.

## Federate resources
There is an application [example](https://raw.githubusercontent.com/kubernetes-sigs/application/master/docs/example.yaml) from kubernetes application github.
It is used as application for federation.
### download example yaml
```
wget https://raw.githubusercontent.com/kubernetes-sigs/application/master/docs/example.yaml
```

### create application in test namespace
```
kubectl create namespace test
kubectl config set-context --current --namespace=test
kubectl apply -f example.yaml
```

### enable federation of application and statefulsets.apps
```
kubefedctl enable applications.app.k8s.io
kubefedctl enable statefulsets.apps
```

### federate application resource objects
```
kubefedctl federate ns test --contents --skip-api-resources 'pods,secrets,serviceaccount,persistentvolumeclaims,controllerrevisions.apps'
```

# Example log
Cluster1 is the kubefed host cluster. The related operations runs in the context.
```
$ kubectl apply -f example.yaml
application.app.k8s.io/wordpress-01 created
service/wordpress-mysql-hsvc created
statefulset.apps/wordpress-mysql created
service/wordpress-webserver-svc created
service/wordpress-webserver-hsvc created
statefulset.apps/wordpress-webserver created

$ kubefedctl enable applications.app.k8s.io
customresourcedefinition.apiextensions.k8s.io/federatedapplications.types.kubefed.io created
federatedtypeconfig.core.kubefed.io/applications.app.k8s.io created in namespace kube-federation-system

$ kubefedctl enable statefulsets.apps
customresourcedefinition.apiextensions.k8s.io/federatedstatefulsets.types.kubefed.io created
federatedtypeconfig.core.kubefed.io/statefulsets.apps created in namespace kube-federation-system

$ kubefedctl federate ns test --contents --skip-api-resources 'pods,secrets,serviceaccount,persistentvolumeclaims,controllerrevisions.apps'
I0801 22:46:29.817205    5872 federate.go:459] Resource to federate is a namespace. Given namespace will itself be the container for the federated namespace
I0801 22:46:29.821240    5872 federate.go:488] Successfully created FederatedNamespace "test/test" from Namespace
I0801 22:46:29.824835    5872 federate.go:488] Successfully created FederatedStatefulSet "test/wordpress-mysql" from StatefulSet
I0801 22:46:29.846795    5872 federate.go:488] Successfully created FederatedStatefulSet "test/wordpress-webserver" from StatefulSet
I0801 22:46:29.861988    5872 federate.go:488] Successfully created FederatedApplication "test/wordpress-01" from Application
I0801 22:46:29.866095    5872 federate.go:488] Successfully created FederatedService "test/wordpress-mysql-hsvc" from Service
I0801 22:46:29.875984    5872 federate.go:488] Successfully created FederatedService "test/wordpress-webserver-hsvc" from Service
I0801 22:46:29.893507    5872 federate.go:488] Successfully created FederatedService "test/wordpress-webserver-svc" from Service

$ kubectl --context cluster2 -n test get application
NAME           AGE
wordpress-01   24m

$ kubectl --context cluster2 -n test get controllerrevisions.apps
NAME                             CONTROLLER                             REVISION   AGE
wordpress-mysql-79bd449444       statefulset.apps/wordpress-mysql       1          3m10s
wordpress-webserver-74bfc59df9   statefulset.apps/wordpress-webserver   1          3m5s
```
You can see that `controllerrevisions` is not federated but exists in `cluster2`.
