#coding=utf-8
"""task 处理任务请求
    从队列里面接收处理任务  """
#coding=utf-8
import logging
import subprocess
import os

PATH = os.path.split(os.path.abspath(__file__))[0]
logfile = os.path.join(PATH, '../log/task.log')
runshell_logfile = os.path.join(PATH, '../log/runshell.log')
q_tasks, q_results = None, None

def init_log():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', filename=logfile)


def run_shell_cmd(cmd):
    if isinstance(cmd, basestring):
        cmd = cmd.split()
    assert isinstance(cmd, list)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    return p.returncode, p.stderr.read()

def send_msg(msg, receivers):
    pass

def start_task(t):
    username, cmd, env = t["name"], t["cmd"], t["env"]
    if cmd == "build":
        #   添加自己的脚本  
        ret, errmsg = run_shell_cmd("bash building.sh %s %s" %(env, runshell_logfile))
        logging.info('cmd=%s, ret=%d', cmd, ret)
        if ret:
            send_msg("！！！编译失败！！！", username)
            logging.error(errmsg)
        else:
            send_msg("编译成功", username)
 

def process_task(tasks, results):
    global q_tasks, q_results
    q_tasks, q_results = tasks, results
    init_log()
    logging.info('START')
    while True:
        #block
        t = q_tasks.get()
        try:
            start_task(t)
        except:
            logging.exception("")
    logging.info('DONE')
