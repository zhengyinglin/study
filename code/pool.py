#coding=utf-8

import time
import collections
import threading

class Connection(object):

    def last_active_time(self):
        raise NotImplemented
    
    def close(self):
        raise NotImplemented


class ConnectionPool(object):
    def __init__(self, pool_name ,factory, max_size=10, max_idie_time=600.0 ,
                  *args, **kwargs):
        '''max_size : 连接池最多缓存多少个连接
           max_idie_time: 连接最大空闲时间，如果超过该值，该连接将抛弃
           factory:  create concrete conn object '''
        assert isinstance(pool_name, (str, unicode))
        assert max_size >= 0
        self.max_size = max_size
        self.pool_name = pool_name
        self.factory = factory
        self.max_idie_time = max_idie_time
        self._pool = collections.deque()
        self.args , self.kwargs = args, kwargs

    def cache(self , conn):
        if self.max_size > len(self._pool) :
            self._pool.append(conn)
        else:
            conn.close()

    def close(self):
        while self._pool:
            conn = self._pool.popleft()
            conn.close()

    def connection(self):
        now = time.time()
        while self._pool:
            conn = self._pool.popleft()
            if conn.last_active_time() > self.max_idie_time:
                conn.close()
            else:
                return conn
        conn = self.factory(self.args , self.kwargs)
        return conn


class ConnectionPools(object):
    @classmethod
    def get_connection_pool(self, pool_name , factory, max_size=10, max_idie_time=600.0 ,
                            *args, **kwargs):
        if not hasattr(self, '_pools'):
            with threading.Lock():
                 if not hasattr(self, '_pools'):
                     self._pools = {}
        if pool_name not in self._pools:
            self._pools[pool_name] = ConnectionPool(pool_name, factory,
                                                    max_size, max_idie_time , *args, **kwargs)
        return self._pools[pool_name]

    @classmethod
    def close_pool(self, pool_name=None):
        if not hasattr(self, '_pools'):
            return
        if pool_name is not None:
            if pool_name not in self._pools:
                return
            self._pools[pool_name].close()
        else:
            for pool_name, pool in self._pools.items():
                pool.close()


