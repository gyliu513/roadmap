fdisk /dev/vdc

mkfs.xfs -i size=512 /dev/vdc1
mkdir -p /data/brick1
echo '/dev/vdc1 /data/brick1 xfs defaults 1 2' >> /etc/fstab
mount -a

yum install -y glusterfs-server

gluster peer probe 10.218.36.62
gluster peer probe 10.218.36.63

gluster peer status

for a in `seq 0 5`; do mkdir -p /data/brick1/vg$a; gluster volume create vg$a replica 2 10.218.36.62:/data/brick1/vg$a 10.218.36.63:/data/brick1/vg$a; gluster volume start vg$a;done

gluster volume info

