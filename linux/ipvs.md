```
[root@gyliu-centos-1 ~]# ipvsadm -A -t 9.111.255.240:80 -s rr
[root@gyliu-centos-1 ~]# ipvsadm -a -t 9.111.255.240:80 -r 9.111.255.32 -m
[root@gyliu-centos-1 ~]# ipvsadm -a -t 9.111.255.240:80 -r 9.111.255.167 -m
[root@gyliu-centos-1 ~]# ipvsadm -L -n --stats
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port               Conns   InPkts  OutPkts  InBytes OutBytes
  -> RemoteAddress:Port
TCP  9.111.255.240:80                    0        0        0        0        0
  -> 9.111.255.32:80                     0        0        0        0        0
  -> 9.111.255.167:80                    0        0        0        0        0
[root@gyliu-centos-1 ~]# ipvsadm -S -n > ipvsadm.conf
[root@gyliu-centos-1 ~]# cat ipvsadm.conf
-A -t 9.111.255.240:80 -s rr
-a -t 9.111.255.240:80 -r 9.111.255.32:80 -m -w 1
-a -t 9.111.255.240:80 -r 9.111.255.167:80 -m -w 1
[root@gyliu-centos-1 ~]# ipvsadm --clear^C
[root@gyliu-centos-1 ~]# ipvsadm -ln
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  9.111.255.240:80 rr
  -> 9.111.255.32:80              Masq    1      0          0
  -> 9.111.255.167:80             Masq    1      0          0
[root@gyliu-centos-1 ~]# ipvsadm -L -n --stats
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port               Conns   InPkts  OutPkts  InBytes OutBytes
  -> RemoteAddress:Port
TCP  9.111.255.240:80                    0        0        0        0        0
  -> 9.111.255.32:80                     0        0        0        0        0
  -> 9.111.255.167:80                    0        0        0        0        0
[root@gyliu-centos-1 ~]# ipvsadm --clear
[root@gyliu-centos-1 ~]# ipvsadm -L -n --stats
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port               Conns   InPkts  OutPkts  InBytes OutBytes
  -> RemoteAddress:Port
[root@gyliu-centos-1 ~]#
[root@gyliu-centos-1 ~]# ls
docker-ce-17.03.2.ce-1.el7.centos.x86_64.rpm  docker-ce-selinux-17.03.2.ce-1.el7.centos.noarch.rpm  ipvsadm.conf  rhel-server-7.4-x86_64-dvd.iso
[root@gyliu-centos-1 ~]# ipvsadm -R < ./ipvsadm.conf
[root@gyliu-centos-1 ~]# ipvsadm -ln
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  9.111.255.240:80 rr
  -> 9.111.255.32:80              Masq    1      0          0
  -> 9.111.255.167:80             Masq    1      0          0
```
