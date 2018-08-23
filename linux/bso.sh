#!/usr/bin/expect
set timeout 2
set username xxx
set password xxx

proc login { host username password } {
    spawn telnet $host
    expect {
        "Username:" {
            send "$username\r"
            expect "Password:"
            send "$password\r";
            expect eof
        }
        "Unable to connect to remote host" {
            expect eof
        }
        "Connection refused" {
            expect eof
        }
    }
}

set running [login "9.111.250.2" $username $password]
set running [login "9.21.63.1" $username $password]
set running [login "9.111.143.1" $username $password]
