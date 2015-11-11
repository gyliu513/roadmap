INCLUDE=/root/librdkafka/include
LIBS=/root/librdkafka/lib/librdkafka.a
CFLAGS=-O2 -fPIC -Wall -Wfloat-equal -Wpointer-arith
CC=g++

nereus_send: nereus_send.c
	${CC} ${CFLAGS} -I${INCLUDE} $< -o $@ ${LIBS} -lpthread -lz -lrt

clean:
	rm -f nereus_send
