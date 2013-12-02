# Logs message local to this VM
LOG()
{
    msg=$1;
    echo `date` "$msg" >> "$LOG_FILE"
}
 
# Function to install Hadoop
install_hadoop()
{
    # Install the JDK
    LOG "Installing JDK from $DOWNLOAD_DIR"
    cd $DOWNLOAD_DIR
    chmod +x $DOWNLOAD_DIR/$JDK_PKG_NAME
    yes | $DOWNLOAD_DIR/$JDK_PKG_NAME
    if [ "$?" != "0" ] ; then
        LOG "Error installing JDK "
        exit 1
    fi
    JDK_version=`ls /usr/java/ | grep jdk`
 
    echo "export JAVA_HOME=/usr/java/$JDK_version" >> /etc/profile
    echo "export JRE_HOME=/usr/java/$JDK_version/jre" >> /etc/profile
    echo "export CLASSPATH=.:\$JAVA_HOME/lib:\$JRE_HOME/lib:\$CLASSPATH" >> /etc/profile
    echo "export PATH=\$JAVA_HOME/bin:\$JRE_HOME/bin:\$PATH" >> /etc/profile
    
    source /etc/profile
    if [ "$?" != "0" ] ; then
        LOG "Fail to config /etc/profile to add java environment variables.You can config it manually."
    fi
    LOG "Installing Hadoop 1.2.1"
    tar xvfz $DOWNLOAD_DIR/hadoop-1.2.1-bin.tar.gz -C /opt
    if [ "$?" != "0" ] ; then
        LOG "Error installing Cloudera Hadoop"
        exit 1
    fi
    command="s#JAVA_HOME=.*\$#JAVA_HOME=/usr/java/$JDK_version#"
    sed -i $command $HADOOP_CONF/conf/hadoop-env.sh
    sed -i "s/^#.*JAVA_HOME=/ export JAVA_HOME=/" $HADOOP_CONF/conf/hadoop-env.sh
    return 0
}
 
# Function to start up hadoop
config_hadoop()
{
    local HADOOP_CONF=/opt/hadoop-1.2.1/
    # Some how alternatives not setting correctly
    #cp -r $HADOOP_CONF/conf.pseudo $HADOOP_CONF/conf.my_cluster
    #alternatives --install $HADOOP_CONF/conf hadoop-0.20-conf $HADOOP_CONF/conf.my_cluster 50
    
    LOG "Configuring Cloudera Hadoop"
    HADOOP_MASTER=`hostname`
 
    # Put master name into the config files
 
    add_slave_hostname slaves
    if [ "$?" != "0" ] ; then
        LOG "Failed to config slave for hadoop."
        return 1
    fi
 
    sed -i '/<\/configuration>/d' /opt/hadoop-1.2.1/conf/core-site.xml
    cat <<AAA >> /opt/hadoop-1.2.1/conf/core-site.xml
<property>
         <name>fs.default.name</name>
         <value>hdfs://$HADOOP_MASTER:9000</value>
</property>
AAA
    echo "</configuration>" >> /opt/hadoop-1.2.1/conf/core-site.xml
 
    sed -i '/<\/configuration>/d' /opt/hadoop-1.2.1/conf/mapred-site.xml
    cat <<AAA >> /opt/hadoop-1.2.1/conf/mapred-site.xml
<property>
          <name>mapred.job.tracker</name>
         <value>$HADOOP_MASTER:9001</value>
</property>
AAA
    echo "</configuration>" >> /opt/hadoop-1.2.1/conf/mapred-site.xml
 
    command="s/localhost/$HADOOP_MASTER/" 
    sed -i $command $HADOOP_CONF/conf/masters 
    # config hadoop for dynamic refresh cluster info.
    touch -f /opt/hadoop-1.2.1/conf/datanode_allowlist
    touch -f /opt/hadoop-1.2.1/conf/tasktracker_allowlist
    sed -i '/<\/configuration>/d' /opt/hadoop-1.2.1/conf/hdfs-site.xml
    cat <<AAA >> /opt/hadoop-1.2.1/conf/hdfs-site.xml
<property>
         <name>dfs.replication</name>
         <value>1</value>
     </property>
<property>
<name>dfs.hosts</name>
<value>/opt/hadoop-1.2.1/conf/datanode_allowlist</value>
</property>
<property>
<name>mapred.hosts</name>
<value>/opt/hadoop-1.2.1/conf/tasktracker_allowlist</value>
</property>
AAA
    echo "</configuration>" >> /opt/hadoop-1.2.1/conf/hdfs-site.xml
 
    JDK_version=`ls /usr/java | grep jdk`
 
    LOG "Finish config Cloudera Hadoop"
 
    # chkconfig hadoop-0.20-namenode --add
    # chkconfig hadoop-0.20-namenode on
    # chkconfig hadoop-0.20-jobtracker --add
    # chkconfig hadoop-0.20-jobtracker on
    # chkconfig hadoop-0.20-secondarynamenode --add
    # chkconfig hadoop-0.20-secondarynamenode on
    # chkconfig hadoop-0.20-tasktracker --add
    # chkconfig hadoop-0.20-tasktracker on
    # chkconfig hadoop-0.20-datanode --add
    # chkconfig hadoop-0.20-datanode on
    config_ssh
 
    # change sudoers file to use "sudo" command in script.
    #sed -i 's/Defaults.*requiretty/#Defaults requiretty/' /etc/sudoers
    #if [ "$?" != "0" ] ; then
    # LOG "Failed to change /etc/sudoers file."
    # return 1
    #fi
 
    LOG "Start Hadoop cluster..."
    echo "Y" | /opt/hadoop-1.2.1/bin/hadoop namenode -format
    #sudo -u hadoop /usr/lib/hadoop-0.20/bin/start-all.sh
    #if [ "$?" != "0" ] ; then
    # LOG "Failed to start Hadoop cluster, you can run /usr/lib/hadoop-0.20/bin/start-all.sh manually."
    #fi
    LOG "Format namenode successfully."
 
    return 0
}
 
config_ssh()
{
    return 0
}
 
add_slave_hostname()
{
    local HADOOP_CONF=/opt/hadoop-1.2.1/
    local file=$1
    if [ -f $HADOOP_CONF/conf/${file}.temp ];then
        rm -f $HADOOP_CONF/conf/${file}.temp
    fi
    mv $HADOOP_CONF/conf/${file} $HADOOP_CONF/conf/${file}.temp
    
    # config input file to add hostnames of all slaves.
    config_file="$HADOOP_CONF/conf/${file}"
    slave_hostname=`echo $HadoopSlaveTier_HOSTNAMES | sed "s/;/ /g"`
    array_hostname=($slave_hostname)
    
    len=${#array_hostname[@]}
    index=0
    while [ $index -lt $len ];do
        echo "${array_hostname[$index]}" >> $config_file
        let ++index
    done
    if [ "$?" != "0" ] ; then
        LOG "Failed to config file $config_file."
        return 1
    fi
    return 0
}
 
#================= Main Entry =======================================
 
# Where to output log file
LOG_FILE=/tmp/hadoopMaster.log
 
# Where to download files
DOWNLOAD_DIR="/hadoop_package"
JDK_PKG_NAME="jdk-6u30-linux-x64-rpm.bin"
HADOOP_CONF=/opt/hadoop-1.2.1/
# OK. Do the work.
 
HadoopMasterTier_IP_ADDRS=`ifconfig eth0 | grep "inet addr" | awk '{print $2}'| awk -F ":" '{print $2}'`
HadoopMasterTier_HOSTNAMES=`hostname`
 
 
#HadoopSlaveTier_IP_ADDRS=$1
#HadoopSlaveTier_HOSTNAMES=$2
HadoopSlaveTier_IP_ADDRS="1.1.1.1"
HadoopSlaveTier_HOSTNAMES="host1"
 
LOG "PATH $PATH"
PATH=$PATH:/usr/sbin
PATH=$PATH:/sbin
LOG "PATH $PATH"
 
LOG "Starting........."
 
#LOG_EVENT "Post-provisioning script started"
 
LOG "Current Action is CREATE"
 
install_hadoop
if [ "$?" != "0" ] ; then
   exit 99
fi

config_hadoop
if [ "$?" != "0" ] ; then
   exit 99
fi
 
LOG "End....."
 
exit 0
