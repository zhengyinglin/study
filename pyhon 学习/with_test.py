#coding=utf-8
# python with statement 


class Test(object):
    
    def __enter__(self):
        """If a target was included in the with statement,
            the return value from __enter__() is assigned to it.
        """
        print '__enter__'
        return self

    def __exit__(self, typ, value, traceback ):
        """
            If the suite was exited due to an exception,
            and the return value from the __exit__() method was false, the exception is reraised.
            If the return value was true, the exception is suppressed,and execution continues with the statement following the with statement.
        """
        print '__exit__' , type ,value ,traceback 
        return None  #如果有例外，返回值如果是None or False 会重新抛出例外；如果是ture则忽略该例外 
        


with Test() as t:
    print 'start raise'
    raise Exception("ddddd")
    print 'raiseed ..'

