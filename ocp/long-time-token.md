```console
[root@ocp42-inf ~]# oc get oauth cluster -o yaml
apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  annotations:
    release.openshift.io/create-only: "true"
  creationTimestamp: "2019-11-20T08:36:09Z"
  generation: 2
  name: cluster
  resourceVersion: "17300"
  selfLink: /apis/config.openshift.io/v1/oauths/cluster
  uid: ccf5c876-0b70-11ea-8ebb-00000a100178
spec:
  tokenConfig:
    accessTokenMaxAgeSeconds: 36000000
 ```
