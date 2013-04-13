#coding=utf-8
"""
an adopt udp connection used by tornado.

"""
import functools
import time
import socket
from tornado import ioloop
import logging


class UDPClient(object):
    def __init__(self, io_loop=None):
        self._socket = None
        self._state = None
        self._read_callback = None
        self._read_timeout = None
        self._io_loop = io_loop or ioloop.IOLoop.instance()
        self._init_socket()

    def _init_socket(self):
        self.close()
        # udp
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self._socket.setblocking(False)
        print '_init_socket succ'
        
    def close(self):
        print  'warning  _close_socket'
        if self._socket is not None:
            if self._state is not None:
                self._io_loop.remove_handler(self._socket.fileno())
                self._state = None
            self._socket.close()
            self._socket = None
        self._read_callback = None
        self._read_timeout = None

    def _add_io_state(self, state):
        if self._state is None:
            self._state = ioloop.IOLoop.ERROR | state
            self._io_loop.add_handler(
                self._socket.fileno(), self._handle_events, self._state)
        elif not self._state & state:
            self._state = self._state | state
            self._io_loop.update_handler(self._socket.fileno(), self._state)

    def _handle_events(self, fd, events):
        if events & self._io_loop.READ:
            self._handle_read()
        #if events & self._io_loop.WRITE:
        #    self._handle_write()
        if events & self._io_loop.ERROR:
            logging.error('%s event error' % self)
            
    def send_data(self , buff ,addr , callback , timeout=5):
       try:
           num_bytes = self._socket.sendto(buff , addr)
       except socket.error, e:
            #if e.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
            print 'sendto  ' , e
            raise 
       #QQQQ  should raise ???
       if num_bytes == 0:
           print 'waring sendto[bufflen=%d] but return = 0' , len(buf)
           raise Exception("sendto fail ")
       print 'send data succ ....'
       self._read_timeout = self._io_loop.add_timeout( time.time() + timeout, 
           self._on_timeout_read )
       self._add_io_state(ioloop.IOLoop.READ)
       self._read_callback = callback

    def _on_timeout_read(self):
        if self._read_callback:
            callback = self._read_callback
            self._read_callback = None
            callback("TIMEOUT")

    def _handle_read(self):
        if self._read_timeout:
            self._io_loop.remove_timeout(self._read_timeout)
            self._read_timeout = None
        try:
            data , addr = self._socket.recvfrom(2048) # 2K
            print 'recv data len=' , len(data)
        except socket.error, e:
            if e.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                print 'hahahah'
                return None
            else:
                raise
        if self._read_callback:
            callback = self._read_callback
            self._read_callback = None
            callback(data)

#=====================test====================
from petapi import petid
import tornado.ioloop
import tornado.options
udp = UDPClient()

def test():
    req = petid.AdoptPkg(uin=979762787)
    udp.send_data(req.pack() ,('10.12.17.125' , 6298) , petidresp )

def petidresp(data):
    print 'len=' , len(data)
    print data
    resp = petid.GetAdoptResponse()
    resp.unpack(data)
    print 'petid' , resp.getpetid()
    test()

if __name__ == '__main__': 
  tornado.options.parse_command_line()
  test()
  tornado.ioloop.IOLoop.instance().start()
    
    
