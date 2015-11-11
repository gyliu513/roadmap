#!/bin/bash

echo "FROM $HUB_USER/mesos" > Dockerfile
cat Dockerfile.template >> Dockerfile

sudo docker build -t $HUB_USER/marathon --no-cache .
