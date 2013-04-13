#coding=utf-8
import sys
import os

def add_module_path(path):
    assert os.path.isdir(path)
    if path not in sys.path:
        sys.path = [path] + sys.path




def compute_checksum(buf):
    '''计算效验和  '''
    nleft = len(buf)
    a = array.array('B', buf)
    i = 0
    s = 0
    while nleft > 1:
       s ^= (a[i+1] * 256 + a[i])
       i += 2
       nleft -= 2
    return s



