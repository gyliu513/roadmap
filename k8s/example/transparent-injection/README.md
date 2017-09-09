## Transparent injection for istio

## NOTE
The sidecar-initializer:0.2.1 does not work, I have build one myself and pushed it to my dockerhub here `gyliu/sidecar_initializer:0909`, the `istio-sidecar-initializer` deployment is using my build for this demo.

## Pre-conditions

Have Kubernetes 1.7.3 and istio 0.2.1 installed.

isito 2.1 is running well.
```
root@pc002:~/cases/init# kubectl get pods -owide
NAME                             READY     STATUS    RESTARTS   AGE       IP            NODE
istio-egress-425999992-gjjwj     1/1       Running   0          24m       10.1.72.100   9.21.60.43
istio-ingress-1327524770-vlb6b   1/1       Running   0          24m       10.1.73.98    9.21.62.122
istio-mixer-130005935-bpdgj      2/2       Running   0          24m       10.1.73.97    9.21.62.122
istio-pilot-1248573728-ks63b     1/1       Running   0          24m       10.1.72.99    9.21.60.43
```

## Test Steps


### 1. Create configMap for sidecar-initializer

`namespaces`: All of the `deployment` in those namespace will be impacted by the sidecar-initializer.

```
root@pc002:~/cases/init# cat cm.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio-inject
data:
  config: |-
    namespaces:
    - kube-system
    - default
    - kube-public
    params:
      initImage: "docker.io/istio/proxy_init:0.2.1"
      proxyImage: "docker.io/istio/proxy_debug:0.2.1"
      MeshConfigMapName: "istio"
```

Create the config map.
```
root@pc002:~/cases/init# kubectl apply -f ./cm.yaml
configmap "istio-inject" configured
```

### 2. Deploy the sidecar-initializer.

```
root@pc002:~/cases/init# cat initializer.yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: istio-sidecar-initializer
  initializers:
    pending: []
  labels:
    istio: istio-sidecar-initializer
spec:
  replicas: 1
  template:
    metadata:
      name: istio-sidecar-initializer
      labels:
        istio: sidecar-initializer
    spec:
      containers:
        - name: sidecar-initializer
          image: gyliu/sidecar_initializer:0909
          imagePullPolicy: IfNotPresent
          args:
            - --port=8083
            - -v=2
          volumeMounts:
          - name: config-volume
            mountPath: /etc/istio/config
      volumes:
      - name: config-volume
        configMap:
          name: istio
```

Deploy the initializer.

```
root@pc002:~/cases/init# kubectl apply -f ./initializer.yaml
deployment "istio-sidecar-initializer" created
```

### 3. Create InitializerConfiguration

`InitializerConfiguration` will define which resource will be impacted by the sidecar-initializer. The following config means only `deployment` will be impacted by the initializer.

```
root@pc002:~/cases/init# cat initconfig.yaml
apiVersion: admissionregistration.k8s.io/v1alpha1
kind: InitializerConfiguration
metadata:
  name: istio-sidecar
initializers:
  - name: sidecar.initializer.istio.io
    rules:
      - apiGroups:
          - "*"
        apiVersions:
          - "*"
        resources:
          - deployments # e2e test only uses deployments
```

Create the `InitializerConfiguration`
```
root@pc002:~/cases/init# kubectl apply -f ./initconfig.yaml
initializerconfiguration "istio-sidecar" created
```

### 4. Check sidecar-initializer status.
```
2017-09-09 02:44:43.547536 I | proto: duplicate proto type registered: google.protobuf.Timestamp
NAME                                         READY     STATUS    RESTARTS   AGE       IP            NODE
istio-egress-425999992-gjjwj                 1/1       Running   0          28m       10.1.72.100   9.21.60.43
istio-ingress-1327524770-vlb6b               1/1       Running   0          28m       10.1.73.98    9.21.62.122
istio-mixer-130005935-bpdgj                  2/2       Running   0          28m       10.1.73.97    9.21.62.122
istio-pilot-1248573728-ks63b                 1/1       Running   0          28m       10.1.72.99    9.21.60.43
istio-sidecar-initializer-1430767161-1t4gv   1/1       Running   0          43s       10.1.72.107   9.21.60.43
```

### 5. Run BookInfo - NO `istioctl kube-inject` anymore!!

```
root@pc002:~/cases/init# kubectl apply -f istio-0.2.1/samples/apps/bookinfo/bookinfo.yaml
service "details" created
deployment "details-v1" created
service "ratings" created
deployment "ratings-v1" created
service "reviews" created
deployment "reviews-v1" created
deployment "reviews-v2" created
deployment "reviews-v3" created
service "productpage" created
deployment "productpage-v1" created
ingress "gateway" created
```

### 6. Check bookinfo status
All pods for bookinfo are running.
```
root@pc002:~/cases/init# kubectl get pods -owide
NAME                                         READY     STATUS    RESTARTS   AGE       IP            NODE
details-v1-2162502517-vb6h7                  1/1       Running   0          45s       10.1.73.102   9.21.62.122
istio-egress-425999992-gjjwj                 1/1       Running   0          29m       10.1.72.100   9.21.60.43
istio-ingress-1327524770-vlb6b               1/1       Running   0          29m       10.1.73.98    9.21.62.122
istio-mixer-130005935-bpdgj                  2/2       Running   0          29m       10.1.73.97    9.21.62.122
istio-pilot-1248573728-ks63b                 1/1       Running   0          29m       10.1.72.99    9.21.60.43
istio-sidecar-initializer-1430767161-1t4gv   1/1       Running   0          2m        10.1.72.107   9.21.60.43
productpage-v1-3246585699-4kl6x              1/1       Running   0          44s       10.1.72.110   9.21.60.43
ratings-v1-3807623045-8m8ft                  1/1       Running   0          45s       10.1.72.108   9.21.60.43
reviews-v1-1607762320-1bzxz                  1/1       Running   0          45s       10.1.73.103   9.21.62.122
reviews-v2-3177644196-p5vsx                  1/1       Running   0          44s       10.1.72.109   9.21.60.43
reviews-v3-2293581772-q9q7b                  1/1       Running   0          44s       10.1.73.104   9.21.62.122
```

Get ingress server and port
```
root@pc002:~/cases/init# kubectl get pods -owide | grep ingress
istio-ingress-1327524770-vlb6b               1/1       Running   0          30m       10.1.73.98    9.21.62.122
root@pc002:~/cases/init# kubectl get svc | grep ingress
istio-ingress   10.0.0.94    <pending>     80:30818/TCP,443:31955/TCP                               30m
```

Confirm that the BookInfo application is running with the following curl command:
```
root@pc002:~/cases/init# curl -o /dev/null -s -w "%{http_code}\n" http://9.21.62.122:30818/productpage
200
```
