FROM ubuntu

MAINTAINER Klaus Ma <klaus1982.cn@gmail.com>

ENV TOP_DIR /opt

ADD https://storage.googleapis.com/golang/go1.5.1.linux-amd64.tar.gz /opt

ENV GOROOT $TOP_DIR/go
ENV GOPATH $TOP_DIR/godep
ENV PATH $GOROOT/bin:$PATH

RUN mkdir -p $GOPATH

RUN go get github.com/tools/godep
RUN mkdir -p $GOPATH/src/github.com/docker
WORKDIR $GOPATH/src/github.com/docker

# Build Swarm
RUN git clone https://github.com/docker/swarm
WORKDIR $GOPATH/src/github.com/docker/swarm
RUN git checkout v1.0.0
RUN $GOPATH/bin/godep go install .

# Copy swarm binary 
RUN cp $GOPATH/bin/swarm /opt/

# Cleanup build tools
RUN rm -rf $GOROOT $GOPATH

# Runtime environment
WORKDIR /opt

ENTRYPOINT ["swarm"]

