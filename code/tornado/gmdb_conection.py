import time
import socket
import struct
import functools
from tornado.iostream import IOStream
from tornado import ioloop
import logging


class GMDBConnection(object):
    TTENOREC = 7 #not record
    MAGIC = 0xc8
    PUT = 0x10
    OUT = 0x20
    GET = 0x30
    
    def __init__(self, io_loop , addr , max_idle_time=300):
        self._io_loop = io_loop or tornado.ioloop.IOLoop.instance()
        self._stream = None
        self._addr = addr
        self._start_time = time.time()
        self._connecting = False
        self._connect_timeout = None
        self._request_timeout = None
        self._callback = None

    @property
    def alive(self):
        return ( not self._connecting ) and  self._stream
    
    def _start_connect(self , timeout=1):
        assert self._connecting == False
        if self._stream :
             self._stream.close()
             self._stream = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._stream = IOStream( sock , self._io_loop )
        self._stream.set_close_callback(self.on_close)
        # check connection timeout
        self._connect_timeout = self._io_loop.add_timeout( self._start_time + timeout,
                        functools.partial(self._on_timeout , 'connecting (%s,%d) timeout %d s' %(self._addr[0] ,self._addr[1],timeout)))
        logging.debug('start connect (%s,%d).....' % self._addr)
        self._stream.connect( self._addr, self._on_connect )
        self._connecting = True

    def _on_timeout(self , msg=None):
        if self._connecting: #timeout with connectiong
            self._connecting = False
        logging.warn('Timeout , msg=%r' % msg)
        if self._callback:
            logging.info("_on_timeout|runing callback")
            callback = self._callback
            self._callback = None
            callback('timeout')
        
    def _on_connect(self):
        logging.info('connect (%s,%d) succ' % self._addr)
        self._connecting = False
        if self._connect_timeout is not None:
            logging.info('remove _connect_timeout (%s , %d)' % self._addr )
            self._io_loop.remove_timeout(self._connect_timeout)
            self._connect_timeout = None

    def on_close(self):
        logging.warn('GMDBConnection close , Connection closed  ')
        self._connect_timeout = None
        self._request_timeout = None
        self._callback = None
        self._stream = None
        
    def close(self):
        if self._stream:
            self._stream.close()
            self._stream = None
  
    def get_data(self , petid , callback=None, timeout=3 ):
        assert self._request_timeout is None  and self._callback is None
        logging.debug('get_gmdb_data  ...')
        key = struct.pack('=Q', petid)
        buff = struct.pack('!BBI', self.MAGIC, self.GET, len(key)) + key
        self._request_timeout = self._io_loop.add_timeout(time.time() + timeout,
                                                         functools.partial(self._on_timeout , "get (%s,%d) petid %d" % (self._addr[0] ,self._addr[1], petid ) ))
        self._stream.write(buff)
        self._stream.read_bytes( 1  , self._on_get_head)
        self._callback = callback

    def _on_get_head(self , data):
        fail_code = ord(data)
        if fail_code == self.TTENOREC:
           self._on_get_body(None)
           return 
        elif fail_code:
            logging.error('_on_parse_head|get data response data ret fail , fail_code = %d'  % fail_code)
            raise Exception("_on_get_response_head fail ret = %d" % fail_code  )
        self._stream.read_bytes( 4  , self._on_get_body_len)
        
    def _on_get_body_len(self, data):
        pkg_len = struct.unpack('!I', data)[0]
        self._stream.read_bytes( pkg_len , self._on_get_body)
        
    def _on_get_body(self,data):
        if self._request_timeout:
            self._io_loop.remove_timeout(self._request_timeout)
            self._request_timeout = None
        if self._callback:
            logging.debug("_on_get_body|runing callback")
            callback = self._callback
            self._callback = None
            callback(data)

    def save_data(self , petid , value , callback=None, timeout=3):
        assert self._request_timeout is None  and self._callback is None
        logging.info('save_data  ...')
        key = struct.pack('=Q', petid)
        buff = ''.join( struct.pack('!BBII', self.MAGIC, self.PUT, len(key) , len(value) ) , key , value )
        self._request_timeout = self._io_loop.add_timeout(self._start_time + timeout,
                                                         functools.partial(self._on_timeout , "put (%s,%d) petid %d" % (self._addr[0] ,self._addr[1], petid ) ))
        self._stream.write(buff)
        self._stream.read_bytes( 1  , self._on_save_result)
        self._callback = callback

    def _on_save_result(self , data):
        fail_code = ord(data)
        if self._request_timeout:
            self._io_loop.remove_timeout(self._request_timeout)
            self._request_timeout = None
        if self._callback:
            logging.info("_on_save_result|runing callback")
            callback = self._callback
            self._callback = None
            callback(fail_code)

    def del_data(self , petid , callback=None, timeout=3):
        assert self._request_timeout is None  and self._callback is None
        logging.info('del_data  ...')
        key = struct.pack('=Q', petid)
        buff = struct.pack('!BBI', self.MAGIC, self.OUT, len(key)) + key
        self._request_timeout = self._io_loop.add_timeout(self._start_time + timeout,
                                                         functools.partial(self._on_timeout , "del (%s,%d) petid %d" % (self._addr[0] ,self._addr[1], petid ) ))
        self._stream.write(buff)
        self._stream.read_bytes( 1  , self._on_del_result)
        self._callback = callback

    def _on_del_result(self , data):
        fail_code = ord(data)
        if self._request_timeout:
            self._io_loop.remove_timeout(self._request_timeout)
            self._request_timeout = None
        if self._callback:
            logging.info("_on_del_result|runing callback")
            callback = self._callback
            self._callback = None
            callback(fail_code)
        


class SimpleAsyncGMDBClient(object):
    def __init__(self , io_loop = None, addr=('10.152.23.144',3639)):
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.addr = addr
        self.conn = GMDBConnection(self.io_loop , self.addr)
        self.conn._start_connect(1)
    def asyn_get(self , petid , callback):
        self.conn.get_data(petid , callback)
    def close(self):
        self.conn.close()



def test():
  tornado.options.parse_command_line()
  start_request()
  tornado.ioloop.IOLoop.instance().start()



if __name__ == '__main__':
   test()    
