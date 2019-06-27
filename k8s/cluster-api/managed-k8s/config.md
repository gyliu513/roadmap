```yaml
apiVersion: v1
data:
  config.yaml: |-
    default_admin_password: admin
    password_rules:
    - '.*'
    management_services:
      monitoring: disabled
      metering: disabled
      logging: disabled
      audit-logging: disabled
      custom-metrics-adapter: disabled
      platform-pod-security: disabled
      image-security-enforcement: disabled
kind: ConfigMap
metadata:
  name: cloudctlConfig
  namespace: default
```

```shell
kubectl create secret generic kubeconfig --from-file=kubeconfig=/root/.kube/config
```

```yaml
apiVersion: v1
data:
  kubeconfig: xxxxx
kind: Secret
metadata:
  name: kubeconfig
  namespace: default
type: Opaque
```
