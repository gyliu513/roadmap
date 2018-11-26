REMOTE_IP=10.28.241.172
 
# Edit this variable: the bridge address on 'this' host.
BRIDGE_ADDRESS=172.17.42.1/24
 
# Name of the bridge (should match /etc/default/docker).
BRIDGE_NAME=docker0
 
# bridges
 
# Deactivate the docker0 bridge
ip link set $BRIDGE_NAME down
# Remove the docker0 bridge
brctl delbr $BRIDGE_NAME
# Delete the Open vSwitch bridge
ovs-vsctl del-br br0
# Add the docker0 bridge
brctl addbr $BRIDGE_NAME
# Set up the IP for the docker0 bridge
ip a add $BRIDGE_ADDRESS dev $BRIDGE_NAME
# Activate the bridge
ip link set $BRIDGE_NAME up
# Add the br0 Open vSwitch bridge
ovs-vsctl add-br br0
# Create the tunnel to the other host and attach it to the
# br0 bridge
ovs-vsctl add-port br0 gre0 -- set interface gre0 type=gre options:remote_ip=$REMOTE_IP
# Add the br0 bridge to docker0 bridge
brctl addif $BRIDGE_NAME br0
 
# iptables rules
 
# Enable NAT
iptables -t nat -A POSTROUTING -s 172.17.42.0/24 ! -d 172.17.42.0/24 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 172.17.41.0/24 ! -d 172.17.41.0/24 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 172.17.40.0/24 ! -d 172.17.40.0/24 -j MASQUERADE
# Accept incoming packets for existing connections
iptables -A FORWARD -o docker0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# Accept all non-intercontainer outgoing packets
iptables -A FORWARD -i docker0 ! -o docker0 -j ACCEPT
# By default allow all outgoing traffic
iptables -A FORWARD -i docker0 -o docker0 -j ACCEPT
 
# Restart Docker daemon to use the new BRIDGE_NAME
service docker restart
 
 
ovs-vsctl set bridge br0 stp_enable=true
route add -net 172.17.42.0/24 dev docker0
route add -net 172.17.41.0/24 dev docker0
route add -net 172.17.40.0/24 dev docker0
