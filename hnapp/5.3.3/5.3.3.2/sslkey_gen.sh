openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /tmp/tls.key -out /tmp/tls.crt -subj "/CN=tomcat.com"

echo "
apiVersion: v1
kind: Secret
metadata:
  name: tls
data:
  tls.crt: `base64 -w 0 /tmp/tls.crt`
  tls.key: `base64 -w 0 /tmp/tls.key`
" > ssl.yaml
