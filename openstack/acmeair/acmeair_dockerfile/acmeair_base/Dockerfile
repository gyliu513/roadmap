# CentOS 6 based container with Java, Websphere Liberty, and Websphere Extremescale, Acme Air installed 
#

FROM acmeair/extremescale
MAINTAINER David Nguyen <nguyen1d@us.ibm.com>

# Build Acme Air
RUN /bin/mkdir -p /acmeair/eclipse

WORKDIR /acmeair/eclipse
# RUN /usr/bin/git clone https://github.com/acmeair/acmeair.git
RUN git clone -b server_ip_info https://github.com/davidnnguyen/acmeair.git

# RUN mvn twice in the same command otherwise docker bails when mvn fails the first time.
WORKDIR /acmeair/eclipse/acmeair
RUN mvn clean compile package install;mvn clean compile package install

# The objectgrid.jar dependency gets resolved when maven is run the second time
#WORKDIR /acmeair/eclipse/acmeair
#RUN mvn clean compile package install

ENV ACMEAIR_SRCDIR /acmeair/eclipse/acmeair
