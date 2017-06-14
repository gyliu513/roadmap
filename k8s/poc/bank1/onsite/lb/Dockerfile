FROM ubuntu:16.04

RUN export http_proxy=http://9.21.53.16:3128 \
    && export https_proxy=http://9.21.53.16:3128 \
    && apt update \
    && apt install --no-install-recommends -y net-tools libltdl-dev\
    && apt-get -y autoremove \
    && apt-get -y autoclean \
    && unset http_proxy https_proxy
	

COPY files/collect.sh /
COPY files/etcdctl /usr/local/bin/
COPY files/docker /usr/bin/

ENTRYPOINT ["/collect.sh"]


