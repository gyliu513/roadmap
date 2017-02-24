#!/bin/bash

echo `hostname-`v1 > /usr/share/nginx/html/index.html
nginx -g "daemon off;"
