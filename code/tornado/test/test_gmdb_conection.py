import sys
sys.path = ['../'] + sys.path
import logging
import functools
import tornado.ioloop
import tornado.options
from  tornado import gen 
from gmdb_conection import SimpleAsyncGMDBClient


def start_request_callback():
    gmdb = SimpleAsyncGMDBClient()
    petid = 281914043137635L
    callback = functools.partial(get_data_resp , gmdb )
    gmdb.asyn_get(petid , callback= callback)

def get_data_resp(gmdb , data):
    if data is None:
        data = ""
    logging.info("Hello, world  data len=%d \n\n" % len(data) )
    gmdb.close()

@gen.engine
def start_request():
    gmdb = SimpleAsyncGMDBClient()
    petid = 281914043137635L
    for i in xrange(100):
        data = yield gen.Task(gmdb.asyn_get, petid)
        if data == 'timeout':
           print data
           break
        logging.info("seq %d  , Hello, world using yield data len=%d " %(i ,  len(data)) )
    gmdb.close()
    tornado.ioloop.IOLoop.instance().stop()


def main():
    tornado.options.parse_command_line()
    #start_request_callback()
    for i in xrange(100):
        start_request()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    import sys
    #logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.basicConfig(filename="tmplog.log" ,  level=logging.INFO , 
               format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s' )
    logging.info("start logging")
    main()

    
