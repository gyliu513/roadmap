package net.cguru.nereus.db;

import net.cguru.nereus.conf.Configuration;
import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.influxdb.InfluxDB;
import org.influxdb.InfluxDBFactory;
import org.influxdb.dto.Serie;

import java.util.Collections;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Created by dma on 6/15/15.
 */
public class InfluxDBAdapter implements DataBaseAdapter {

    private static final Logger logger = Logger.getLogger(InfluxDBAdapter.class);
    private InfluxDB influxDB;
    private Configuration conf;

    public void connect() {
        logger.debug("connect to influxdb with URL <" + conf.getDbUrl()
                + ">, Username <" + conf.getDbUserName()
                + ">, Password <" + conf.getDbPassword()
                + ">, DBName <" + conf.getDbName() + ">.");
        this.influxDB = InfluxDBFactory.connect(conf.getDbUrl(), conf.getDbUserName(), conf.getDbUserName());
    }

    public void save(String key, Map<String, Object> datas) {
        Serie.Builder sb = new Serie.Builder(key);
        String[] cols = new String[datas.size()];
        Object[] vals = new Object[datas.size()];

        int i = 0;

        for (Map.Entry<String, Object> entry : datas.entrySet()) {
            cols[i] = entry.getKey();
            vals[i] = entry.getValue();
            i++;
        }

        logger.debug("Save data as cols <" + StringUtils.join(cols, ",")
                    + ">, vals <" + StringUtils.join(vals, ",")
                    + "> by key <" + key + ">.");

        sb.columns(cols).values(vals);

        influxDB.write(this.conf.getDbName(), TimeUnit.MILLISECONDS, sb.build());
    }

    public void close() {
        influxDB= null;
    }

    public Configuration getConf() {
        return conf;
    }

    public void setConf(Configuration conf) {
        this.conf = conf;
    }
}
