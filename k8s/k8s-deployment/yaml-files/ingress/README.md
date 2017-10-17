yaml files to setup the Kubernetes nginx ingress controller and expose a backend nginx service in the Kubernetes cluster, see https://github.com/kubernetes/contrib/tree/master/ingress/controllers/nginx for more details.

## default http backend

Review the default-http-backend.yaml before creating the default http backend.

```
kubectl create -f default-http-backend.yaml
```

This is what the default backend does:

```
root@kube-master:~# kubectl get pod default-http-backend-2331281283-81pgj -o wide
NAME                                    READY     STATUS    RESTARTS   AGE       IP               NODE
default-http-backend-2331281283-81pgj   1/1       Running   0          4m        192.168.49.176   kube-worker2.sl.cloud9.ibm.com
root@kube-master:~# curl 192.168.49.176:8080/
default backend - 404
root@kube-master:~# 
root@kube-master:~# curl 192.168.49.176:8080/healthz
ok
root@kube-master:~# 

```

## nginx ingress controller

It is recommended to run nginx ingress controller as "hostNetwork" mode for performance and stability considerations. Review and update the nginx-ingress-controllers-hostnetwork.yaml before creating the nginx ingress controller, at least the following attributes need to be updated:

**nodeAffinity**


```
kubectl create -f nginx-ingress-controllers-hostnetwork.yaml
```

## create the my-nginx service to be exposed

```
kubectl create -f ../nginx/nginx.yaml
```

## ingress rules

Review the ingress-rules-nginx.yaml before creating the ingress rules, at least update **spec.rules.host**.

```
kubectl create -f ingress-rules-nginx.yaml
```

## Update /etc/hosts or DNS

Update /etc/hosts or DNS to point the FQDN in ingress-rules-nginx.yaml to the public ip address of the Kubernetes node in nginx-ingress-controllers.yaml, **9.12.246.27     my-nginx.poc.myvm.info** in this example.


## access the service through nginx ingress controller

```
root@kube-master:~# curl my-nginx.poc.myvm.info
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
root@kube-master:~# 
```

## An alternative

If you want to use the different postfix directories instead of the different hostnames for different services, you could update the ingress rules, here is an example:

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: my-nginx
spec:
  rules:
  - host: kube-worker1.sl.cloud9.ibm.com
    http:
      paths:
      - path: /my-nginx
        backend:
          serviceName: my-nginx
          servicePort: 8800

```

Please be aware that the **path** will be passed to the service itself, so you need to configure the my-nginx service to use the URL http://\<my-nginx-service-name\>/my-nginx

Here is a quick and dirty option, run the following commands against all PODs with my-nginx deployment:

```
root@kube-worker2:~# docker exec -it 2e4680934d62 /bin/bash
root@my-nginx-3864129975-v22bx:/# cd /usr/share/nginx/html
root@my-nginx-3864129975-v22bx:/usr/share/nginx/html# mkdir my-nginx
root@my-nginx-3864129975-v22bx:/usr/share/nginx/html# mkdir my-nginx
root@my-nginx-3864129975-v22bx:/usr/share/nginx/html# cp -f * my-nginx/
cp: omitting directory 'my-nginx'
root@my-nginx-3864129975-v22bx:/usr/share/nginx/html# 
```

Then access the service using the following URL:

```
root@kube-master:~/k8s-deployment/yaml-files/ingress# curl kube-worker1.sl.cloud9.ibm.com/my-nginx/
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
root@kube-master:~/k8s-deployment/yaml-files/ingress# 

```

## use https

**create SSL key and certificate**

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /root/yaml/ingress/tls.key -out /root/yaml/ingress/tls.crt -subj "/CN=kube-worker1.sl.cloud9.ibm.com
```

**create Kubernetes secret**

```
kubectl create secret tls my-nginx --key /root/yaml/ingress/tls.key --cert /root/yaml/ingress/tls.crt
```

**create the ingress rules**

```
kubectl create -f ingress-rules-nginx-tls.yaml
```

**access the service through https**

```
curl --cacert /root/yaml/ingress/tls.crt https://kube-worker1.sl.cloud9.ibm.com/my-nginx/index.html
```
