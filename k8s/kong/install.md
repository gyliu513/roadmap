## Install failed

- Set a default storageclass

```
storageclass.kubernetes.io/is-default-class: "true"
```

```
oc patch storageclass  rook-ceph-cephfs-internal  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

- Add permission

```
oc adm policy add-role-to-user admin xxx -n ns
```

- scc for all service accounts in kong namespace

```
oc adm policy add-scc-to-group anyuid system:serviceaccounts:kong
```
