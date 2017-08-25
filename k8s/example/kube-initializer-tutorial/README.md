# Kubernetes Initializer Tutorial ![SuperDopeBadge](https://img.shields.io/badge/Hightower-super%20dope-b9f2ff.svg)

This tutorial walks you through building and deploying a [Kubernetes Initializer](https://kubernetes.io/docs/admin/extensible-admission-controllers/#what-are-initializers) that injects a sidecar container into uninitialized Deployments. 

> Initializers are an alpha feature and subject to change. Please report any Initializer specific issues on the [Kubernetes issue tracker](https://github.com/kubernetes/kubernetes/issues).

## Prerequisites

Kubernetes 1.7.0+ is required with [support for Initializers enabled](https://kubernetes.io/docs/admin/extensible-admission-controllers/#enable-initializers-alpha-feature). If you're using Google Container Engine create an alpha cluster:

```
gcloud alpha container clusters create k0 \
  --enable-kubernetes-alpha \
  --cluster-version 1.7.0
```

Download the tutorial by cloning this repository:

```
git clone https://github.com/gyliu513/jay-work.git
```

```
cd jay-work/k8s/example/kube-initializer-tutorial
```

## Tutorial

* [1. Deploy The Sidecar Initializer](docs/deploy-sidecar-initializer.md)
* [2. Initializing Deployments](docs/initializing-deployments.md)
* [3. Initializing Deployments Based On Metadata](docs/initializing-deployments-based-on-metadata.md)
* [4. Cleaning Up](docs/cleanup.md)
* [5. Best Practices](docs/best-practices.md)
