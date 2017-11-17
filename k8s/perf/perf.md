Skip to content
This repository
Search
Pull requests
Issues
Marketplace
Explore
 @gyliu513
 Sign out
View Repository
 Watch 1
  Star 0  Fork 0 mengjieli0726/System-Testing  
 Code
 Issues 0
 Pull requests 0
 Boards
 Reports
 Projects 0
 Wiki
 Insights
You’re editing a file in a project you don’t have write access to. We’ve created a fork of this project for you to commit your proposed changes to. Submitting a change to this file will write it to a new branch in your fork, so you can send a pull request.
System-Testing/ 
System_testing_tools.md
   or cancel
    
 Edit file    Preview changes
1
# #_Tools or Scripts of Performance Testing_
2
​
3
## Performance Testing
4
​
5
_Configure the SSH passwordless_
6
​
7
                #!/bin/bash
8
                for a in $(seq 1 3)
9
                do
10
                       sshpass -p 'Letmein123' ssh-copy-id -o StrictHostKeyChecking=no  root@cfc1m${a}p.ma.platformlab.ibm.com
11
                
12
                done
13
​
14
​
15
_**Remote enable docker service on all nodes**_
16
​
17
   1. Create the docker repo and dependency package repo
18
                        
19
                        cat << EOF >> /etc/yum.repos.d/docker.repo
20
                        
21
                        [dockerrepo]
22
                        name=Docker Repository
23
                        baseurl=http://ftp.unicamp.br/pub/ppc64el/rhel/7_1/docker-ppc64el/
24
                        proxy=http://9.21.53.14:3128
25
                        enabled=1
26
                        gpgcheck=0
27
                        #gpgkey=https://yum.dockerproject.org/gpg
28
                        
29
                        EOF
30
                        
31
                        cat << EOF >> /etc/yum.repos.d/platformlab.repo
32
                                
33
                        [rhel-server-7.2-x86_64]
34
                        name=Red Hat Enterprise Linux $releasever - $basearch
35
                        gpgcheck=0
36
                        enabled=1
37
                        proxy=http://9.21.53.14:3128
38
                        baseurl=http://yum.platformlab.ibm.com/deploy/yum/redhat/releases/rhel-server-7.2-ppc64le/              
39
                
40
                        EOF
41
​
42
                
43
  2. Remote install docker engine and start docker service, check docker version.
44
​
45
                        #/bin/bash
46
                        
47
                        for a in $(seq 1001 1060)
48
                        
49
                        do
@gyliu513
Propose file change

Update System_testing_tools.md

Add an optional extended description…
Propose file change  Cancel 
 Waiting for your fork…
© 2017 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
API
Training
Shop
Blog
About
