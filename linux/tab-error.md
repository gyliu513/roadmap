## ubuntu下按tab键出现warning: setlocale: LC_CTYPE: cannot change locale (zhCN.UTF-8";)的解决办法

 
```
vi /etc/profile
# Add follows
export LC_ALL=C
```
