# CentOS 6 based container with Java, Websphere Liberty, and Websphere Extremescale, Acme Air installed 
#
# This container will start the Extremescale catalog for Acme Air

FROM acmeair/acmeair_base
MAINTAINER David Nguyen <nguyen1d@us.ibm.com>

#
# Configure Extremescale as a 'local config'
#
WORKDIR /acmeair/ObjectGrid
RUN mkdir acmeair
RUN /bin/cp gettingstarted/* -R acmeair

# Make a copy of the env.sh file and then edit it to coment out current server classpath and customize it by adding a new line right after it with the right values
RUN /bin/cp acmeair/env.sh acmeair/env.sh.original

RUN /bin/sed -i 's/SAMPLE_SERVER_CLASSPATH=/#SAMPLE_SERVER_CLASSPATH=/g' acmeair/env.sh

RUN /bin/sed -i '/#SAMPLE_SERVER_CLASSPATH/aSAMPLE_SERVER_CLASSPATH="${SAMPLE_COMMON_CLASSPATH}:${SAMPLE_HOME}/server/bin:$ACMEAIR_SRCDIR/acmeair-common/target/classes:$ACMEAIR_SRCDIR/acmeair-services-wxs/target/classes:/root/.m2/repository/commons-logging/commons-logging/1.1.1/commons-logging-1.1.1.jar"' acmeair/env.sh

#
# Start the catalog
#
# Copy the Acme Air specific eXtreme Scale configuration files from our source directory
RUN /bin/mv /acmeair/ObjectGrid/acmeair/server/config/deployment.xml /acmeair/ObjectGrid/acmeair/server/config/deployment.xml.original
RUN /bin/cp /acmeair/eclipse/acmeair/acmeair-services-wxs/src/main/resources/deployment.xml /acmeair/ObjectGrid/acmeair/server/config
RUN /bin/mv /acmeair/ObjectGrid/acmeair/server/config/objectgrid.xml /acmeair/ObjectGrid/acmeair/server/config/objectgrid.xml.original
RUN /bin/cp /acmeair/eclipse/acmeair/acmeair-services-wxs/src/main/resources/objectgrid.xml /acmeair/ObjectGrid/acmeair/server/config

# recompile again...may not be necessary
WORKDIR /acmeair/eclipse/acmeair
RUN mvn clean compile package install

RUN touch /acmeair/hosts
RUN mkdir -p -- /lib-override && cp /lib64/libnss_files.so.2 /lib-override
RUN perl -pi -e 's:/etc/hosts:/tmp/hosts:g' /lib-override/libnss_files.so.2
ENV LD_LIBRARY_PATH /lib-override

ADD .bash_profile /root/.bash_profile
ADD authorized_keys /root/.ssh/authorized_keys
ADD supervisord.conf /etc/supervisord.conf
ADD run.sh /bin/run.sh

CMD /bin/run.sh

# Expose 2809 for CORBA
# Expose 1099 for Java RMI
EXPOSE 2809 1099
