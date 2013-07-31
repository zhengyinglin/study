#!/usr/bin/env python

from setuptools import setup


setup(
    name = 'sshrun',
    version = '1.0',
    description = 'SSHrun is a tool running remote command and copying remote file (just encapsulated  paramiko.SSHClient)',
    long_description = open('README.txt').read() , 
    author = 'ghostzheng',
    author_email = '979762787@qq.com',
    url = 'www.xxx.com',
    packages = ['sshrun'],
    install_requires = ['paramiko>=1.10.1'],
    entry_points = {
        'console_scripts': [
            'sshrun = sshrun.scricp:process',
        ]
    },
)
