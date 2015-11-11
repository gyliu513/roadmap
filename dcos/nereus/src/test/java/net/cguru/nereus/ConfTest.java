package net.cguru.nereus;

import net.cguru.nereus.common.GlobalConstants;
import net.cguru.nereus.db.DataBasePool;
import net.cguru.nereus.db.DataBaseAdapter;
import net.cguru.nereus.streaming.Workflow;
import org.junit.Test;
import org.springframework.context.support.FileSystemXmlApplicationContext;

/**
 * Created by dma on 6/15/15.
 */


public class ConfTest {

    @Test
    public void testConf()
    {
        FileSystemXmlApplicationContext applicationContext = new FileSystemXmlApplicationContext( "file:///Users/dma/workspace/Nereus/src/main/java/nereus.xml");
        Workflow workflow = applicationContext.getBean(GlobalConstants.WORKFLOW_BEAN_ID, Workflow.class);

        DataBaseAdapter db = DataBasePool.getDataBase("influxdb");

        System.out.print(workflow.toString());
    }
}
