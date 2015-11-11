FROM ubuntu

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>

# Install JDK for ZooKeeper
#
RUN apt-get update && apt-get -y install openjdk-7-jre

ENV ZK_VER zookeeper-3.4.6
ENV ZK_URL http://apache.arvixe.com/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
ENV ZK_TAR zookeeper-3.4.6.tar.gz

ADD $ZK_URL /opt/$ZK_TAR

# Make soft link to /opt/zookeeper, so we did not need to change it
RUN tar zxvf /opt/$ZK_TAR -C /opt
ENV ZK_HOME /opt/zookeeper
RUN mv /opt/$ZK_VER $ZK_HOME
ENV PATH $ZK_HOME/bin:$PATH

RUN mkdir -p $ZK_HOME/logs

ADD bootstrap.sh $ZK_HOME/bin/
ADD log4j.properties $ZK_HOME/conf/
RUN chmod +x $ZK_HOME/bin/bootstrap.sh

RUN cp $ZK_HOME/conf/zoo_sample.cfg $ZK_HOME/conf/zoo.cfg

WORKDIR $ZK_HOME

ENTRYPOINT ["bootstrap.sh"]
