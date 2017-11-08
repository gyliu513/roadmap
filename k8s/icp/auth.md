## Using `bx pr` CLI to get authenticate against IBM Cloud Private

```
# bx pr login -u admin -p admin -a https://172.23.0.50:8443
 Login method invokedAPI endpoint: https://172.23.0.50:8443
Authenticating...
Post https://172.23.0.50:8443/idprovider/v1/auth/identitytoken: x509: cannot validate certificate for 172.23.0.50 because it doesn't contain any IP SANs

Password> [root@poc1 ~]# bx pr login -u admin -p admin -a https://172.23.0.50:8443  --skip-ssl-validation
 Login method invokedAPI endpoint: https://172.23.0.50:8443
Authenticating...
OK

Select an account:
1. ICP Account (f9a2432a320b2cf5ea206eb73e0001f9)
Enter a number> 1
Targeted account: ICP Account (f9a2432a320b2cf5ea206eb73e0001f9)


# bx pr tokens
Access token:  Bearer F8M2mfdhifJkWxUlCzwUZx5IKystYBtAd5ng1tEnrs4PSizOBp22aOxKOyt9pfAD4eYVNJYpJ10xKxjPssW2XmtFGB04ihBLY50mVibEk1u6A1sx8ulPQKYbxQIsJDzEjOuQWXqh5eq9oSuloEV1IKZq5uPGIkntgxvRsiigbQtwSnwnIoc7bc9xaCKHt4rkUQP2M0pXuxu5Rs3pxNYoFGQ2BhH5r4sfVX7vi2YzXT3w9GvQ3ef8pz7o1pcEpiMQlOdZNuajC0XvRTuxtb3TjJxyIZf0UDv54fedG5Y6i6aqKll0D3X39joSCeH35bUUKuUXzi21qsWK8AvsPZv270jYNGFmEZ1ujqFgyPi8DNd1hHx1QvCaolZGBRls0EpYy9ONx5jszf5HyBK3G8JRcNHdpua8y4SsmQJxiUDF2Na3ARF291gl6MmmcLwX2Tx5Rn9Pl6v1XwQd2XbUYHzOaO8HDH4y0o5TwPC7wvfLyHpRIAcjC0SvCqiXX4xr1k4aQrStoYbwPHDxh4i2DTXOi7iPGz6G6tHKwLm1bdaiRtyoiqp6fRqAyLDLqLb4eay77OyNx0bYDrf5tYeHC0qiRdxyUOAHi5PkQkJgOgZJdngOfR0tMJ8DCKgZVRe5rXpG3lnvupwil5WdrEiXfaNectRXQQaXnUwSBDS8znj4XWk8UrBc6hDXCaxYaChz5DSo1h8xPiLHqjoB1YaJZolCVJF8wDz5oLKRUYIwTyfYrW3gVUVXFmFgQnnxPTzo27uDyYUjrcetW56vRKad4dibL0uC5UFb8Qb7jCnTkf6pw9kEIa0L5VESKw0W8OClnuyGMuJAaJEqH1CzwClHpbar8PrFC9fllPhOQkAKk5GBBMnVXx2E4qYhasVaytsnSzVrNNtllMa48AZq8sffk2DM2dIxGgvvByKNOqGnPvKcLgCMqGhS0x1xvoTZkpndo1mtnaFVfIqASs2I1cHQKjTyROGKeKywPPkdKEJwEl2p
ID token:  eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoidDN6cWR4cDBzbHF6enF1ODdrOW0iLCJyZWFsbU5hbWUiOiJjdXN0b21SZWFsbSIsInVuaXF1ZVNlY3VyaXR5TmFtZSI6ImFkbWluIiwiaXNzIjoiaHR0cHM6Ly9jbHVzdGVyMS5pY3A6OTQ0My9vaWRjL2VuZHBvaW50L09QIiwiYXVkIjoiOTM4NWNiOGM1NzQ2ZTFkMzNjOTllNjE4ZDMxMzFhMjQiLCJleHAiOjE1MTAyMDgxNTUsImlhdCI6MTUxMDIwODE1NSwic3ViIjoiYWRtaW4ifQ.if-O-JjTOCU71-USAwgAFGkiPlW7F6F5chgaNxR5g9zywceY0sJYh8Zmw2i-d-87YW2JsyGc0Kgt0zh09Z_iQmagZinWTu_0Dx2Ddh4hnwqDH75LKMOV4n1QbqgJBmnQM5wQqQdtZrPh6Ky5jCF4h4RXRVkHf2Xta6up1o0NQy8z0jPJT5YB3Ii8Z9Q-4fz9ENG5EpQz_cE80P4NoqCbomfi9bfReuHpNjuFWZj9v2n3UA72aiPjE6nWgVIU88TAuHCxcM4YkboxOPQdWIDjymX5fncAogyg6pFeaqcl_oPC6G06wPbREeyk5o0ZQnKAU_KciXhyxUdqYI0_T189fg
```

You know can use `ID token` to access origin kubernetes API or other service API.

```
# curl -k -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoidDN6cWR4cDBzbHF6enF1ODdrOW0iLCJyZWFsbU5hbWUiOiJjdXN0b21SZWFsbSIsInVuaXF1ZVNlY3VyaXR5TmFtZSI6ImFkbWluIiwiaXNzIjoiaHR0cHM6Ly9jbHVzdGVyMS5pY3A6OTQ0My9vaWRjL2VuZHBvaW50L09QIiwiYXVkIjoiOTM4NWNiOGM1NzQ2ZTFkMzNjOTllNjE4ZDMxMzFhMjQiLCJleHAiOjE1MTAyMDgxNTUsImlhdCI6MTUxMDIwODE1NSwic3ViIjoiYWRtaW4ifQ.if-O-JjTOCU71-USAwgAFGkiPlW7F6F5chgaNxR5g9zywceY0sJYh8Zmw2i-d-87YW2JsyGc0Kgt0zh09Z_iQmagZinWTu_0Dx2Ddh4hnwqDH75LKMOV4n1QbqgJBmnQM5wQqQdtZrPh6Ky5jCF4h4RXRVkHf2Xta6up1o0NQy8z0jPJT5YB3Ii8Z9Q-4fz9ENG5EpQz_cE80P4NoqCbomfi9bfReuHpNjuFWZj9v2n3UA72aiPjE6nWgVIU88TAuHCxcM4YkboxOPQdWIDjymX5fncAogyg6pFeaqcl_oPC6G06wPbREeyk5o0ZQnKAU_KciXhyxUdqYI0_T189fg" https://172.23.0.50:8443/kubernetes/api/v1/namespaces
{
  "kind": "NamespaceList",
  "apiVersion": "v1",
  "metadata": {
    "selfLink": "/api/v1/namespaces",
    "resourceVersion": "103514"
  },
  "items": [
    {
      "metadata": {
        "name": "default",
        "selfLink": "/api/v1/namespaces/default",
        "uid": "a7631058-c3b0-11e7-9d35-005056b7586e",
        "resourceVersion": "14",
        "creationTimestamp": "2017-11-07T11:41:54Z"
      },
...
```

## Directly calling IBM Cloud Private auth api to get authentication token

```
# curl -k -X POST -H "Content-Type: application/x-www-form-urlencoded;charset=UTF-8" https://172.23.0.50:8443/idprovider/v1/auth/identitytoken -d "grant_type=password&username=admin&password=admin&scope=openid%20email%20profile"
{"access_token":"EkezKjB7Ljh2CBYavAMpQ5RTBJaoTPS1HL2T30vnlCgaQTQ8RVYEbyvYoLIg8QIgCzL6pwzNzmP4ziDVTXD44hORhSewF1jnWgZX1ebKT4lynEKfV9PHuAlqMhh6CF41GrXfWPgZAdiDNpPOU4i0V0brPNJxBIF6blZLn1nfCW4lUlhbLLVhls3yFtUo3C2cvcihbpPRUPy0eHjvfzFcyhOOD3azAKzzjLSQxjMyrkTMBGQagiWIkm2Vimgs38Mewy0dzJnR3T0df4IkQzTr3RcQrlDxkbzBeYLv6lMf3yPfhxghcFvQru9rkm53JeRGNbF8hTQVBSKKGCJDFsOYHjiDZF2GuoVyQmG39FgUNc27j40Vy5694BgazErPJrBk793OTL97hG1dr6ufCUbRlqX2mmm392VEP0BZZenyz7F143xExXgA7yrxLfXqkUSAbPb0H1KMkyV8IMELGflTjZNzX9bxqugsWKKu2lQgUQQRZ2VIIO0nUdH49Euwppdr52tTsb3ew8PGKif3hFTM8KG4sB4Hd0WlzSe9pgC2TS7gTGh0DKE80Mm0QqAMxg2zrrR90HM5Ob74kz6XAzjTZuk2hHDoGLWh8oDmTrxrPSr0K740MmSIK4xxIHqjMqgcBTF6t3rwAalnJ5tFnD8GshIKu9ASgBZNSCxB0VsLfzlMC2RcusRcQGdTovpOP5cFK3ZGxQWsMCoRve9HAsuLnS1b72r0NzkORsUDPwUTvO1rbQ99CbQbJaopEATzFTrcKDBY6VUGZW6gOSHnPalY48LJWIpnuoFJxYIiVmaUgbeeKScTAMpl43PUMYtumtx9or2C0hzFHeYIB9mrNEchUJn9ykCWqYOK5f2JfN1fqG3pK84AsWzA6v4OvdlEqpLNeBx7SLhzVLYJRxsm4daD9vqql7XmkSSqSQ8XfqTcSFkAGvKUcopCIRnxWZZtZb4U7NzuqCYhQqqWnUf4piA7YTZdRSe7wG16bwBftjFF","token_type":"Bearer","expires_in":43199,"scope":"openid profile email","refresh_token":"k3gdGZlFQo6FC7z2zneH3ey4cblBGtlzIHU8ISbvfuj2nqhsBn","id_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoicXMwdTZmZTI5NHYxODU3cGl2bnkiLCJyZWFsbU5hbWUiOiJjdXN0b21SZWFsbSIsInVuaXF1ZVNlY3VyaXR5TmFtZSI6ImFkbWluIiwiaXNzIjoiaHR0cHM6Ly9jbHVzdGVyMS5pY3A6OTQ0My9vaWRjL2VuZHBvaW50L09QIiwiYXVkIjoiOTM4NWNiOGM1NzQ2ZTFkMzNjOTllNjE4ZDMxMzFhMjQiLCJleHAiOjE1MTAyMDg2MTUsImlhdCI6MTUxMDIwODYxNSwic3ViIjoiYWRtaW4ifQ.ktnEeldsvJ5AwNiYs5KAYw2qVhnvSfMHm8IkQ3fESNnz-boibi-NfJ1BqpBxQ8gsJpLTmIq4FuuRSow2iYutoPRWYBQ0Lz_oVU1T45ZCqm0BTwSdaKrYzYGcof-vI7kTJHaMqVWadX679tr9vQ2P_lflOE8Uan93WXx2JikMWbCaz38bQzvNiqsLHBevDukLBiBU2eRCXefjcQjbp4ACLIV6QwDmNkmJv3KAyFbx9Az757DJb_E2K5UPxsq3j4T-eKne7FlgyRt2NWVzRw7thx41MHkqa4dcT4XqfzsHR4D2qHt1ujI8IjQ2Zg_l4m1S6shRkabF-MQ5CZcLxMp0ng"}
```

You now can try the ID token to call Kubernetes API.

```
# curl -k -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoicXMwdTZmZTI5NHYxODU3cGl2bnkiLCJyZWFsbU5hbWUiOiJjdXN0b21SZWFsbSIsInVuaXF1ZVNlY3VyaXR5TmFtZSI6ImFkbWluIiwiaXNzIjoiaHR0cHM6Ly9jbHVzdGVyMS5pY3A6OTQ0My9vaWRjL2VuZHBvaW50L09QIiwiYXVkIjoiOTM4NWNiOGM1NzQ2ZTFkMzNjOTllNjE4ZDMxMzFhMjQiLCJleHAiOjE1MTAyMDg2MTUsImlhdCI6MTUxMDIwODYxNSwic3ViIjoiYWRtaW4ifQ.ktnEeldsvJ5AwNiYs5KAYw2qVhnvSfMHm8IkQ3fESNnz-boibi-NfJ1BqpBxQ8gsJpLTmIq4FuuRSow2iYutoPRWYBQ0Lz_oVU1T45ZCqm0BTwSdaKrYzYGcof-vI7kTJHaMqVWadX679tr9vQ2P_lflOE8Uan93WXx2JikMWbCaz38bQzvNiqsLHBevDukLBiBU2eRCXefjcQjbp4ACLIV6QwDmNkmJv3KAyFbx9Az757DJb_E2K5UPxsq3j4T-eKne7FlgyRt2NWVzRw7thx41MHkqa4dcT4XqfzsHR4D2qHt1ujI8IjQ2Zg_l4m1S6shRkabF-MQ5CZcLxMp0ng" https://172.23.0.50:8443/kubernetes/api/v1/namespaces
{
  "kind": "NamespaceList",
  "apiVersion": "v1",
  "metadata": {
    "selfLink": "/api/v1/namespaces",
    "resourceVersion": "104055"
  },
  "items": [
    {
      "metadata": {
        "name": "default",
...
```

## Get application log with elasticsearch API

```
# curl -k -X POST -H "Accept: application/json, */*" -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoicXMwdTZmZTI5NHYxODU3cGl2bnkiLCJyZWFsbU5hbWUiOiJjdXN0b21SZWFsbSIsInVuaXF1ZVNlY3VyaXR5TmFtZSI6ImFkbWluIiwiaXNzIjoiaHR0cHM6Ly9jbHVzdGVyMS5pY3A6OTQ0My9vaWRjL2VuZHBvaW50L09QIiwiYXVkIjoiOTM4NWNiOGM1NzQ2ZTFkMzNjOTllNjE4ZDMxMzFhMjQiLCJleHAiOjE1MTAyMDg2MTUsImlhdCI6MTUxMDIwODYxNSwic3ViIjoiYWRtaW4ifQ.ktnEeldsvJ5AwNiYs5KAYw2qVhnvSfMHm8IkQ3fESNnz-boibi-NfJ1BqpBxQ8gsJpLTmIq4FuuRSow2iYutoPRWYBQ0Lz_oVU1T45ZCqm0BTwSdaKrYzYGcof-vI7kTJHaMqVWadX679tr9vQ2P_lflOE8Uan93WXx2JikMWbCaz38bQzvNiqsLHBevDukLBiBU2eRCXefjcQjbp4ACLIV6QwDmNkmJv3KAyFbx9Az757DJb_E2K5UPxsq3j4T-eKne7FlgyRt2NWVzRw7thx41MHkqa4dcT4XqfzsHR4D2qHt1ujI8IjQ2Zg_l4m1S6shRkabF-MQ5CZcLxMp0ng" https://172.23.0.50:8443/logstash*/_search -d @log_filter.json
{"took":15,"timed_out":false,"_shards":{"total":5,"successful":5,"failed":0},"hits":{"total":68875,"max_score":null,"hits":[{"_index":"logstash-2017.11.08","_type":"kube-logs","_id":"AV-aYjy2MmPOI40q44Bp","_score":null,"_source":{"log":"2017-11-08 06:47:25.145 [INFO][117] ipsets.go 297: Finished resync family=\"inet\" numInconsistenciesFound=0 resyncDuration=1.684206ms","time":"2017-11-08T06:47:25.145995759Z"},"sort":[1510123645145]},{"_index":"logstash-2017.11.08"
```

And here is elasticseach query spec,

```
# cat log_filter.json
{
  "from": 0,
  "size": 100,
  "_source": [
    "log",
    "time"
  ],
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "kubernetes.namespace": "kube-system"
          }
        },
        {
          "match": {
            "kubernetes.pod": "calico-policy-controller-1048521425-l2p0q"
          }
        },
        {
          "match": {
            "kubernetes.container_name": "calico-policy-controller"
          }
        }
      ]
    }
  },
  "sort": [
    {
      "time": {
        "order": "desc"
      }
    }
  ]
}
```
