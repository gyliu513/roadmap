#!/bin/sh

check_rc () {
  echo $1
  echo $2
  if [ $1 -ne 0 ]
  then
    echo "$2 build failed"
    exit 1
  fi
}

/usr/bin/docker build -t acmeair/base base/

check_rc $? "acmeair/base"

/usr/bin/docker build -t acmeair/java java/

check_rc $? "acmeair/java"

/usr/bin/docker build -t acmeair/liberty liberty/

check_rc $? "acmeair/liberty"

/usr/bin/docker build -t acmeair/extremescale extremescale/

check_rc $? "acmeair/extremescale"

/usr/bin/docker build --no-cache=true -t acmeair/acmeair_base acmeair_base/

check_rc $? "acmeair/acmeair_base"

/usr/bin/docker build -t acmeair/acmeair_catalog acmeair_catalog/

check_rc $? "acmeair/acmeair_catalog"

/usr/bin/docker build -t acmeair/acmeair_webserver acmeair_webserver/

check_rc $? "acmeair/acmeair_webserver"

/usr/bin/docker build -t acmeair/acmeair_container acmeair_container/

check_rc $? "acmeair/acmeair_container"

exit 0
