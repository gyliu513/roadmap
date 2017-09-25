# Kubernetes Initializers Deep Dive and Tutorial

It is recommended that you go through the blog https://ahmet.im/blog/initializers/ first before this tutorial, as this article is an extension of the previous one.

## PodPreset and Initializers
Someone may think that the PodPreset also support injecting data into Kubernetes resources files, why bother to have customized initializers which require the customer write their own initializer. Some discussion about this topic can be found [here in Kubernetes dev mail list](https://groups.google.com/forum/#!searchin/kubernetes-dev/podpreset|sort:relevance/kubernetes-dev/r-y00XVl5Ug/8shh6QOeCQAJhttps://groups.google.com/forum/#!searchin/kubernetes-dev/podpreset|sort:relevance/kubernetes-dev/r-y00XVl5Ug/8shh6QOeCQAJ)

Here are some takeaways from the above discussion:
1) Initializers themselves are actually just a special case of generic webhook admission - they exist to make it easy to take existing Kubernetes controller client code and handle common actions.  Making it easy to extend Kubernetes is important enough that we want many levels of flexibility.
2) Cluster admins need to be careful about what initializers they install due to a) A buggy one could block everyone's ability to create things in the cluster. b) The initializers have lots of power, so the code needs to be trusted.
3) PodPreset is a an initializer that someone wrote for you, which your cluster administrator can trust.
4) PodPreset represents the common "80%" use cases for initializers.  Not everyone should be required to write an initializer.

## How does initializers works
Basically, you may need three objects to make the initializer works:

### initializer: 
The initializer controller will observes the new uninitialized workload when it was created. It finds its configured initializer name as the first in the list of pending initializers.

Then the initializer checks to see if it was responsible for initializing the namespace of the workload. The initializer will ignore the workload if the initializer is not assumed to initialize the workload,  otherwise, it will try to the initialization work for the workload.

After the initialization work finished,  the initializer removes itself from the list of pending initializers for the workloads. 

### initializerConfigMap:
The configMap usually include some data for initializer, such as the injection data or some other configuration data of the initializer.

### initializerConfig:
The initializerConfig resource is used to configure what initializers are enabled and what resources are subject to the initializers.

You should first deploy the initializer and make sure that it is working properly before creating the initializerConfiguration. Otherwise, any newly created resources that configured in initializerConfig will be stuck in an uninitialized state and then timeout. Check here for how to workaround such issues.

You can have multiple initializers in your cluster and each initializer can focus on different tasks in different namespaces.

The following is a diagram which describes the relationship of the above three objects.


## Tutorial for initializers
My tutorial was based on https://github.com/kelseyhightower/kubernetes-initializer-tutorial , I updated it a bit by making it more simple and committed all of the code here https://github.com/gyliu513/jay-work/tree/master/k8s/example/kube-initializer-tutorial

Now we can go through the tutorial step by step and also try to see how to troubleshooting if you encounter some issues.

### Configuration
The `initializers` is an alpha feature for 1.7, so you need to enable it first.

Enable `admissionregistration.k8s.io/v1alpha1` for `runtime-config` and `Initializers` for `admission-control` in apiserver.

### Deploy the sidecar initializer configMap
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/configmaps# cat sidecar-initializer.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sidecar-initializer
data:
  config: |
    containers:
    - name: sidecar-nginx
      image: nginx:1.8.1
      imagePullPolicy: IfNotPresent
```
The configMap in the above only including container info that will be injected to the workloads. You can add more data here, such as volumes, sidecar initializer configuration etc.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/configmaps# kubectl apply -f ./sidecar-initializer.yaml
configmap "sidecar-initializer" created
```

### Deploy the sidecar initializer
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# cat sidecar-initializer.yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  initializers:
    pending: []
  labels:
    app: sidecar-initializer
  name: sidecar-initializer
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: sidecar-initializer
      name: sidecar-initializer
    spec:
      containers:
      - name: sidecar-initializer
        image: gcr.io/hightowerlabs/envoy-initializer:0.0.1
        imagePullPolicy: IfNotPresent
        args:
        - "-initializer-name=sidecar.initializer.kubernetes.io"
        - "-configmap=sidecar-initializer"
```
You may see that the `initializers` for above deployment is `[]` as following:

```
metadata:
  initializers:
    pending: []
```

The reason that we define it as above is because initializers should explicitly set the list of pending initializers to exclude itself, or to an empty array, to avoid getting stuck waiting to initialize. 

Set the list of pending initializers to exclude itself:
```
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  initializers:
    pending:
      - initializer.vaultproject.io
      # Do not include the Sidecar Initializer
      # - sidecar.initializer.kubernetes.io
  name: sidecar-initializer
```

Set the pending initializers to an empty array:
```
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  initializers:
    pending: []
```

Then deploy the sidecar deployment, using deployment can facilitate upgrades and auto restarts.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl apply -f ./sidecar-initializer.yaml
deployment "sidecar-initializer" created
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get pods
NAME                                   READY     STATUS    RESTARTS   AGE
sidecar-initializer-7f4767c77b-rnw4w   1/1       Running   0          6s
```

When an object is POSTed, it is checked against all existing initializerConfiguration objects (explained below). For all that it matches, all `spec.initializers[].names` are appended to the new object’s `metadata.initializers.pending` field.

An initializer controller should list and watch for uninitialized objects, by using the query parameter `?includeUninitialized=true`. If using client-go, just set `listOptions.includeUninitialized` to true.

Some fake code as following to describe the logic.
```
// Watch uninitialized Deployments in all namespaces.
restClient := clientset.AppsV1beta1().RESTClient()
watchlist := cache.NewListWatchFromClient(restClient, "deployments", corev1.NamespaceAll, fields.Everything())

// Wrap the returned watchlist to workaround the inability to include
// the `IncludeUninitialized` list option when setting up watch clients.
includeUninitializedWatchlist := &cache.ListWatch{
	ListFunc: func(options metav1.ListOptions) (runtime.Object, error) {
		options.IncludeUninitialized = true
		return watchlist.List(options)
	},
	WatchFunc: func(options metav1.ListOptions) (watch.Interface, error) {
		options.IncludeUninitialized = true
		return watchlist.Watch(options)
	},
}

resyncPeriod := 30 * time.Second

_, controller := cache.NewInformer(includeUninitializedWatchlist, &v1beta1.Deployment{}, resyncPeriod,
	cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			err := initializeDeployment(obj.(*v1beta1.Deployment), c, clientset)
			if err != nil {
				log.Println(err)
			}
		},
	},
)

stop := make(chan struct{})
go controller.Run(stop)

signalChan := make(chan os.Signal, 1)
signal.Notify(signalChan, syscall.SIGINT, syscall.SIGTERM)
<-signalChan

log.Println("Shutdown signal received, exiting...")
close(stop)
```

### Create the initializeConfig
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# cat sidecar.yaml
apiVersion: admissionregistration.k8s.io/v1alpha1
kind: InitializerConfiguration
metadata:
  name: sidecar
initializers:
- name: sidecar.initializer.kubernetes.io
  rules:
  - apiGroups:
    - "*"
    apiVersions:
    - "*"
    resources:
    - deployments
```
The above means that the sidecar initializer will only impact the deployment resources.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl apply -f ./sidecar.yaml
initializerconfiguration "sidecar" created
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl get initializerconfiguration
NAME      AGE
sidecar   5s
```

### Create an nginx application
Now let us create an nginx application to see if the sidecar can be injected to the nginx application.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# cat nginx.yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  labels:
    app: nginx
  name: nginx
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: nginx
      name: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.8.1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl apply -f ./nginx.yaml
deployment "nginx" created
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get pods
NAME                                   READY     STATUS    RESTARTS   AGE
nginx-f5f94b64-g95dx                   2/2       Running   0          4s
sidecar-initializer-7f4767c77b-rnw4w   1/1       Running   0          32m
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get pods nginx-f5f94b64-g95dx  -oyaml
...
spec:
  containers:
  - image: nginx:1.8.1
    imagePullPolicy: IfNotPresent
    name: nginx
    ports:
    - containerPort: 80
      protocol: TCP
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-5j13j
      readOnly: true
  - image: nginx:1.8.1
    imagePullPolicy: IfNotPresent
    name: sidecar-nginx
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: default-token-5j13j
      readOnly: true
...
```

From above, we can see that sidecar from the sidecar initializer configMap has been injected to the nginx application.

But there is a problem for this,  with above configurations, all of the deployments will be injected with sidecar, this may be not expected for some cases.

For such case, we can update the sidecar initializer to filter applications with specified annotations, using annotations to enable opting in or out of initialization.

Now let us delete the sidecar initializer, sidecar initializerConfig and nginx, then re-create the sidecar initializer with logic to filter out some deployments.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial# kubectl delete -f ./initializer-configurations/sidecar.yaml
initializerconfiguration "sidecar" deleted
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial# kubectl delete -f deployments/sidecar-initializer.yaml
deployment "sidecar-initializer" deleted
```

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial# kubectl delete -f deployments/nginx.yaml
deployment "nginx" deleted
```

### Re-deploy the sidecar initializer with annotation filter

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# cat sidecar-initializer-with-annotation.yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  initializers:
    pending: []
  labels:
    app: sidecar-initializer
  name: sidecar-initializer
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: sidecar-initializer
      name: sidecar-initializer
    spec:
      containers:
      - name: sidecar-initializer
        image: gcr.io/hightowerlabs/envoy-initializer:0.0.1
        imagePullPolicy: IfNotPresent
        args:
        - "-annotation=initializer.kubernetes.io/sidecar"
        - "-require-annotation=true"
        - "-initializer-name=sidecar.initializer.kubernetes.io"
        - "-configmap=sidecar-initializer"
```
You may see that we have added a new parameter named as `-annotation=initializer.kubernetes.io/sidecar` and this parameter will help check if the deployment does not include the required annotation, sidecar initializer will not inject data to the deployment.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl apply -f ./sidecar-initializer-with-annotation.yaml
deployment "sidecar-initializer" created
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get pods
NAME                                   READY     STATUS             RESTARTS   AGE
sidecar-initializer-5b7699577d-gp654   1/1       Running            0          4s
```

Some fake code as following for how to use `annotation` to filter out some applications:
```
if requireAnnotation {
	a := deployment.ObjectMeta.GetAnnotations()
	_, ok := a[annotation]
	if !ok {
		log.Printf("Required '%s' annotation missing; skipping envoy container injection", annotation)
		_, err = clientset.AppsV1beta1().Deployments(deployment.Namespace).Update(initializedDeployment)
		if err != nil {
			return err
		}
		return nil
	}
}
```

### Re-deploy the initializer config

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl apply -f ./sidecar.yaml
initializerconfiguration "sidecar" created
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl get initializerconfiguration
NAME      AGE
sidecar   5s
```

### Deploy the nginx without annotation

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl apply -f ./nginx.yaml
deployment "nginx" created
```

Due to above nginx do not include the annotation, so after the deployment was created, it will not have inject data.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get pods
NAME                                   READY     STATUS    RESTARTS   AGE
nginx-7ff795885f-pklsf                 1/1       Running   0          3s
sidecar-initializer-5b7699577d-gp654   1/1       Running   0          5m
```

From above output, we can see that the nginx include only one container, and no data was injected.

### Deploy an nginx with annotation
Now, let us deploy an nginx with annotation as following:
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# cat nginx-with-annotation.yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  annotations:
    "initializer.kubernetes.io/sidecar": "true"
  labels:
    app: nginx
    envoy: "true"
  name: nginx-with-annotation
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: nginx
        envoy: "true"
      name: nginx-with-annotation
    spec:
      containers:
      - name: nginx
        image: nginx:1.8.1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
``` 

From above, we can see that the deployment including an annotation as follows:
```
annotations:
    "initializer.kubernetes.io/sidecar": "true"
```

This means that sidecar initializer will inject data to this deployment.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl apply -f ./nginx-with-annotation.yaml
deployment "nginx-with-annotation" created
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get pods
NAME                                     READY     STATUS    RESTARTS   AGE
nginx-7ff795885f-pklsf                   1/1       Running   0          4m
nginx-with-annotation-5cf4d7fcdb-f7b9l   2/2       Running   0          2s
sidecar-initializer-5b7699577d-gp654     1/1       Running   0          9m
```

You can see the new created pod of nginx `nginx-with-annotation-5cf4d7fcdb-f7b9l` has two containers which means that the injection has take effect.

## Troubleshooting
Sometimes, you may found that you cannot deploy applications and all applications will be pending for about 30s and then timeout. For such kind of issue, it is usually caused by the initializerConfig if the sidecar initializer does not work.

Let us simulate the error case step by step.

### Delete the sidecar initializer
Till now, we have the initializer working well, now let's delete the sidecar initializer and both of the nginx, this will left a initializerConfig without initializer.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl delete -f ./sidecar-initializer-with-annotation.yaml
deployment "sidecar-initializer" deleted
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl delete -f ./nginx-with-annotation.yaml
deployment "nginx-with-annotation" deleted
```
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl delete -f ./nginx.yaml
deployment "nginx" deleted
```
No pods left.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get pods
No resources found.
```

The initializerConfig still exist.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get initializerconfigurations
NAME      AGE
sidecar   10m
```

### Create an nginx
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl apply -f ./nginx.yaml
Error from server (Timeout): error when creating "./nginx.yaml": Timeout: request did not complete within allowed duration
```
From above, we can see that the nginx create failed because of timeout.

Then I try to get the deployment, no deployment.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get deploy
No resources found.
```

But when I create the nginx deployment again, it failed!!
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl create -f ./nginx.yaml
Error from server (AlreadyExists): error when creating "./nginx.yaml": deployments.apps "nginx" already exists
```

### Get the uninitialized deploy
Check out more detail at here https://github.com/kubernetes/kubernetes/issues/51883 .

For such kind of issues, it was usually caused by the uninitialized objects, we can get all of the uninitialized objects by adding a flag named as `--include-uninitialized` to `kubectl`, such as `kubectl get deploy --include-uninitialized`.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/deployments# kubectl get deploy --include-uninitialized -oyaml
apiVersion: v1
items:
- apiVersion: extensions/v1beta1
  kind: Deployment
  metadata:
    annotations:
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1beta1","kind":"Deployment","metadata":{"annotations":{},"labels":{"app":"nginx"},"name":"nginx","namespace":"default"},"spec":{"replicas":1,"template":{"metadata":{"labels":{"app":"nginx"},"name":"nginx"},"spec":{"containers":[{"image":"nginx:1.8.1","imagePullPolicy":"IfNotPresent","name":"nginx","ports":[{"containerPort":80}]}]}}}}
    creationTimestamp: 2017-09-25T08:02:23Z
    generation: 1
    initializers:
      pending:
      - name: sidecar.initializer.kubernetes.io
    labels:
      app: nginx
    name: nginx
    namespace: default
    ...
```

You can see that above output includes the following:

```
initializers:
  pending:
  - name: sidecar.initializer.kubernetes.io
```

As I do not have such as initializer, so the deployment keeps pending.

### Resolve this issue

We need first delete the initializeConfig.

```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl delete -f ./sidecar.yaml
initializerconfiguration "sidecar" deleted
```

As the nginx deployment already include the `pending initializers`, so we need edit the deployment by removing the `pending initializers` and delete the deployment.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl edit deploy nginx  --include-uninitialized
deployment "nginx" edited
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl get deploy
NAME      DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
nginx     0         0         0            0           21m
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl delete deploy nginx
deployment "nginx" deleted
```

Then re-create the nginx deployment, it will be succeed.
```
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl apply -f ../deployments/nginx.yaml
deployment "nginx" created
root@k8s001:~/cases/jay-work/k8s/example/kube-initializer-tutorial/initializer-configurations# kubectl get pods
NAME                     READY     STATUS    RESTARTS   AGE
nginx-7ff795885f-gdzss   1/1       Running   0          2s
```

## Reference
- https://github.com/kubernetes/kubernetes/pull/50497 
- https://ahmet.im/blog/initializers/ 
- https://kubernetes.io/docs/admin/extensible-admission-controllers/
