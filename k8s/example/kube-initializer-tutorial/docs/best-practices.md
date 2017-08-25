# Best Practices

The following list represents a set of best practices to follow when building Initializers.


* Initializers must have a unique fully qualified name. Examples:

```
initializer.vaultproject.io
sidecar.initializer.example.com
```
 
* Initializers should be deployed using a Deployment for easy upgrades and auto restarts.
* Initializers should explicitly set the list of pending initializers to exclude itself, or to an empty array, to avoid getting stuck waiting to initialize. Examples:

Set the list of pending initializers to exclude itself

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

* Limit the scope of objects to be initialized to the smallest subset possible using an InitializerConfiguration. Examples:

Limit the `sidecar.initializer.kubernetes.io` Initializer to Deployment objects:

```
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

* Use annotations to enable opting in or out of initialization. Examples:

Opting in using an annotation:

```
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  annotations:
    "initializer.kubernetes.io/sidecar": "true"
  labels:
    app: nginx
    envoy: "true"
  name: nginx-with-annotation
...
```
The complete [nginx-with-annotation deployment](https://raw.githubusercontent.com/gyliu513/jay-work/master/k8s/example/kube-initializer-tutorial/deployments/sidecar-initializer-with-annotation.yaml).

Use a flag on the Initializer to enable or disable an annotation to trigger initialization. See the [Sidecar Initializer](https://github.com/gyliu513/jay-work/tree/master/k8s/example/kube-initializer-tutorial/sidecar-initializer) for a complete example.

## Tutorial

* [1. Deploy The Sidecar Initializer](docs/deploy-sidecar-initializer.md)
* [2. Initializing Deployments](docs/initializing-deployments.md)
* [3. Initializing Deployments Based On Metadata](docs/initializing-deployments-based-on-metadata.md)
* [4. Cleaning Up](docs/cleanup.md)
* [5. Best Practices](docs/best-practices.md)
