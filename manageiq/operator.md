```
operator-sdk new manageiq-operator
operator-sdk add api --api-version=manageiq.org/v1alpha1 --kind=Manageiq
operator-sdk generate k8s
operator-sdk generate crds
operator-sdk add controller --api-version=manageiq.org/v1alpha1 --kind=Manageiq
```
