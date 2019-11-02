```console
[root@bunnies-inf aws]# oc logs -f mycluster-0-4vqbn-provision-8fhbr
Error from server (BadRequest): a container name must be specified for pod mycluster-0-4vqbn-provision-8fhbr, choose one of: [installer cli hive]
[root@bunnies-inf aws]# oc get pods
ocNAME                                READY   STATUS      RESTARTS   AGE
hive-controllers-7db4fdf95b-4qtrd   1/1     Running     0          13m
hive-operator-645d68d9f-2bzpn       1/1     Running     1          21d
hiveadmission-68f5449f98-cbqlc      1/1     Running     0          13m
hiveadmission-68f5449f98-zqnqn      1/1     Running     0          13m
mycluster-0-4vqbn-provision-8fhbr   1/3     Running     0          2m4s
mycluster-imageset-q2h5w            0/2     Completed   0          2m21s
[root@bunnies-inf aws]# oc logs -f mycluster-imageset-q2h5w
Error from server (BadRequest): a container name must be specified for pod mycluster-imageset-q2h5w, choose one of: [release hiveutil]
[root@bunnies-inf aws]# oc logs -f mycluster-imageset-q2h5w -c release
About to run oc adm release info
installer image resolved successfully
cli image resolved successfully
[root@bunnies-inf aws]# oc logs -f mycluster-imageset-q2h5w -c hiveutil
time="2019-11-02T09:48:57Z" level=debug msg="starting to wait for success result"
time="2019-11-02T09:49:02Z" level=debug msg="contents of success file: 1"
time="2019-11-02T09:49:02Z" level=debug msg="the oc release info command was successful"
time="2019-11-02T09:49:02Z" level=debug msg="contents of installer-image.txt: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:f8a1e0d2263e8a21f2231f61b94ce25f7a6022b7281ed87ed63fdaf5a661ef6c"
time="2019-11-02T09:49:02Z" level=debug msg="contents of cli-image.txt: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:b212d6faabbe78e68af2894286741b892139bd612a5cf21bbbf7e66c7049b029"
time="2019-11-02T09:49:02Z" level=debug msg="fetching clusterdeployment" clusterdeployment=hive/mycluster
time="2019-11-02T09:49:02Z" level=debug msg="updating clusterdeployment status" clusterdeployment=hive/mycluster
[root@bunnies-inf aws]# oc logs -f mycluster-0-4vqbn-provision-8fhbr -c installer
'/bin/openshift-install' -> '/output/openshift-install.tmp'
'/output/openshift-install.tmp' -> '/output/openshift-install'
total 287000
drwxrwsrwx. 2 root       1000470000        31 Nov  2 09:49 .
drwxr-xr-x. 1 root       root              33 Nov  2 09:49 ..
-rwxr-xr-x. 1 1000470000 1000470000 293887936 Nov  2 09:49 openshift-install
[root@bunnies-inf aws]# oc logs -f mycluster-0-4vqbn-provision-8fhbr -c cli
'/usr/bin/oc' -> '/output/oc.tmp'
'/output/oc.tmp' -> '/output/oc'
total 359628
drwxrwsrwx. 2 root       1000470000        41 Nov  2 09:49 .
drwxr-xr-x. 1 root       root              47 Nov  2 09:49 ..
-rwxr-xr-x. 1 1000470000 1000470000  74368728 Nov  2 09:49 oc
-rwxr-xr-x. 1 1000470000 1000470000 293887936 Nov  2 09:49 openshift-install
```
