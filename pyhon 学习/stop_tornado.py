#coding=utf-8
#比较优雅启动和重启tornado svr（单进程、单线程） 长连接不合适
#HIT 代码没有测试过
from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer
import signal
import logging
import time
import os
import sys
logging.basicConfig(level=logging.INFO)
#http://sourceforge.net/apps/trac/elpi/wiki/AlpCreatingProcesses
#http://www.keakon.net/2012/12/17/%E7%94%9F%E4%BA%A7%E7%8E%AF%E5%A2%83%E4%B8%8B%E5%A6%82%E4%BD%95%E4%BC%98%E9%9B%85%E5%9C%B0%E9%87%8D%E5%90%AFTornado
class MyTcpServer(TCPServer):
    def handle_stream(self, stream, address):
        print address
        stream.write('hello world')

    def sig_stop_handle(self, sig, frame):
        logging.warning('Caught signal : %s will stop server', sig)
        IOLoop.instance().add_callback_from_signal(self._showdown)

    def _showdown(self):
        logging.info('Stopping server')
        self.stop()
        logging.info('Will shutdown in %d seconds ...', 5)
        deadline = time.time() + 5
        def stop_loop():
            ioloop = IOLoop.instance()
            now = time.time()
            if now < deadline and not self._isfinished(ioloop):
                ioloop.add_timeout(now + 0.5, stop_loop)       
            else:
                ioloop.stop()
            logging.info('Shutdown')
        stop_loop()
        
    def _isfinished(self, ioloop):
        if ioloop._callbacks :
            return False
        for t in ioloop._timeouts:
            if t[0].callback:
                return False
        return True

    def sig_restart_handle(self, sig, frame):
        logging.warning('Caught signal : %s will restart server', sig)
        IOLoop.instance().add_callback_from_signal(self._restart)

    def _restart(self):
        logging.info('restart server')
        self._showdown()
        #http://sourceforge.net/apps/trac/elpi/wiki/AlpCreatingProcesses
        pid = os.fork()
        if pid != 0 : #parent 
            logging.info('fork in parent will quit')
            return
        logging.info('fork in child will start running')
        os.execvp("python", ['python'] + sys.argv) 
        os.abort() 




if __name__ == '__main__':
    #catch TERM , INT  
    logging.info('start running....')
    server = MyTcpServer()
    signal.signal(signal.SIGTERM, server.sig_stop_handle)
    signal.signal(signal.SIGINT, server.sig_stop_handle)
    signal.signal(signal.SIGUSR1, server.sig_restart_handle)
    server.listen(4567)
    IOLoop.instance().start()