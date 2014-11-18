#!/bin/sh

# We need to start sshd once to generate the systems fingerprints
# Then in the supervisor conf file start sshd as the foreground process
service sshd start
service sshd stop

echo search xip.io >> /etc/resolv.conf

sleep 60

IFC=$(ifconfig | grep '^[a-z0-9]' | awk '{print $1}' | grep -e ns -e eth0)
IP_ADDRESS=$(ifconfig $IFC | grep 'inet addr' | awk -F : {'print $2'} | awk {'print $1'})
echo "This node has an IP of " $IP_ADDRESS
hostname web.$IP_ADDRESS.xip.io
cp /etc/hosts /acmeair/hosts
sed -i "1s/.*/$IP_ADDRESS web.$IP_ADDRESS.xip.io web/" /acmeair/hosts

echo "Catalog is $CATALOG_IP"
echo "$CATALOG_IP catalog.$CATALOG_IP.xip.io catalog" >> /acmeair/hosts
echo "export CATALOG_IP=$CATALOG_IP" > /root/.bash_profile

cat /acmeair/hosts

sed -i "s/127.0.0.1/catalog.$CATALOG_IP.xip.io/g" /acmeair/eclipse/acmeair/acmeair-services-wxs/src/main/resources/spring-config-acmeair-data-wxs-direct.xml
sed -i "s/127.0.0.1/catalog.$CATALOG_IP.xip.io/g" /acmeair/eclipse/acmeair/acmeair-services-wxs/src/main/resources/spring-config-acmeair-data-wxs-direct-notx.xml

# Recompile to refresh packages and stage war file
mvn clean compile package install
cp acmeair-webapp/target/acmeair-webapp-1.0-SNAPSHOT.war /acmeair/wlp/usr/servers/server1/dropins/

/usr/bin/supervisord
