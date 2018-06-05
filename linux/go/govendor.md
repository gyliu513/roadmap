```
go get -u github.com/kardianos/govendor
```
```
govendor init
```

```
govendor add +external
```

```
状态	缩写状态	含义
+local	l	本地包，即项目自身的包组织
+external	e	外部包，即被 $GOPATH 管理，但不在 vendor 目录下
+vendor	v	已被 govendor 管理，即在 vendor 目录下
+std	s	标准库中的包
+unused	u	未使用的包，即包在 vendor 目录下，但项目并没有用到
+missing	m	代码引用了依赖包，但该包并没有找到
+program	p	主程序包，意味着可以编译为执行文件
+outside		外部包和缺失的包
+all		所有的包
```

```
go build
```

If there are build errors, just `govendor fetch xxx` to get the missed vendor packages.

