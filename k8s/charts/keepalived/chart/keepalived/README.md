# Service LoadBalancer Helm Chart

## Prerequisites

`ipvs` module is required by the vip manager.

Make sure that the ip_vs module is loaded.

```
# lsmod| grep ^ip_vs
```

If no `ip_vs` module is loaded, install `ipvsadm`

```console
# yum -y install ipvsadm

# ipvsadm -ln
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn

# lsmod | grep ^ip_vs
ip_vs                 145497  0
```

## Installing the Chart

To install the chart with the release name `my-release`:

```console
$ helm install --name my-release --namespace my-namespace chart/keepalived
```

## Uninstalling the Chart

To uninstall/delete the my-release deployment:

```console
$ helm delete --purge my-release
```

The command removes all the Kubernetes resources associated with the chart and deletes the release.

## Configuration

The following tables lists the configurable parameters of the Prometheus chart and their default values.

Parameter                                       | Description                              | Default
----------------------------------------------- | ---------------------------------------- | -------
`imagePullPolicy`                               | image pull policy                        | IfNotPresent
`imagePullSecrets`                              | image pull secret                        | None
`nodeSelector`                                  | node selector of keepalived load balancer| None
`tolerations`                                   | toleration of keepalived load balancer   | None
`keepalivedCloudProvider.image.repository`      | image repository name of keepalived cloud provider | quay.io/munnerz/keepalived-cloud-provider
`keepalivedCloudProvider.image.tag`             | image tag name of keepalived cloud provider | 0.0.1
`keepalivedCloudProvider.resources`             | resource request/limit of keepalived cloud provider | {}
`keepalivedCloudProvider.serviceIPRange`        | service IP range of external cloud provider | 192.168.1.0/24
`keepalivedVIPManager.image.repository`         | image repository name of keepalived VIP manager | gcr.io/google_containers/kube-keepalived-vip
`keepalivedVIPManager.image.tag`                | image tag name of keepalived VIP manager | 0.9
`keepalivedVIPManager.resources`                | resource request/limit of keepalived VIP manager | {}
