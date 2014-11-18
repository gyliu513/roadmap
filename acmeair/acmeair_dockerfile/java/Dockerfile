# CentOS 6 based container with Java installed
#

FROM acmeair/base
MAINTAINER David Nguyen <nguyen1d@us.ibm.com>

# Install Java
ADD ibm-java-x86_64-sdk-7.1-1.0.x86_64.rpm /ibm-java-x86_64-sdk-7.1-1.0.x86_64.rpm
RUN /bin/rpm -ivh /ibm-java-x86_64-sdk-7.1-1.0.x86_64.rpm
RUN /bin/rm -f /ibm-java-x86_64-sdk-7.1-1.0.x86_64.rpm

ENV JAVA_HOME /opt/ibm/java-x86_64-71
ENV PATH $JAVA_HOME/bin:$PATH

