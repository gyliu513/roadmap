FROM ubuntu

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>

RUN apt-get update && apt-get install -yq supervisor

ADD https://github.com/coreos/etcd/releases/download/v2.2.1/etcd-v2.2.1-linux-amd64.tar.gz /opt/

WORKDIR /opt

RUN tar xzvf etcd-v2.2.1-linux-amd64.tar.gz

ENV ETCD_HOME /opt/etcd-v2.2.1-linux-amd64

ADD ./bootstrap.sh $ETCD_HOME/
RUN chmod +x $ETCD_HOME/bootstrap.sh

WORKDIR $ETCD_HOME

ENTRYPOINT ["./bootstrap.sh"]
