# CentOS 6 based container with Java, Websphere Liberty, and Websphere Extremescale installed
#

FROM acmeair/liberty
MAINTAINER David Nguyen <nguyen1d@us.ibm.com>

# Install Extremescale
ADD wxs-wlp_8.6.0.4.jar /wxs-wlp_8.6.0.4.jar
RUN java -jar /wxs-wlp_8.6.0.4.jar --acceptLicense /acmeair
RUN /bin/rm -f /wxs-wlp_8.6.0.4.jar

ADD extremescaletrial860.zip /extremescaletrial860.zip
RUN /usr/bin/unzip /extremescaletrial860.zip -d /acmeair
RUN /bin/rm -f /extremescaletrial860.zip

ENV WXS_SERVERDIR /acmeair/ObjectGrid

WORKDIR /acmeair/ObjectGrid/lib
RUN  mvn install:install-file -Dfile=objectgrid.jar -DgroupId=com.ibm.websphere.objectgrid -DartifactId=objectgrid -Dversion=8.6.0.2 -Dpackaging=jar

