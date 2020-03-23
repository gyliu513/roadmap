## Install failed

- Set a default storageclass

```
storageclass.kubernetes.io/is-default-class: "true"
```

```
oc patch storageclass rook-ceph-block-internal -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

- Add permission

```
oc adm policy add-role-to-user admin xxx -n ns
```
