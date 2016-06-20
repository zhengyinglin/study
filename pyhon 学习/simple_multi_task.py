#coding=utf-8
"""多任务转换多进程并发处理"""

import logging
import multiprocessing
logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

def process_task(task):
    logger.info("task[%r] process OK", task)
    return task, True

class TaskProcess(multiprocessing.Process):
    def __init__(self, task_queue, result_queue, exit_flag, process_function):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.exit_flag = exit_flag
        self.process_function = process_function

    def run(self):
        while not self.task_queue.empty():
            task = self.task_queue.get()
            if self.exit_flag.value:
                succ = False
            else:
                succ = self._do_task(task)
                if not succ:
                    self.exit_flag.value = 1
            self.result_queue.put((self.name, task, succ))

    def _do_task(self, task):
        try:
            self.process_function(task)
        except:
            logger.exception("%r", task)
            return False
        return True 

def run_tasks(task_queue, process_num, process_function):
    if process_num < 1:
        process_num = 1
    task_result = multiprocessing.Queue()
    task_exit = multiprocessing.Manager().Value('i', 0, lock=True)
    task_num = task_queue.qsize()
    tasks = [ TaskProcess(task_queue, task_result, task_exit, process_function) 
                for i in xrange(process_num) ]
    for t in tasks:
        t.start()
    for t in tasks:
        t.join()
    fail_results = []
    while task_num > 0:
        task_name, task, succ = task_result.get()
        logger.info('%s: %r: %s', task_name, task, succ)
        if not succ:
            fail_results.append( task_name )
        task_num -= 1
    if not fail_results:
        logger.info("------- DONE PROCESS OK---------")
    else:
        for task_name in fail_results:
            logger.error("!!!!!! ERROR task[%s] Failed !!!!!", task_name)
    
if __name__ == '__main__':
    task_queue = multiprocessing.Queue()
    process_num = multiprocessing.cpu_count()/2
    tasks = [ "task_%d" % i for i in range(4) ]
    for task in tasks:
        task_queue.put(task)
    run_tasks(task_queue, process_num, process_task)

