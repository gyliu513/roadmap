 
REMOTE_IP=10.28.241.175
# Create the tunnel to the other host and attach it to the
# br0 bridge
ovs-vsctl add-port br0 gre1 -- set interface gre1 type=gre options:remote_ip=$REMOTE_IP
 
service docker restart
