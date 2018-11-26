```
$ kubectl run -it --rm --restart=Never --image=infoblox/dnstools:latest dnstools
dnstools# dig @10.110.98.230 nginx.example.org +short 
10.0.2.15     
```
