#include <ctype.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <syslog.h>
#include <sys/time.h>
#include <errno.h>

#include "librdkafka/rdkafka.h"  /* for Kafka driver */

static rd_kafka_t *rk;


/**
 * Kafka logger callback (optional)
 */
static void logger (const rd_kafka_t *rk, int level, const char *fac, const char *buf) 
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    fprintf(stderr, "%u.%03u RDKAFKA-%i-%s: %s: %s\n",
        (int)tv.tv_sec, (int)(tv.tv_usec / 1000),
        level, fac, rd_kafka_name(rk), buf);
}

/**
 * Message delivery report callback.
 * Called once for each message.
 * See rdkafka.h for more information.
 */
static void msg_delivered (rd_kafka_t *rk,
               void *payload, size_t len,
               rd_kafka_resp_err_t error_code,
               void *opaque, void *msg_opaque) {
    
    if (error_code)
        fprintf(stderr, "%% Message delivery failed: %s\n", rd_kafka_err2str(error_code));
}

int main (int argc, char **argv) {
    rd_kafka_topic_t *rkt;
    char *brokers = 0;
    char *topic = NULL;
    int partition = RD_KAFKA_PARTITION_UA;
    int opt;
    rd_kafka_conf_t *conf;
    rd_kafka_topic_conf_t *topic_conf;
    char errstr[512];
    char tmp[16];
    char* msg = 0;
    char* key = 0;

    /* Kafka configuration */
    conf = rd_kafka_conf_new();

    /* Quick termination */
    snprintf(tmp, sizeof(tmp), "%i", SIGIO);
    rd_kafka_conf_set(conf, "internal.termination.signal", tmp, NULL, 0);

    /* Topic configuration */
    topic_conf = rd_kafka_topic_conf_new();

    while ((opt = getopt(argc, argv, "t:p:b:z:m:k:")) != -1) {
        switch (opt) {
        case 't':
            topic = optarg;
            break;
        case 'p':
            partition = atoi(optarg);
            break;
        case 'b':
            brokers = optarg;
            break;
        case 'z':
            if (rd_kafka_conf_set(conf, "compression.codec",
                          optarg,
                          errstr, sizeof(errstr)) !=
                RD_KAFKA_CONF_OK) {
                fprintf(stderr, "%% %s\n", errstr);
                exit(1);
            }
            break;
        case 'm':
            msg = optarg;
            break;
        case 'k':
            key = optarg;
            break;
        default:
            goto usage;
        }
    }

    if (optind != argc || msg == 0 || brokers == 0) {
    usage:
        fprintf(stderr,
            "Usage: %s -t <topic> -m <message>"
            "[-p <partition>] [-b <host1:port1,host2:port2,..>] [-k <key>]\n"
            "\n"
            "librdkafka version %s (0x%08x)\n"
            "\n"
            " Options:\n"
            "  -t <topic>      Topic to fetch / produce\n"
            "  -p <num>        Partition (random partitioner)\n"
            "  -b <brokers>    Broker address (localhost:9092)\n"
            "  -z <codec>      Enable compression:\n"
            "                  none|gzip|snappy\n"
            "  -m <msg>        Message to send\n"
            "  -k <key>        Key of message\n"
            "\n"
            "\n",
            argv[0],
            rd_kafka_version_str(), rd_kafka_version());
        exit(1);
    }

    {
        /*
         * Producer
         */

        /* Set up a message delivery report callback.
         * It will be called once for each message, either on successful
         * delivery to broker, or upon failure to deliver to broker. */

                /* If offset reporting (-o report) is enabled, use the
                 * richer dr_msg_cb instead. */
        rd_kafka_conf_set_dr_cb(conf, msg_delivered);

        /* Create Kafka handle */
        if (!(rk = rd_kafka_new(RD_KAFKA_PRODUCER, conf,
                    errstr, sizeof(errstr)))) {
            fprintf(stderr,
                "%% Failed to create new producer: %s\n",
                errstr);
            exit(1);
        }

        /* Set logger */
        rd_kafka_set_logger(rk, logger);
        rd_kafka_set_log_level(rk, LOG_DEBUG);

        /* Add brokers */
        if (rd_kafka_brokers_add(rk, brokers) == 0) {
            fprintf(stderr, "%% No valid brokers specified\n");
            exit(1);
        }

        /* Create topic */
        rkt = rd_kafka_topic_new(rk, topic, topic_conf);

            /* Send/Produce message. */
            if (rd_kafka_produce(rkt, partition,
                         RD_KAFKA_MSG_F_COPY,
                         /* Payload and length */
                         msg, strlen(msg),
                         /* Optional key and its length */
                         key, key?strlen(key): 0,
                         /* Message opaque, provided in
                          * delivery report callback as
                          * msg_opaque. */
                         NULL) == -1) {
                fprintf(stderr,
                    "%% Failed to produce to topic %s "
                    "partition %i: %s\n",
                    rd_kafka_topic_name(rkt), partition,
                    rd_kafka_err2str(
                        rd_kafka_errno2err(errno)));
                /* Poll to handle delivery reports */
                rd_kafka_poll(rk, 0);
                exit(1);
            }

            /* Poll to handle delivery reports */
            // rd_kafka_poll(rk, 0);

        /* Poll to handle delivery reports */
        rd_kafka_poll(rk, 0);

        /* Wait for messages to be delivered */
        while (rd_kafka_outq_len(rk) > 0)
            rd_kafka_poll(rk, 100);

        /* Destroy topic */
        rd_kafka_topic_destroy(rkt);

        /* Destroy the handle */
        rd_kafka_destroy(rk);

    } 

    /* Let background threads clean up and terminate cleanly. */
    rd_kafka_wait_destroyed(2000);

    return 0;
}
