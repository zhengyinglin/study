# 多进程简单任务处理
基于队列方式执行一些比较耗时的任务请求

## 起停程序
```
cd script
python setup.py start
python setup.py stop
```

## 原理
主进程，启动2个子进程
- webtask 处理页面请求
- task  处理页面过来的任务

进程间通信用multiprocessing.Queue

## 其他
日期：2016-06-20

EMail：979762787@qq.com