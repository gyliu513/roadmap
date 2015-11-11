package net.cguru.nereus.streaming;

import net.cguru.nereus.common.GlobalConstants;
import net.cguru.nereus.conf.Configuration;
import net.cguru.nereus.db.DataBasePool;
import net.cguru.nereus.db.DataBaseAdapter;
import net.cguru.nereus.db.DataParser;
import org.apache.log4j.Logger;
import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.function.Function;
import org.apache.spark.streaming.Durations;
import org.apache.spark.streaming.api.java.JavaPairReceiverInputDStream;
import org.apache.spark.streaming.api.java.JavaStreamingContext;
import org.apache.spark.streaming.kafka.KafkaUtils;
import scala.Tuple2;

import java.util.Map;

/**
 * Created by dma on 6/15/15.
 */
public class Workflow {

    private static final Logger logger = Logger.getLogger(Workflow.class);

    private Configuration conf;

    public void run() {
        // Create the context with a 1 second batch size
        SparkConf sparkConf = new SparkConf().setAppName(GlobalConstants.APP_NAME);
        JavaStreamingContext streamingContext = new JavaStreamingContext(sparkConf, Durations.seconds(1));

        final DataBaseAdapter db = DataBasePool.getDataBase(conf.getDbDriver());

        JavaPairReceiverInputDStream<String, String> lines = KafkaUtils.createStream(streamingContext, conf.getKafkaBrokers(),
                conf.getKafkaGroupId(), conf.getKafkaTopics());

        logger.debug("DBDriver <" + conf.getDbDriver() + ">, Kafka Brokers <" + conf.getKafkaBrokers()
                + ">, Kafka GroupID <" + conf.getKafkaGroupId() +">.") ;

        lines.foreach(new Function<JavaPairRDD<String, String>, Void>() {
            public Void call(JavaPairRDD<String, String> stringStringJavaPairRDD) throws Exception {
                for (Tuple2<String, String> csvData : stringStringJavaPairRDD.collect()) {
                    Map<String, Object> dataMap = DataParser.parse(csvData._2());
                    db.save(csvData._1(), dataMap);
                }
                return null;
            }
        });

        streamingContext.start();
        streamingContext.awaitTermination();
    }

    public Configuration getConf() {
        return conf;
    }

    public void setConf(Configuration conf) {
        this.conf = conf;
    }
}
