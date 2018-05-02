## Test Tool
```
https://github.com/coreos/etcd/tree/master/tools/benchmark
```

## QPS1 test script
```
./benchmark --endpoints=https://10.29.103.167:4001,https://10.29.103.165:4001,https://10.29.103.166:4001 --key=/etc/cfc/conf/etcd/client-key.pem --cert=/etc/cfc/conf/etcd/client.pem --cacert=/etc/cfc/conf/etcd/ca.pem --conns=1 --clients=1 put --key-size=8  --sequential-keys --total=10000 --val-size=256
```

## QPS2 test script
```
./benchmark --endpoints=https://10.29.103.167:4001,https://10.29.103.165:4001,https://10.29.103.166:4001 --key=/etc/cfc/conf/etcd/client-key.pem --cert=/etc/cfc/conf/etcd/client.pem --cacert=/etc/cfc/conf/etcd/ca.pem --conns=100 --clients=1000 put --key-size=8  --sequential-keys --total=100000 --val-size=256
```
