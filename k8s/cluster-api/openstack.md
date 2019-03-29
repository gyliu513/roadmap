```
apt-get purge docker.io
rm -rf /var/lib/docker
```
```
apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
```
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
```
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
```
```
## And then reinstall as

apt-get update && apt-get install docker-ce=18.06.0~ce~3-0~ubuntu
```

修改或创建/etc/docker/daemon.json，加入下面的内容：
```
Copy
{
  "exec-opts": ["native.cgroupdriver=systemd"]
}
```

```
docker_version=$(apt-cache policy docker.io | grep 18.06 | awk '{print $1}' | head -n1)
apt-get install -y docker.io=${docker_version}
```
```
--exec-opt native.cgroupdriver=systemd
```
