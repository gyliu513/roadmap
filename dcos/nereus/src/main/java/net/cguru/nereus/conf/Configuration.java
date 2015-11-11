package net.cguru.nereus.conf;

import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

/**
 * Created by dma on 6/14/15.
 * <p>
 * The configuration of Nereuse
 */
public class Configuration {

    public static final String KAFKA_BROKERS="kafka.brokers";
    public static final String KAFKA_TOPIC_PRE="kafka.topics.";
    public static final String KAFKA_GROUP_ID="kafka.groupid";

    public static final String DB_NAME="db.name";
    public static final String DB_DRIVER="db.driver";
    public static final String DB_URL="db.url";
    public static final String DB_PASSWORD="db.password";
    public static final String DB_USER_NAME="db.username";


    private String dbDriver;
    private String dbName;
    private String dbPassword;
    private String dbUserName;
    private String dbUrl;
    private String kafkaBrokers;
    private Map<String, Integer> kafkaTopics = new HashMap<String, Integer>();
    private String kafkaGroupId;

    public Configuration(String confFile) throws IOException {
        // reading the configuration from the file
        Properties props = new Properties();

        props.load(new FileReader(ClassLoader.getSystemResource(confFile).getFile()));

        this.setDbDriver(props.getProperty(DB_DRIVER));
        this.setDbName(props.getProperty(DB_NAME));
        this.setDbUserName(props.getProperty(DB_USER_NAME));
        this.setDbUrl(props.getProperty(DB_URL));
        this.setDbPassword(props.getProperty(DB_PASSWORD));


        this.setKafkaBrokers(props.getProperty(KAFKA_BROKERS));
        this.setKafkaGroupId(props.getProperty(KAFKA_GROUP_ID));

        for (Map.Entry<Object, Object> _entry : props.entrySet())
        {
            String key = _entry.getKey().toString();
            if (!key.startsWith(KAFKA_TOPIC_PRE))
                continue;
            String topic = key.substring(KAFKA_TOPIC_PRE.length());

            this.kafkaTopics.put(topic, Integer.parseInt(_entry.getValue().toString()));
        }

    }

    public String getDbDriver() {
        return dbDriver;
    }

    public void setDbDriver(String dbDriver) {
        this.dbDriver = dbDriver;
    }

    public String getDbName() {
        return dbName;
    }

    public void setDbName(String dbName) {
        this.dbName = dbName;
    }

    public String getDbPassword() {
        return dbPassword;
    }

    public void setDbPassword(String dbPassword) {
        this.dbPassword = dbPassword;
    }

    public String getDbUserName() {
        return dbUserName;
    }

    public void setDbUserName(String dbUserName) {
        this.dbUserName = dbUserName;
    }

    public String getDbUrl() {
        return dbUrl;
    }

    public void setDbUrl(String dbUrl) {
        this.dbUrl = dbUrl;
    }

    public String getKafkaBrokers() {
        return kafkaBrokers;
    }

    public void setKafkaBrokers(String kafkaBrokers) {
        this.kafkaBrokers = kafkaBrokers;
    }

    public Map<String, Integer> getKafkaTopics() {
        return kafkaTopics;
    }

    public void setKafkaTopics(Map<String, Integer> kafkaTopics) {
        this.kafkaTopics = kafkaTopics;
    }

    public String getKafkaGroupId() {
        return kafkaGroupId;
    }

    public void setKafkaGroupId(String kafkaGroupId) {
        this.kafkaGroupId = kafkaGroupId;
    }
}
