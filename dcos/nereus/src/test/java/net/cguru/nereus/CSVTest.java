package net.cguru.nereus;

import com.opencsv.CSVReader;
import org.junit.Assert;
import org.junit.Test;

import java.io.IOException;
import java.io.StringReader;

/**
 * Created by dma on 2015/6/10.
 */

public class CSVTest {

    @Test
    public void testCSV() throws IOException {
        CSVReader reader = new CSVReader(new StringReader("aaa,bbb"));
        String[] nextLine;
        while ((nextLine = reader.readNext()) != null) {
            // nextLine[] is an array of values from the line
            Assert.assertEquals("aaa", nextLine[0]);
            Assert.assertEquals("bbb", nextLine[1]);
        }
    }
}
