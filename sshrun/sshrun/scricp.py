#coding=utf-8
'''
这个脚本是执行命令行 sshrun [ -f sshfile.py ]  command

command 定义在 sshfile.py  里面的函数
'''
import argparse
import os
import sys

def add_module_path(path):
    assert os.path.isdir(path)
    path = os.path.realpath(path) 
    if path not in sys.path:
        sys.path = [path] + sys.path


def process():
    parser = argparse.ArgumentParser(description='SSH2 Clinet')
    parser.add_argument('-f' , '--file' , type = str , default='sshfile.py' ,
                        help = 'ssh file path defualt local sshfile.py ')
    parser.add_argument('command' , type = str )

    args = parser.parse_args()
    sshfile =  os.path.abspath( args.file )

    if  not os.path.isfile(sshfile):
        print """Couldn't find any sshfile.py---%s!

Remember that -f can be used to specify sshfile.py path, and use -h for help.""" % sshfile
        sys.exit()

    directory, sshfile = os.path.split(sshfile)
    add_module_path(directory)
    module = __import__( os.path.splitext(sshfile)[0] ) # remove .py
    
    getattr(module , args.command )()

if __name__ == '__main__':
    process()

