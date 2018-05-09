
Add a router
```
ip route add 20.1.198.128/26 via 9.111.255.21 dev tunl0 proto bird onlink
```

Delete a router
```
ip route del 10.1.31.128/26 dev tunl0
```

For Calico Mesh cross cluster
```
ip route add 10.121.0.0/16 via 10.23.220.76
```



