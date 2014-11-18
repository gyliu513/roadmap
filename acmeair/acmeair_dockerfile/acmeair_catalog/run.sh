#!/bin/sh

# We need to start sshd once to generate the systems fingerprints
# Then in the supervisor conf file start sshd as the foreground process
service sshd start
service sshd stop

sleep 10
IFC=$(ifconfig | grep '^[a-z0-9]' | awk '{print $1}' | grep -e ns -e eth0)
IP_ADDRESS=$(ifconfig $IFC | grep 'inet addr' | awk -F : {'print $2'} | awk {'print $1'})
echo "This node has an IP of " $IP_ADDRESS
hostname catalog.$IP_ADDRESS.xip.io
cp /etc/hosts /acmeair/hosts
sed -i "1s/.*/$IP_ADDRESS catalog.$IP_ADDRESS.xip.io catalog/" /acmeair/hosts
cat /acmeair/hosts

# Now start the Acme Air WebSphere eXtreme Scale configuration catalog server
# In one window start the catalog server
/acmeair/ObjectGrid/acmeair/runcat.sh &
sleep 30

# In another window start a single container server
/acmeair/ObjectGrid/acmeair/runcontainer.sh c0 &
sleep 30


# Now we will load sample data into eXtreme Scale
# In another window, we do this by running a Acme Air loader program
cd /acmeair/eclipse/acmeair/acmeair-loader
mvn exec:java &

/usr/bin/supervisord
