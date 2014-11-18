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
hostname $IP_ADDRESS.xip.io
cp /etc/hosts /acmeair/hosts
sed -i "1s/.*/$IP_ADDRESS container.$IP_ADDRESS.xip.io container/" /acmeair/hosts
cat /acmeair/hosts

echo "Catalog is $CATALOG_IP"
echo "$CATALOG_IP catalog.$CATALOG_IP.xip.io catalog" >> /acmeair/hosts

sed -i "s/localhost/catalog.$CATALOG_IP.xip.io/g" /acmeair/ObjectGrid/acmeair/env.sh
sed -i "s/127.0.0.1/catalog.$CATALOG_IP.xip.io/g" /acmeair/eclipse/acmeair/acmeair-services-wxs/src/main/resources/spring-config-acmeair-data-wxs-direct.xml
sed -i "s/127.0.0.1/catalog.$CATALOG_IP.xip.io/g" /acmeair/eclipse/acmeair/acmeair-services-wxs/src/main/resources/spring-config-acmeair-data-wxs-direct-notx.xml

cd /acmeair/eclipse/acmeair
mvn clean compile package install

OCTET4=$(ifconfig eth0 | grep -A2 "$INTERFACE " | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' | cut -f4 -d.)
echo $OCTET4 >> /var/log/acmeair.log
CONTAINER_NAME=C$OCTET4
echo $CONTAINER_NAME >> /var/log/acmeair.log

/acmeair/ObjectGrid/acmeair/runcontainer.sh $CONTAINER_NAME &

/usr/bin/supervisord
