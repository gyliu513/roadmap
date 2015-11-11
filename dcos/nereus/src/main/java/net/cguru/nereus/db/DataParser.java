package net.cguru.nereus.db;

import com.opencsv.CSVReader;

import java.io.IOException;
import java.io.StringReader;
import java.util.HashMap;
import java.util.Map;

/**
 * Created by dma on 6/15/15.
 */
public final class DataParser {

    public static final char KV_SPLITOR = ':';

    public static Map<String, Object> parse(String data) throws IOException {

        Map<String, Object> dataMap = new HashMap<String, Object>();

        CSVReader reader = new CSVReader(new StringReader(data));
        String[] datas;

        while ((datas = reader.readNext()) != null) {
            for (String d : datas) {
                if (d == null) continue;

                int idx = d.indexOf(KV_SPLITOR);

                if (idx <= 0) {
                    continue;
                }

                String k = d.substring(0, idx).trim();
                String v = d.substring(idx + 1).trim();

                try {
                    Double dv = Double.parseDouble(v);
                    dataMap.put(k, dv);
                } catch (Exception e) {
                    dataMap.put(k, v);
                }
            }

        }
        return dataMap;
    }
}
