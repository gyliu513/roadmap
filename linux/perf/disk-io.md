
```
fio -filename=/tmp/test_randread -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=sync -bs=8k -size=2G -numjobs=10 -runtime=60 -group_reporting -name=mytest
```
