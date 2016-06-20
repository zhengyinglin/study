#coding=utf-8
"""webtask 处理页面请求
    基于tornado"""

import os
import tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.log import app_log
import collections
import datetime

local_dir = os.path.split(os.path.abspath(__file__))[0]
logfile = os.path.join(local_dir, '../log/webtask.log')
q_tasks, q_results = None, None
operator_infos = collections.deque()

class MailHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', wait_num=q_tasks.qsize(), items=operator_infos)


class TaskHandler(tornado.web.RequestHandler):
    def post(self):
        cmd = self.get_argument("cmd", "")
        env = self.get_argument("env", "")
        name = "" #self.get_cookie('username')
        q_tasks.put_nowait({"cmd": cmd, "env": env, "name": name})
        self.write('{"ret": 0, "msg": "处理已经接受，请等待"}')
        cmd_trans = {"build": "编译"}
        env_trans = {"dev": "开发环境"}
        info = "%s %s %s %s" % (datetime.datetime.today(), name, env_trans.get(env, "未知环境"), cmd_trans.get(cmd, "未知命令"))
        global operator_infos
        operator_infos.appendleft(info)
        if len(operator_infos) > 10:
            operator_infos.pop()


def process_web_task(tasks, results):
    global q_tasks, q_results
    q_tasks, q_results = tasks, results
    settings = {
        "template_path": os.path.join(local_dir, "templates"),
        "static_path": os.path.join(local_dir, "static"),
    }
    app = tornado.web.Application([
        (r"/", MailHandler),
        (r"/add_task", TaskHandler),
        ], **settings)
    tornado.options.parse_command_line(['--logging=DEBUG', '--log_file_prefix=%s' % logfile])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(9000)
    tornado.ioloop.IOLoop.instance().start()
