
## Install Tips
```
root@gyliu-icp-6:~/cluster# docker run -e LICENSE=accept --net=host -it -v "$(pwd)":/installer/cluster registry.ng.bluemix.net/mdelder/icp-inception:latest bash
bash-4.3# cd /addon
bash-4.3# ls
auth-apikeys                heapster                    icp-management-ingress      metering                    platform-api                unified-router
auth-idp                    helm                        icp-mongodb                 metrics-server              platform-ui                 vulnerability-advisor
auth-pap                    helm-api                    istio                       monitoring                  rescheduler
auth-pdp                    ibm-custom-metrics-adapter  kube-dns                    nginx-ingress               security-onboarding
calico                      icp-catalog-chart           mariadb                     nsx-t                       service-catalog
bash-4.3# cd /installer/
bash-4.3# ls
ansible.cfg   cfc-files     cluster       images        installer.sh  playbook      plugins
```
