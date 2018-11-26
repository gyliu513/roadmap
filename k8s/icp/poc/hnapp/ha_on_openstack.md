### Create a port for vip


```openstack port create vip-port --network={private_network_name}```

### Update port for all ports of master vm, this update should be done for every master vm.

Use ```neutron port-list``` to get the port id for each master vm

```neutron port-update {port id for each master vm} --allowed_address_pairs list=true type=dict ip_address={ip address of vip-port}```

Note: port-update must be run under admin project role.

### Associate vip port to a floating ip

Use ```neutron floatingip-list``` to get the floatin_ip_id to use.

``` neutron floatingip-associate {floatin_ip_id} {vip_port_id}```
