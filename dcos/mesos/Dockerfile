#
# Dockerfile for building Mesos from source
#
# Create snapshot builds with:
# docker build -t mesos/mesos:git-`git rev-parse --short HEAD` .
#
# Run master/slave with:
# docker run mesos/mesos:git-`git rev-parse --short HEAD` mesos-master [options]
# docker run mesos/mesos:git-`git rev-parse --short HEAD` mesos-slave [options]
#

FROM ubuntu:14.04

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>

RUN apt-get update && apt-get install -y libapr1 libcurl3-nss libgflags2 libsasl2-2 libsvn1 libcurl3 libsasl2-modules openjdk-7-jre-headless libapparmor1

ADD ./mesos.deb /opt/mesos/
RUN dpkg -i /opt/mesos/mesos.deb && rm -rf /opt/mesos

ENV MESOS_HOME /opt/ibm/mesos

ENV PATH=$PATH:$MESOS_HOME/sbin:$MESOS_HOME/bin
RUN mkdir -p /var/lib/mesos

# include libmesos on library path
ENV LD_LIBRARY_PATH $MESOS_HOME/lib


