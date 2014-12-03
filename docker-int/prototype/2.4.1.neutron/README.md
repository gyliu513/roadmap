#Apache Hadoop 2.4.1 Docker image


#pull the basement image
docker pull sequenceiq/hadoop-docker:2.4.1

# Build the image
If you'd like to try directly from the Dockerfile you can build the image as:

```
docker build -t="sequenceiq/hadoop-cluster-docker:2.4.1" .
```
# Start a container

```
# Start a container
docker run   --net=host  sequenceiq/hadoop-cluster-docker:2.4.1 $1 $2 $3 $4 $5 $6
Params definition as below:
$1:Hdfs port, such as 9000
$2:Hdfs DataNode port, such as 50010
$3:Type of Namenode or Datanode, such as N | D
$4:Number of hdfs replication, default is 1. Need more improvement for this param.
$5:Default command, run as service "-d", run as interactive "-bash"
$6:Master Node IP address, such as 10.28.241.174


#start name node
eg: docker run  -i -t --net=host sequenceiq/hadoop-cluster-docker:2.4.1 9001 50010 N 1 -bash 10.28.241.172 

#start data node
eg: docker run  -i -t --net=host sequenceiq/hadoop-cluster-docker:2.4.1 9001 50010 D 1 -bash 10.28.241.172 

```

## Testing
You can run one of the stock examples:
```
cd $HADOOP_PREFIX
# run the mapreduce
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-2.4.1.jar grep input output 'dfs[a-z.]+'

# check the output
bin/hdfs dfs -cat output/*
```
