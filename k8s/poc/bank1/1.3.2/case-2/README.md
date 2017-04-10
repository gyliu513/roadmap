# Expose a tcp port

* redis.tar The `redis:3.2.8` image.
* redis-server.yaml The template file to create redis-server app

## Steps

1. Create redis-server app

	kubectl apply -f redis-server.yaml

2. Get the redis-server ports

	kubectl get service redis-server

	NAME           CLUSTER-IP   EXTERNAL-IP   PORT(S)          AGE
	redis-server   10.0.0.11    <nodes>       6379:30307/TCP   2h

3. The `30307` is nodeport of redis-server app, use this port and a worker ip address to connect

4. Set a key/value to redis-server app

	docker run --rm redis:3.2.8 redis-cli -h a_worker_ip -p 30307 set key1 value1

5. Get the value of key1

	docker run --rm redis:3.2.8 redis-cli -h a_worker_ip -p 30307 get key1
