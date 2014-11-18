# CentOS 6 based container with Java installed
#

FROM centos:centos6
MAINTAINER David Nguyen <nguyen1d@us.ibm.com>

# 1)  Install RPMs needed for the rest of the setup
# 2)  Install supervisord to run our daemons
# 3)  Install Maven
# 4)  Create acmeair base directory

RUN /usr/bin/yum -y update &&\
/usr/bin/yum -y install openssh-server openssh-clients python-setuptools wget unzip git &&\
/usr/bin/easy_install supervisor &&\
/usr/bin/wget http://apache.mesi.com.ar/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.zip &&\
/usr/bin/unzip apache-maven-3.0.5-bin.zip &&\
/bin/mv apache-maven-3.0.5 /usr/local/maven &&\
/bin/rm -f apache-maven-3.0.5-bin.zip &&\
/bin/mkdir /acmeair

ENV M2_HOME /usr/local/maven
ENV PATH /usr/local/maven/bin:$PATH

EXPOSE 22
