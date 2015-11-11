package net.cguru.nereus.db;

import java.util.Map;

/**
 * Created by dma on 6/15/15.
 */
public class DataBasePool {

    private  static Map<String, DataBaseAdapter> dataBaseAdapterMap;

    public  static  DataBaseAdapter getDataBase(String name)
    {
        return dataBaseAdapterMap.get(name);
    }

    public static Map<String, DataBaseAdapter> getDataBaseAdapterMap() {
        return dataBaseAdapterMap;
    }

    public static void setDataBaseAdapterMap(Map<String, DataBaseAdapter> dataBaseAdapterMap) {
        DataBasePool.dataBaseAdapterMap = dataBaseAdapterMap;
    }

}
