package net.cguru.nereus.streaming;

import net.cguru.nereus.common.GlobalConstants;
import org.apache.log4j.Logger;
import org.springframework.context.support.ClassPathXmlApplicationContext;

import java.io.IOException;

public final class MainLoop {

    private static final Logger logger = Logger.getLogger(MainLoop.class);

    public static void main(String[] args) throws IOException {

        ClassPathXmlApplicationContext applicationContext = new ClassPathXmlApplicationContext(GlobalConstants.SPRING_CONF);
        Workflow workflow = applicationContext.getBean(GlobalConstants.WORKFLOW_BEAN_ID, Workflow.class);

        workflow.run();

    }

}
