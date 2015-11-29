#!/bin/bash

wget --no-check-certificate https://lweb.eng.platformlab.ibm.com/engr/pcc/release_eng/work/sym/sym7.1.1/last/pssasetup2015_linux-x86_64.bin -O ./files/pssasetup2015_linux-x86_64.bin
chmod a+x ./files/pssasetup2015_linux-x86_64.bin

docker build -t mesostest/platform-asc:1.1.1 --no-cache .
