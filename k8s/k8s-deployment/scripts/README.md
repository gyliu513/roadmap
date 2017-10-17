**xCAT postscripts to setup the Kubernetes workers**

Review the scripts and update the ip addresses and hostnames in the scripts before running the scripts on the Kubernetes workers.

Here is an example:

```
updatenode n06k01-n06k08 --noverify k8s/install_docker,k8s/install_conntrack,k8s/make_k8s_dirs,k8s/setup_k8s_worker,k8s/setup_calico,k8s/docker_load_images,k8s/sync_files,k8s/registry_keys
```
