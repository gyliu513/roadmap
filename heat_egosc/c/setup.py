#!/usr/bin/env python
 
# $Id: setup.py,v 1.1.2.5 2013/06/24 05:34:20 xianwu Exp $
 
import commands
from distutils.core import Extension
from distutils.core import setup
import os
 
# Adjust 'ego_top_dir' to be the top-level ego directory if working outside of
# the CVS tree hierarchy
 
ego_top_dir = '../../../..'
lib_base_dir = '/pcc/lsfqa-trusted/blue/drs_ext/havana/'
third_lib_base_dir = '/pcc/lsfqa-trusted/blue/ego_ext/3.1/'
icu_lib_dir = '%s/icu/3.2/' % third_lib_base_dir
libxml2_lib_dir = '%s/libxml2/2.6.20/' % lib_base_dir
openssl_lib_dir = '%s/openssl/0.9.8c/' % lib_base_dir
 
 
HOME = os.environ.get('HOME')
LM_ARCH = 'fail'
(status, output) = commands.getstatusoutput("uname -m")
if status == 0 and output == 'ppc64':
    LM_ARCH = 'linux2.6-glibc2.5-ppc64'
elif status == 0 and output == 's390x':
    LM_ARCH = 'linux2.6-glibc2.5-s390x'
else:
    LM_ARCH = 'linux2.6-glibc2.3-x86_64'
 
# Create instance of 'Extension' class
module1 = Extension('ego',
        sources=[
                'egomodule.c'
                ],
        include_dirs=[
                ego_top_dir + '/kernel',
                ego_top_dir + '/kernel/lib',
                ego_top_dir + '/eservice/esc',
                ],
        extra_link_args=[
                '-L' + ego_top_dir + '/kernel/lib/static',
                '-L' + ego_top_dir + '/kernel/modules/util/static',
                '-L' + ego_top_dir + '/eservice/esc/lib/static',
                '-L' + libxml2_lib_dir + LM_ARCH + '/lib',
                '-L' + openssl_lib_dir + LM_ARCH + '/lib',
                '-L' + ego_top_dir + '/kernel/lib',
                '-L' + icu_lib_dir + LM_ARCH + '/lib',
                '-lstdc++', '-lvem', '-lpccutilstatic', '-L/usr/lib',
                '-lxml2', '-lz', '-lm', '-L/usr/kerberos/lib',
                '-lssl', '-lcrypto', '-ldl', '-lz', '-lsicui18n',
                '-lsicuuc', '-lsicudata', '-lsicuio'
                ])
 
# Invoke setup() function to define the VEM Python extension
setup(name='EGO',
        version='1.0',
        description='EGO Python bindings',
        long_description='FOR OPENSTACK DRS INTEGRATION',
        author='Guangya Liu',
        author_email='liugya@cn.ibm.com',
        ext_modules=[module1])
