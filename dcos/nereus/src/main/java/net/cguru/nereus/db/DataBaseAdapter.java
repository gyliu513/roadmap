package net.cguru.nereus.db;

import net.cguru.nereus.conf.Configuration;

import java.util.Map;

/**
 * Created by dma on 6/15/15.
 */
public interface DataBaseAdapter {

    void connect();

    void save(String key, Map<String, Object> data);

    void close();
}
