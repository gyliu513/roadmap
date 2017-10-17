#!/bin/bash

# etcd
cp -af /etc/sysconfig/etcd etc/sysconfig/
cp -af /usr/lib/systemd/system/etcd.service usr/lib/systemd/system/

# flanneld
cp -af /etc/sysconfig/flanneld* etc/sysconfig/
cp -af /usr/lib/systemd/system/flanneld.service usr/lib/systemd/system/

# Docker
cp -af /usr/lib/systemd/system/docker.service usr/lib/systemd/system/

# Kubernetes
cp -af /etc/kubernetes/* etc/kubernetes
cp -af /usr/lib/systemd/system/kube* usr/lib/systemd/system/
