# Install glusterfs in ICP

## Have a extra disk or partition for glusterfs

```
# fdisk -l

Disk /dev/vda: 214.7 GB, 214748364800 bytes, 419430400 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x0009f7fc

   Device Boot      Start         End      Blocks   Id  System
/dev/vda1            2048   419430399   209714176   83  Linux

Disk /dev/vdb: 42.9 GB, 42949672960 bytes, 83886080 sectors
Units = sectors of 1 * 512 = 512 bytes
```

As you see from `fdisk -l` command, we have secondary disk `/dev/vdb` for glusterfs. 
Now create partition on the disk and change it to `Linux LVM` System.

```
fdisk /dev/vdb
```

Here is the final result,

```
# fdisk -l

Disk /dev/vda: 214.7 GB, 214748364800 bytes, 419430400 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x0009f7fc

   Device Boot      Start         End      Blocks   Id  System
/dev/vda1            2048   419430399   209714176   83  Linux

Disk /dev/vdb: 42.9 GB, 42949672960 bytes, 83886080 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x609638d3

   Device Boot      Start         End      Blocks   Id  System
/dev/vdb1            2048    83886079    41942016   8e  Linux LVM
```

Heketi will use LVM to manage the gluster volume. So the disk/partition **MUST** be `Linux LVM` System.

Erase all file system, raid, and partition-table signatures by using the wipefs command. For example, to erase the signatures on device /dev/sdb, run the following command:

```
 sudo wipefs --all --force /dev/sdb
 ```
 
Get the symlink of the device by entering this command:

```
 ls -altr /dev/disk/*
```

## Update `config.yaml` to enable glusterfs

```
glusterfs: true

storage:
 - kind: glusterfs
   nodes:
     - ip: 172.23.0.6
       device: /dev/disk/by-id/virtio-a800c35b-337b-4e13-a-part1
     - ip: 172.23.0.7
       device: /dev/disk/by-id/virtio-580ae41e-3d3e-4459-8-part1
     - ip: 172.23.0.8
       device: /dev/disk/by-id/virtio-09ab7245-c56b-4f23-b-part1
   storage_class:
     name: demo-storage
     default: true
```

## Install ICP

```
docker run --net host -e LICENSE=accept -v "$(pwd)/cluster":/installer/cluster -t ibmcom/icp-inception:2.1.0-ee install
```

# Remove glusterfs when uninstall ICP
## Uninstall ICP
```
docker run --net host -e LICENSE=accept -v "$(pwd)/cluster":/installer/cluster -t ibmcom/icp-inception:2.1.0-ee uninstall
```

## Remove glusterfs and heketi data/log dir

```
rm -rf /etc/glusterfs /var/log/glusterfs /var/lib/glusterd /var/lib/heketi
```

## Remove lvm for glusterfs volume

```
# lvdisplay
  --- Logical volume ---
  LV Name                tp_1c26cd3b226c4b0fe9844c8729786a91
  VG Name                vg_9ac08216d9066fb3e7618becb4c27565
  LV UUID                DOrPlc-cPg3-5wZ6-dIXX-f0lb-xKPK-CC4FV5
  LV Write Access        read/write
  LV Creation host, time demo06, 2017-11-04 12:46:24 +0800
  LV Pool metadata       tp_1c26cd3b226c4b0fe9844c8729786a91_tmeta
  LV Pool data           tp_1c26cd3b226c4b0fe9844c8729786a91_tdata
  LV Status              available
  # open                 2
  LV Size                2.00 GiB
  Allocated pool data    0.71%
  Allocated metadata     0.33%
  Current LE             512
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     8192
  Block device           252:12

  --- Logical volume ---
  LV Path                /dev/vg_9ac08216d9066fb3e7618becb4c27565/brick_1c26cd3b226c4b0fe9844c8729786a91
  LV Name                brick_1c26cd3b226c4b0fe9844c8729786a91
  VG Name                vg_9ac08216d9066fb3e7618becb4c27565
  LV UUID                nH6MvF-CUJa-gLcC-ejQr-reeF-530w-Q1DyQ3
  LV Write Access        read/write
  LV Creation host, time demo06, 2017-11-04 12:46:24 +0800
  LV Pool name           tp_1c26cd3b226c4b0fe9844c8729786a91
  LV Status              available
  # open                 1
  LV Size                2.00 GiB
  Mapped size            0.71%
  Current LE             512
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     8192
  Block device           252:14
```

Remove them all

```
# lvremove /dev/vg_9ac08216d9066fb3e7618becb4c27565/brick_d46faaab3fa28a2529dc7d4a515b5d95
```

## Remove vg for glusterfs volume

```
# vgs
  VG                                  #PV #LV #SN Attr   VSize  VFree
  vg_9ac08216d9066fb3e7618becb4c27565   1   6   0 wz--n- 39.87g <27.78g
```

Remove vg,

```
# vgremove vg_9ac08216d9066fb3e7618becb4c27565
```

## Remove pv for glusterfs volume

```
# pvs
  PV         VG                                  Fmt  Attr PSize  PFree
  /dev/vdb1  vg_9ac08216d9066fb3e7618becb4c27565 lvm2 a--  39.87g <27.78g
```

Remove pv,

```
# pvremove /dev/vdb1
```
