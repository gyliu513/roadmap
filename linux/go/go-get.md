```
mkdir -p $GOPATH/src/golang.org/x
cd $GOPATH/src/golang.org/x
git clone https://github.com/golang/tools.git
git clone https://github.com/golang/lint.git
完成以上步骤后，执行
go get golang.org/x/lint/golint
成功安装golint ，亲测有效
```
