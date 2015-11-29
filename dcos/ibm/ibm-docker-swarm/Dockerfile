FROM ubuntu

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>
MAINTAINER Yong Feng <yongfeng@ca.ibm.com>

RUN apt-get update && apt-get install -yq supervisor

ADD ./godep/bin/swarm /opt/
ADD ./bootstrap.sh /opt/
RUN chmod +x /opt/bootstrap.sh

WORKDIR /opt

ENTRYPOINT ["./bootstrap.sh"]

