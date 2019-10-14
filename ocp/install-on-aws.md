
Optional: Customize your deployment
Create the `install-config.yaml` file, providing any necessary configuration details when prompted:
```
./openshift-install create install-config --dir=<installation_directory>
```

To customize your cluster, you can modify the install-config.yaml file to provide more details about the platform.

Installation configuration parameters for AWS 
Sample customized install-config.yaml file for AWS 
Customizing your network configuration 
Deploy the cluster
Deploy the cluster following the installer’s interactive prompt:
```
./openshift-install create cluster --dir=<installation_directory>
```

 Do you need to troubleshoot your installation?
Access Your Cluster
You can log into your cluster as a default system user by exporting the cluster kubeconfig file:
```
export KUBECONFIG=<installation_directory>/auth/kubeconfig
```
```
oc whoami
system:admin
```
Next Steps
Learn more  about the latest release of OpenShift Container Platform 4.
