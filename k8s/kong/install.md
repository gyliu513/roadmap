## Install failed

- Set a default storageclass

```
storageclass.kubernetes.io/is-default-class: "true"
```

- Add permission

```
oc adm policy add-role-to-user admin xxx -n ns
```
