gyliu@devstack007:~$ cat /etc/default/docker 
# Docker Upstart and SysVinit configuration file
 
# Customize location of Docker binary (especially for development testing).
#DOCKER="/usr/local/bin/docker"
 
# Use DOCKER_OPTS to modify the daemon startup options.
#DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"
DOCKER_OPTS="-H tcp://127.0.0.1:3128 -H unix:///var/run/docker.sock"
 
# If you need Docker to use an HTTP proxy, it can also be specified here.
#export http_proxy="http://127.0.0.1:3128/"
 
# This is also a handy place to tweak where Docker's temporary files go.
#export TMPDIR="/mnt/bigdrive/docker-tmp"
gyliu@devstack007:~$ cat /etc/heat/heat.conf | grep plugin
#plugin_dirs=/usr/lib64/heat,/usr/lib/heat
#plugin_dirs=/usr/local/lib/heat/docker
plugin_dirs=/opt/stack/heat/contrib/heat_docker/heat_docker/resources

heat create a1 --template-file=/home/gyliu/hadoop_heat/signal.autoscale.template 
