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
## Check your shell

Over the years macOS / OS X changed it shell. Older version shipped with bash. Newer macOS version comes with zsh by default. Users can also set or change their default shell. Hence, first find out the default shell name for the current user. Open the terminal application and run the echo command:
```
echo "$0"
```
OR use the ps command ##
```
ps -p $$
```

You may see bash or zsh or any other shell. For example, on macOS Monterey, I see the following outputs:
```
  PID TTY           TIME CMD
 4653 ttys001    0:00.06 -zsh
```
You need to modify the following file as per your shell
```
Bash/sh – ~/.bashrc
ZSH – ~/.zshrc
```
