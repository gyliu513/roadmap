#!/bin/sh

# check spark home

NEREUS_VER=0.1
NEREUS_JAR=nereus-$NEREUS_VER.jar


if [ -z $SPARK_HOME ]
then
    echo "SPARK_HOME is empty"
    exit 1
fi

# check nereus home
if [ -z $NEREUS_HOME ]
then
    echo "NEREUS_HOME is empty"
    exit 1
fi


NEREUS_LIBS=""

for i in `ls $NEREUS_HOME/lib`
do
    if [ -z $NEREUS_LIBS ]
    then
        NEREUS_LIBS=$NEREUS_HOME/lib/$i
    else
        NEREUS_LIBS=$NEREUS_LIBS,$NEREUS_HOME/lib/$i
    fi
done

for i in `ls $NEREUS_HOME/conf`
do
    cp $NEREUS_HOME/conf/$i $SPARK_HOME/conf
done

$SPARK_HOME/bin/spark-submit --master local[*] --jars $NEREUS_LIBS --class net.cguru.nereus.streaming.MainLoop $NEREUS_HOME/lib/$NEREUS_JAR

