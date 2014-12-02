Volume Usage
==============================

.. contents:: Contents:
   :local: 

emptyDir
--------------

1. Manifest::

   apiVersion: v1beta1
   id: www
   desiredState:
     manifest:
       version: v1beta1
       id: www
       containers:
         - name: nginx
           image: dockerfile/nginx
           volumeMounts:
             - name: www-data
               mountPath: /srv/www
               readOnly: true
         - name: git-monitor
           image: kubernetes/git-monitor
           env:
             - name: GIT_REPO
               value: http://github.com/some/repo.git
           volumeMounts:
             - name: www-data
               mountPath: /data
       volumes:
         - name: www-data
           source:
             emptyDir: {}

2. Description::

   A content-manager container fills with data while a webserver container serves the data.

hostDir
--------------
 
1. Manifest::

   version: v1beta2
   id: cadvisor-agent
   containers:
     - name: cadvisor
       image: google/cadvisor:latest
       ports:
         - name: http
           containerPort: 8080
           hostPort: 4194
       volumeMounts:
         - name: varrun
           mountPath: /var/run
           readOnly: false
         - name: varlibdocker
           mountPath: /var/lib/docker
           readOnly: true
         - name: cgroups
           mountPath: /sys/fs/cgroup
           readOnly: true
   volumes:
     - name: varrun
       source:
         hostDir:
           path: /var/run
     - name: varlibdocker
       source:
         hostDir:
           path: /var/lib/docker
     - name: cgroups
       source:
         hostDir:
           path: /sys/fs/cgroup

2. Description::

   cadvisor need to read some data from docker server for showing them in dashboard.

