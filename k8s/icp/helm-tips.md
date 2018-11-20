## Config helm client

```bash
export HELM_HOME=/root/.helm
cp ./cluster/cfc-certs/helm/admin.crt /root/.helm/cert.pem
cp ./cluster/cfc-certs/helm/admin.key /root/.helm/key.pem
helm init -c --skip-refresh
```
