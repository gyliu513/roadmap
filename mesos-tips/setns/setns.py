#!/usr/bin/env python

import ctypes
import sys
import os
import subprocess

f = None
libc = ctypes.CDLL('libc.so.6')
myfd = os.open('/proc/1201/ns/mnt', os.O_RDONLY)
libc.setns(myfd, 0)

subprocess.Popen(['ls', '/tmp'])
subprocess.Popen(['ls', '/tmp', '/opt'])
