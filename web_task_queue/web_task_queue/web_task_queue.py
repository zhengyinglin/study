#coding=utf-8
"""主进程，会额外启动2个子进程
    1 webtask 处理页面请求
    2 task  处理页面过来的任务  """

from webtask import process_web_task
from task import process_task
import multiprocessing


if __name__ == "__main__":
    tasks = multiprocessing.Queue(maxsize=10)
    results = multiprocessing.Queue(maxsize=10)
    p1 = multiprocessing.Process(target=process_web_task, args=(tasks, results))
    p2 = multiprocessing.Process(target=process_task, args=(tasks, results))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
