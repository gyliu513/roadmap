kubectl scale --replicas=2 deployment/my-nginx


while [ 1 ]; do echo -n "`date +%M:%S`    "; kubectl get ep my-nginx| tail -n 1 | awk '{print $2}' ; sleep 1; done

nginx ingress controller:

kubectl logs -f nginx-ingress-controller-785588834-814bk | grep Reloading


nodeport:

while [ 1 ]; do echo -n "`date +%M:%S`    "; iptables -L -t nat -n  | grep my-nginx | grep "tcp to" | wc -l; sleep 1; done
 

4:03:02 PM: 认为service的ep出现算是容器正确运行了，这之后看nginx和nodeport是否更新 
