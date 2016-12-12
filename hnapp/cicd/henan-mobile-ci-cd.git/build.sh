#!/bin/bash

token=$(cat /run/secrets/kubernetes.io/serviceaccount/token)
namespace=$(cat /run/secrets/kubernetes.io/serviceaccount/namespace)

APP_NAME=zhengzhou-poc-nginx
REPLICAS=1
APP_IMAGE=master.cfc:8500/$namespace/zhengzhou-poc-nginx
IMAGE_SECRET=${IMAGE_USER}.registrykey

# Build and Push Docker image
docker build -t $APP_IMAGE .
docker login -u $IMAGE_USER -p $IMAGE_PASS master.cfc:8500
docker push $APP_IMAGE
docker rmi -f $APP_IMAGE
docker logout master.cfc:8500

# Replace APP_NAME/REPLICAS/APP_IMAGE
sed -i -e 's%IMAGE_SECRET%'$IMAGE_SECRET'%g' \
    -e 's%APP_NAME%'$APP_NAME'%g' \
    -e 's%REPLICAS%'$REPLICAS'%g' \
    -e 's%APP_IMAGE%'$APP_IMAGE'%g' deployment.json service.json

# Create Application
curl -k -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token" \
    -d @deployment.json \
    https://$KUBERNETES_SERVICE_HOST/apis/extensions/v1beta1/namespaces/$namespace/deployments

# Create Service
curl -k -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token" \
    -d @service.json \
    https://$KUBERNETES_SERVICE_HOST/api/v1/namespaces/$namespace/services



