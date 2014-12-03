# Creates pseudo distributed hadoop 2.4
#
# docker build -t="sequenceiq/hadoop-cluster-docker:2.4.1" .

FROM sequenceiq/hadoop-docker

MAINTAINER SequenceIQ

USER root

# pseudo distributed
ADD core-site.xml $HADOOP_PREFIX/etc/hadoop/core-site.xml
ADD hdfs-site.xml $HADOOP_PREFIX/etc/hadoop/hdfs-site.xml

ADD mapred-site.xml $HADOOP_PREFIX/etc/hadoop/mapred-site.xml
ADD yarn-site.xml $HADOOP_PREFIX/etc/hadoop/yarn-site.xml

ADD slaves $HADOOP_PREFIX/etc/hadoop/slaves

ADD bootstrap.sh /etc/bootstrap.sh
RUN chown root:root /etc/bootstrap.sh
RUN chmod 700 /etc/bootstrap.sh
ENV BOOTSTRAP /etc/bootstrap.sh

# passwordless ssh
RUN rm -f /etc/ssh/ssh_host_dsa_key
RUN rm -f /etc/ssh/ssh_host_rsa_key
RUN rm -f /root/.ssh/id_rsa


RUN ssh-keygen -q -N "" -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN ssh-keygen -q -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN ssh-keygen -q -N "" -t rsa -f /root/.ssh/id_rsa
RUN cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys

ADD ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config
RUN chown root:root /root/.ssh/config

#RUN sed -i "/^[^#]*UsePAM/ s/.*/#&/" /etc/ssh/sshd_config
#RUN echo "UsePAM no" >> /etc/ssh/sshd_config
#RUN echo "Port 2122" >> /etc/ssh/sshd_config
#modify /etc/hosts file
#ADD hosts /tmp/hosts
#RUN mv /tmp/hosts /etc/hosts
#RUN mkdir -p -- /lib-override 
#ADD libnss_files.so.2 /lib-override/libnss_files.so.2
#RUN perl -pi -e 's:/etc/hosts:/tmp/hosts:g' /lib-override/libnss_files.so.2
#ENV LD_LIBRARY_PATH /lib-override


#expose ports
    
EXPOSE 50020 50021 50090 50070 50010 50011 50075 50076 8031 8032 8033 8040 8042 49707 22 8088 8030 8020

CMD ["-h"]
ENTRYPOINT ["/etc/bootstrap.sh"]
