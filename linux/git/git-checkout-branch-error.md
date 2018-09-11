项目上有一个分支test，使用git branch -a看不到该远程分支，直接使用命令git checkout test报错如下：
```
error: pathspec 'origin/test' did not match any file(s) known to git.
```

## 解决方法： 
1. 执行命令`git fetch`取回所有分支的更新

2. 执行`git branch -a`可以看到test分支（已经更新分支信息）

3. 切换分支`git checkout test`
