FROM ubuntu:14.04

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>
MAINTAINER Yong Feng <yongfeng@ca.ibm.com>

# Install JDK for ZooKeeper
#
RUN apt-get update && apt-get -y install openjdk-7-jre supervisor

ENV ZK_VER zookeeper-3.4.6
ENV ZK_URL http://apache.arvixe.com/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
ENV ZK_TAR zookeeper-3.4.6.tar.gz

ADD $ZK_URL /opt/$ZK_TAR

# Make soft link to /opt/zookeeper, so we did not need to change it
RUN tar zxvf /opt/$ZK_TAR -C /opt
ENV ZK_HOME /opt/$ZK_VER
ENV PATH $ZK_HOME/bin:$PATH

RUN mkdir -p $ZK_HOME/logs

COPY ./bootstrap.sh $ZK_HOME/bin/
RUN chmod +x $ZK_HOME/bin/bootstrap.sh

COPY ./log4j.properties $ZK_HOME/conf/

RUN cp $ZK_HOME/conf/zoo_sample.cfg $ZK_HOME/conf/zoo.cfg

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["bootstrap.sh"]
