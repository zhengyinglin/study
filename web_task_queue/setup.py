#coding=utf-8
"""启动脚本
    启动 python setup.py start
    关闭 python setup.py stop  """
    
import subprocess
import sys
import os
import signal
import time

PATH = os.path.split(os.path.abspath(__file__))[0]
PATH = os.path.join(PATH, 'web_task_queue')
SVR = "web_task_queue.py"

try:
    os.mkdir("log")
except:
    pass

def start():
    subprocess.Popen(['python', SVR], cwd=PATH)
    print '\n'.join(get_process(SVR))

def stop():
    for line in get_process(SVR):
        pid = int(line.split(None, 2)[1])
        os.kill(pid, signal.SIGTERM)
    OK = False
    for i in xrange(3):
        infos = get_process(SVR)
        if not infos:
            OK = True
            break
        time.sleep(0.1)
    if OK:
        print 'stop OK'
    else:
        print 'warnning stop may fail...'

def get_process(name):
    p = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    res = []
    for line in out.splitlines():
        if name in line:
            res.append(line)
    return res


if __name__ == '__main__':
    cmd = sys.argv[1]
    globals()[cmd]()
