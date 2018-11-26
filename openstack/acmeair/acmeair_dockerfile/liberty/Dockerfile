# CentOS 6 based container with Java and Websphere Liberty installed
#

FROM acmeair/java
MAINTAINER David Nguyen <nguyen1d@us.ibm.com>

# Install Liberty
ADD wlp-developers-runtime-8.5.5.2.jar /
RUN java -jar /wlp-developers-runtime-8.5.5.2.jar --acceptLicense /acmeair
RUN rm -f /wlp-developers-runtime-8.5.5.2.jar

ENV WLP_SERVERDIR /acmeair/wlp
