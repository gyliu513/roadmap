FROM klaus1982/mesos

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>

## Install OpenJDK 8
RUN apt-get update
RUN apt-get install -y python-software-properties software-properties-common
RUN add-apt-repository -y ppa:openjdk-r/ppa

RUN apt-get update

RUN apt-get -y install openjdk-8-jdk

RUN update-java-alternatives -s $(update-java-alternatives -l | grep "java-1.8" | cut -f3 -d" ")

WORKDIR /opt

ADD http://downloads.mesosphere.com/marathon/v0.11.1/marathon-0.11.1.tgz /opt/

RUN tar zxvf marathon-0.11.1.tgz

ENV MESOS_NATIVE_JAVA_LIBRARY $MESOS_HOME/lib/libmesos.so

WORKDIR /opt/marathon-0.11.1

COPY log4j.properties /opt/marathon-0.11.1/

RUN mkdir -p /opt/log

ENV JAVA_OPTS -Dlog4j.configuration=file:///opt/marathon-0.11.1/log4j.properties

ENTRYPOINT ["./bin/start"]
