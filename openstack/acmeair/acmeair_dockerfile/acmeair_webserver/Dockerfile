# CentOS 6 based container with Java, Websphere Liberty, and Websphere Extremescale, Acme Air installed
#
# This container will start the Extremescale catalog for Acme Air

FROM acmeair/acmeair_base
MAINTAINER David Nguyen <nguyen1d@us.ibm.com>

WORKDIR /acmeair/ObjectGrid

RUN mkdir acmeair
RUN /bin/cp gettingstarted/* -R acmeair

# Make a copy of the env.sh file and then edit it to coment out current server classpath and customize it by adding a new line right after it with the right values
RUN /bin/cp acmeair/env.sh acmeair/env.sh.original

RUN sed -i 's/SAMPLE_SERVER_CLASSPATH=/#SAMPLE_SERVER_CLASSPATH=/g' acmeair/env.sh

RUN sed -i '/#SAMPLE_SERVER_CLASSPATH/aSAMPLE_SERVER_CLASSPATH="${SAMPLE_COMMON_CLASSPATH}:${SAMPLE_HOME}/server/bin:/acmeair/eclipse/acmeair/acmeair-common/target/classes:/acmeair/eclipse/acmeair/acmeair-services-wxs/target/classes:/root/.m2/repository/commons-logging/commons-logging/1.1.1/commons-logging-1.1.1.jar"' acmeair/env.sh

WORKDIR /acmeair/wlp

# Make a copy of the server.xml config file and add a line to allow http calls from all hosts
RUN bin/server create server1
RUN cp usr/servers/server1/server.xml usr/servers/server1/server.xml.original

RUN sed -i '/id="defaultHttpEndpoint"/ahost="*"' usr/servers/server1/server.xml

RUN sed -i 's/<feature>jsp-2.2<\/feature>/<feature>jaxrs-1.1<\/feature> <feature>jndi-1.0<\/feature> <feature>eXtremeScale.client-1.1<\/feature>/g' usr/servers/server1/server.xml

WORKDIR /acmeair/eclipse/acmeair

RUN touch /acmeair/hosts
RUN mkdir -p -- /lib-override && cp /lib64/libnss_files.so.2 /lib-override
RUN perl -pi -e 's:/etc/hosts:/tmp/hosts:g' /lib-override/libnss_files.so.2
ENV LD_LIBRARY_PATH /lib-override

ADD .bash_profile /root/.bash_profile
ADD authorized_keys /root/.ssh/authorized_keys
ADD supervisord.conf /etc/supervisord.conf
ADD run.sh /bin/run.sh

CMD /bin/run.sh

EXPOSE 9080
