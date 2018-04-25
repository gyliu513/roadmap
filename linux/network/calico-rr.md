```console
ETCDCTL_API=3 etcdctl get --keys-only --prefix /
```

Check RR cfg
```console
docker exec f9cfec29f202 cat /config/bird.cfg
```

Check calico node cfg
```console
docker exec 7c880107e28f  cat /etc/calico/confd/config/bird.cfg
```
