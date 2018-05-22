Get ID TOKEN.
```
ID_TOKEN=`curl -k -H "Content-Type: application/x-www-form-urlencoded;charset=UTF-8" -d "grant_type=password&username=admin&password=admin&scope=openid" https://9.111.255.26:8443/idprovider/v1/auth/identitytoken --insecure | jq -r .id_token`
```

Get nodes via `curl`.
```
root@gyliu-icp-6:~/scratch/istio# curl -H GET --header "Authorization: Bearer $ID_TOKEN" https://9.111.255.26:8001/api/v1/nodes  ?  -o /dev/null -s -w "time_connect: %{time_connect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\n"|grep time_total|awk -F ":"  '{print $2}'|head -n 1
 0.132
root@gyliu-icp-6:~/scratch/istio# curl -H GET --header "Authorization: Bearer $ID_TOKEN" https://9.111.255.26:8001/api/v1/nodes  ?  -o /dev/null -s -w "time_connect: %{time_connect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\n"|grep time_total|awk -F ":"  '{print $2}'|head -n 1
 0.096
```
