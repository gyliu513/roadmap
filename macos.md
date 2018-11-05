## Default to root

```
LiuGuangyas-MacBook-Pro:~ gyliu$ cat .ssh/config
Host *
    User root
    CheckHostIP no
    LogLevel ERROR
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
```

## iterm2 color and GO

```
LiuGuangyas-MacBook-Pro:~ gyliu$ cat .bash_profile
export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad
# export PATH=/Users/gyliu/node/node-v5.9.1-darwin-x64/bin:$PATH

# export GOROOT=/usr/local/go
# export PATH=$PATH:$GOROOT/bin

export PATH=$PATH:/Users/gyliu/apiserver-builder/bin
#source /Users/gyliu/Downloads/git-completion.bash.txt

export GOPATH=$HOME/go

export PATH=$PATH:$GOPATH/bin:/Users/gyliu/kubebuilder_0.1.11_darwin_amd64/bin
```
