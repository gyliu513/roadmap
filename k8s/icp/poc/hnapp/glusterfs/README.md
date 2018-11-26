fdisk /dev/vdc

mkfs.xfs -i size=512 /dev/vdc1
mkdir -p /data/brick1
echo '/dev/vdc1 /data/brick1 xfs defaults 1 2' >> /etc/fstab
mount -a

yum install -y glusterfs-server

gluster peer probe 10.218.36.62
gluster peer probe 10.218.36.63

gluster peer status

for a in `seq 0 5`; do mkdir -p /data/brick1/vg$a; gluster volume create vg$a replica 3 10.218.36.77:/data/brick1/vg$a 10.218.36.78:/data/brick1/vg$a 10.218.36.79:/data/brick1/vg$a; gluster volume start vg$a; done

[root@bluedock51 vg0]# gluster volume info

Volume Name: vg0
Type: Replicate
Volume ID: 3086ded1-adb6-4dc6-86c8-b28b5ff66c6c
Status: Started
Number of Bricks: 1 x 2 = 2
Transport-type: tcp
Bricks:
Brick1: 10.218.36.51:/data/brick1/vg0
Brick2: 10.218.36.62:/data/brick1/vg0
Options Reconfigured:
performance.readdir-ahead: on

Volume Name: vg1
Type: Replicate
Volume ID: 652342fd-6cda-4070-92d8-b1e1433eddb3
Status: Started
Number of Bricks: 1 x 2 = 2
Transport-type: tcp
Bricks:
Brick1: 10.218.36.51:/data/brick1/vg1
Brick2: 10.218.36.62:/data/brick1/vg1
Options Reconfigured:
performance.readdir-ahead: on

Volume Name: vg2
Type: Replicate
Volume ID: be6b319c-9962-48e7-ba18-ad2b8ba10036
Status: Started
Number of Bricks: 1 x 2 = 2
Transport-type: tcp
Bricks:
Brick1: 10.218.36.51:/data/brick1/vg2
Brick2: 10.218.36.62:/data/brick1/vg2
Options Reconfigured:
performance.readdir-ahead: on



#If Create failed, execute below commands:
for a in `seq 0 5`; do setfattr -x trusted.glusterfs.volume-id /data/brick1/vg$a/; setfattr -x trusted.gfid /data/brick1/vg$a/; rm -rf /data/brick1/vg$a/.glusterfs; rm -rf /data/brock1/vg$a/.trashcan; done




gluster snapshot activate snapshot
gluster volume stop lv1
gluster snapshot restore snapshot
gluster volume start lv1

