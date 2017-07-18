# Scale up/down Nginx application on scheduled time

* kubectl.tar The `siji/kubectl:v1.6.1` image, can be load by `docker load -i kubectl.tar`
* nginx.yaml The template to create Nginx deployment and service, can adjust the replicas and image name
* scale-up.yaml The template to create CronJob to scale up Nginx application
* scale-down.yaml The template to create CronJob to scale down Nginx application

## Steps

1. Create nginx app

	kubectl apply -f nginx.yaml

2. Watch nginx app

	kubectl get deployment nginx --watch

3. Create scale up cronjob

	kubectl apply -f scale-up.yaml

4. Create scale down cronjob

	kubectl apply -f scale-down.yaml
