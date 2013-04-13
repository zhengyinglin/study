# -*- coding: utf-8 -*-
"""

提供3个类

Package =  fields(包头) + data 类型的请求包
           只提供简单的拆解数据包，pack 和 unpack

TCPClient  简单socket 客户端(TCP)，   
UDPClient  简单socket 客户端(UDP)，
          只简单提供socket的收发包 send_and_recv

对于具体的请求包，可以继承Package类

"""


import itertools
import struct
import array
import socket

#例外
class UnpackError(Exception): pass
class PackError(Exception): pass
class NetworkError(Exception): pass

class GeneratedPackageDataType(type):
    '''元类  用来生成包结构，包体元素基于 python struct.pack/unpack 类型
       package = h_fields + _data
    '''
    def __new__(cls, name, bases, dictionary):
        dictionary['__slots__'] = [
                             '_hdr_fields',  #(dict) 存储包的各个域名称对应的值
                             '_hdr_fmt', #(str)  pack/unpack 格式顺序
                             '_hdr_len', # = struct.calcsize( _hdr_fmt )
                             '_data',  # 去除掉_fields 内容后 的值
                             ]
        superclass = super(GeneratedPackageDataType, cls)
        new_class = superclass.__new__(cls, name, bases, dictionary)
        return new_class
 
    def __init__(cls, name, bases, dictionary):
        # name list
        cls.__hdr_fields_name__ = [ f[0] for f in cls.__hdr__ ]  
        if len( set(cls.__hdr_fields_name__) ) !=  len( cls.__hdr_fields_name__ ) :
           l = cls.__hdr_fields_name__[:]
           for n in set(cls.__hdr_fields_name__):
              l.remove(n)
           l.append("Duplicate fields name")
           raise Exception('\t'.join(l))

        _AddInitMethod(cls)
        # fields = {name:value}
        for fieldname  in  cls.__hdr_fields_name__ :
            _AddPropertiesForField(cls , fieldname )
        superclass = super(GeneratedPackageDataType, cls)
        superclass.__init__(name, bases, dictionary)

 
def _AddInitMethod(cls):
    """添加  __init__ 方法到类 cls 里面"""
    def init(self, **kwargs):
        # fields = {name:value}
        self._hdr_fields = dict( itertools.izip(cls.__hdr_fields_name__ ,
                                [ f[2] for f in cls.__hdr__ ]) )
        self._data = ""
        self._hdr_fmt = cls.__hdr_byte_order__ +  \
                          ''.join( [ f[1] for f in cls.__hdr__ ] )
        self._hdr_len = struct.calcsize( self._hdr_fmt )
 
        for field_name, field_value in kwargs.iteritems():
            if field_name not in self._hdr_fields:
                raise TypeError("%s() got an unexpected keyword argument '%s'" %
                                (field_name, str(field_value)) )
            self._hdr_fields[field_name] = field_value
    init.__module__ = None
    init.__doc__ = None
    cls.__init__ = init
    
 
def _AddPropertiesForField(cls , fieldname ):
    """添加 fields 属性 到类 cls """
    def getter(self):
        return self._hdr_fields[fieldname]
    getter.__module__ = None
    getter.__doc__ = None
    def setter(self, new_value):
        self._hdr_fields[fieldname] = new_value
    setter.__module__ = None
    setter.__doc__ = None
    # Add a property to encapsulate the getter/setter.
    setattr(cls, fieldname, property(getter, setter))
 



class Package(object):
    ''' 包类 Package = 包头(fields) + data 类型的请求包
        __hdr__ 包头 元素 的定义( 名字 , 类型(格式) , 默认值)   如 __hdr__ = ( ('length', 'H', 0), ...  )
                目前类型只支持 python  struct.pack/unpack 里面的格式 如 bBhHiI ...
        __hdr_byte_order__   拆解包的格式@=<>!   网络序、标准等
        )
    '''
    __metaclass__ = GeneratedPackageDataType
    __hdr__ = () #  定义包头元素类型  (('length', 'H', 0),  ... (名字 , 类型(格式) , 默认值 ) )
    __hdr_byte_order__ = '='  # @=<>!  see python struct module  默认标准方式

    def __repr__(self):
        descs = [ "%s = %r" % (name,getattr(self, name))  for name in self.__hdr_fields_name__ ]
        return '%s = {\n%s\n)\n' % (self.__class__.__name__, '\n'.join(descs))
    
    def __str__(self):
        return self.pack()

    def __len__(self):
        return self._hdr_len + len(self._data)

    def pack_hdr(self):
        try:
            return struct.pack(self._hdr_fmt,
                            *[ getattr(self, name) for name in self.__hdr_fields_name__ ] )
        except struct.error , e:
            raise PackError(e)
    
    def pack(self):
        return self.pack_hdr() + self._data

    def unpack_hdr(self , buf):
        try:
            for name, value in itertools.izip(self.__hdr_fields_name__,
                                              struct.unpack(self._hdr_fmt, buf)):
                setattr(self, name, value)
        except struct.error , e:
            raise UnpackError(e)
            
    def unpack(self, buf):
        self.unpack_hdr( buf[:self._hdr_len] )
        self._data = buf[self._hdr_len:]



class TCPClient(object):
   '''简单 tcp 协议'''
   def __init__(self, address, timeout=10):
       self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.sock.settimeout(timeout)
       self.sock.connect(address)
       self.address = address

   def send_and_recv(self , req , resp):
       self.sock.sendall( req.pack() )
       head_len = resp.pkg_head_len()
       buff = self.sock.recv( head_len )
       while len(buff) < head_len:
            chunk = self.sock.recv(head_len - len(buff))
            if chunk == '':
                raise NetworkError("socket connection broken(%s:%d)" % self.address[0] ,self.address[1] )
            buff += chunk
       resp.unpack_head(buff)
       pkg_len = resp.get_pkg_len()
       buff +=  self.sock.recv(pkg_len - head_len)
       while pkg_len > len(buff):
           chunk = self.sock.recv(pkg_len - len(buff))
           if chunk == '':
               raise NetworkError("socket connection broken(%s:%d)" % self.address[0] ,self.address[1] )
           buff += chunk
       resp.unpack(buff)

   def close(self):
       self.sock.close()

   def reconnect(self , address = None):
       if address :
           self.address = address
       self.close()
       self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.sock.settimeout(timeout)
       self.sock.connect(self.address)
       

   def __enter__(self):
      return self

   def __exit__(self, exc_type, exc_value, traceback):
      self.close() 



class UDPClient(object):
    '''简单udp 协议'''
    def __init__(self,address,timeout=10 ,  maxrecvlen=2048):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(timeout)
        self.address = address
        self.maxrecvlen = maxrecvlen
        
    def close(self):
        self.sock.close()
    
    def send_and_recv(self, req , resp):
        if 0 == self.sock.sendto(req.pack() ,  self.address ):
            raise NetworkError("socket connection broken sendto(%s:%d) fail " % self.address[0] ,self.address[1] )
        #udp 协议 不会出现tcp那种粘包情况，收到的包一定是完整的包 ， 如何包不完整，则是缓冲不足
        buff ,addr = self.sock.recvfrom(self.maxrecvlen)
        if buff == '':
           raise NetworkError("socket connection broken recvfrom(%s:%d) fail" % self.address[0] ,self.address[1] )
        resp.unpack(buff)

    #with statement
    def __enter__(self):
        return self
    def __exit__(self, typ, value, tb):
        self.close()




##############################
class XXXPackage(Package):
    __hdr__ = (
        ('length', 'H', 0),
        ('uid' , 'I', 0),
        ('cmdid',   'H', 0),
        )
    __hdr_byte_order__ = '!'  # network (= big-endian)


class ProtoRequest(object):
    '''包体内容是Protobuf编码的简单封装  请求包'''
    def __init__(self, msg ,**kwargs):
        self.pkg = XXXPackage(**kwargs)
        self.msg = msg

    def pack(self):
        self.pkg._data = self.msg.SerializeToString()
        self.pkg.length = len(self.pkg)
        return  self.pkg.pack()

    def unpack_head(self , buf):
        self.pkg.unpack_hdr(buf)

    def unpack(self, buf):
        self.pkg.unpack(buf)
        self.msg.ParseFromString( self.pkg._data )

    def pkg_head_len(self):
        return self.pkg._hdr_len

    def get_pkg_len(self):
        return self.pkg.length
    
    def getmsg(self):
        return self.msg

