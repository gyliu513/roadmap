#!/usr/bin/expect
set timeout 5
set userName liugya@cn.ibm.com
set password xxx

spawn telnet 9.111.250.181
expect "Username:"
send "$userName\r"
expect "Password:"
send "$password\r";
expect eof

spawn telnet 9.21.63.60
expect "Username:"
send "$userName\r"
expect "Password:"
send "$password\r";
expect eof

spawn telnet 9.111.143.202
expect "Username:"
send "$userName\r"
expect "Password:"
send "$password\r";
expect eof

spawn telnet x1
expect "Username:"
send "$userName\r"
expect "Password:"
send "$password\r";
expect eof
