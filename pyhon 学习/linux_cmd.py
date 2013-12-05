# -*- coding: utf8 -*-
'''
linux  cmd find cat grep   python generator implement
'''

import os
import fnmatch
import re


def gen_find(filepat , top):
    for path , dirlist , filelist in os.walk(top):
        for name in fnmatch.filter(filelist , filepat):
            yield  os.path.join(path , name)

#print list( gen_find("*.txt" , "e:\\") )


def gen_cat(sources):
    for s in sources:
        for item in s:
            yield item

def gen_grep(pat , lines):
    patc = re.compile(pat)
    for line in lines:
        if patc.search(line):
            yield line


