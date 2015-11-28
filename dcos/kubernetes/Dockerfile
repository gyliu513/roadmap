FROM klaus1982/kubernetes

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>

RUN apt-get update && apt-get install -yq supervisor 

WORKDIR $K8S_HOME

ENTRYPOINT ["./bootstrap.sh"]

