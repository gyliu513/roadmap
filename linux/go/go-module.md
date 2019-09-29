## 项目目录下，执行以下命令初始化
```
go mod init
```
## 执行以下命令会自动分析项目里的依赖关系同步到go.mod文件中，同时创建go.sum文件
```
go mod tidy
```
## 以上的管理依赖管理操作，所以依赖包还是在GOPATH/src目录下，go module 当然可以把包直接放在当前项目中管理
```
go mod vendor
```
直接使用这个命令就可以把GOPATH/src目录下的依赖包同步到当前项目目录中
