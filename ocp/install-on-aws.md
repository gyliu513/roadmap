
Optional: Customize your deployment
Create the `install-config.yaml` file, providing any necessary configuration details when prompted:
```console
$ ./openshift-install create install-config --dir=<installation_directory>
```

```console
$ ./bin/openshift-install create install-config  --dir=/root/ocp41/ocp-config
? SSH Public Key /root/.ssh/id_rsa.pub
? Platform aws
? Region us-east-1
? Base Domain apps.opencloudops.io
? Cluster Name ocp41
? Pull Secret [? for help]
```

To customize your cluster, you can modify the install-config.yaml file to provide more details about the platform.

Installation configuration parameters for AWS 
Sample customized install-config.yaml file for AWS 
Customizing your network configuration 
Deploy the cluster
Deploy the cluster following the installer’s interactive prompt:
```console
$ ./openshift-install create cluster --dir=<installation_directory>
```

```console
$ ./bin/openshift-install create cluster --dir=/root/ocp41/ocp-config
INFO Consuming Install Config from target directory
INFO Creating infrastructure resources...
ERROR
ERROR Error: Error creating S3 bucket: TooManyBuckets: You have attempted to create more buckets than allowed
ERROR 	status code: 400, request id: E7EEEE95B523F775, host id: NylSLumm5XAGqjSa/G0Yhh/XYeNg5g+2hbYVUxzm8zUAwJjTi/R/RfMPWDLQe/bEcVjxBxkhtBE=
ERROR
ERROR   on ../../../../../../tmp/openshift-install-401972708/bootstrap/main.tf line 1, in resource "aws_s3_bucket" "ignition":
ERROR    1: resource "aws_s3_bucket" "ignition" {
ERROR
ERROR
FATAL failed to fetch Cluster: failed to generate asset "Cluster": failed to create cluster: failed to apply using Terraform
```

```console
$ openshift-install create cluster
INFO Waiting up to 30m0s for the Kubernetes API at https://api.test.example.com:6443...
INFO API v1.11.0+85a0623 up
INFO Waiting up to 30m0s for the bootstrap-complete event...
INFO Destroying the bootstrap resources...
INTO Waiting up to 30m0s for the cluster at https://api.test.example.com:6443 to initialize...
INFO Waiting up to 10m0s for the openshift-console route to be created...
INFO Install complete!
INFO To access the cluster as the system:admin user when using 'oc', run 'export KUBECONFIG=/home/user/auth/kubeconfig'
INFO Access the OpenShift web-console here: https://console-openshift-console.apps.test.example.com
INFO Login to the console with user: kubeadmin, password: 5char-5char-5char-5char
```

 Do you need to troubleshoot your installation?
Access Your Cluster
You can log into your cluster as a default system user by exporting the cluster kubeconfig file:
```console
$ export KUBECONFIG=<installation_directory>/auth/kubeconfig
```
```console
$ oc whoami
system:admin
```
Next Steps
Learn more  about the latest release of OpenShift Container Platform 4.
