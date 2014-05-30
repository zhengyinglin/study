#coding=utf-8
'''
参考
What are the differences amongst Python's “__get*__” and “_del*__” methods?
http://stackoverflow.com/questions/9048826/what-are-the-differences-amongst-pythons-get-and-del-methods

http://b.imf.cc/blog/2013/01/18/special-methods-lookup-strategy-in-python/

关于python “__get*__” methods
__getitem___      __setitem__  __delitem__    对应 x[i] 访问
__get__           __set__      __delete__     对应descriptors
__getattr__       __setattr__  __delattr__    对应 x.name 访问
__getattribute__  
'''

"""
python 默认对象访问：
The default behavior for attribute access is to get, set, or delete the attribute from an object’s dictionary.

For instance, a.x has a lookup chain
    starting with   a.__dict__['x'],   对象字典
    then type(a).__dict__['x'],        类字典
    and continuing through the base classes of type(a) excluding metaclasses.  父类字段

    如果查找的对象是一个descriptor （定义 __get__ __set__ __delete__ 方法） 查找则是调用descriptor method 
   
"""


#__getitem__, __setitem__, __delitem__  -->x[i]  x[i]=val  del x[i] 操作  
# Are methods that can be defined to implement container objects.
class MyColors(object):
    def __init__(self):
        self._colors = {'yellow': 1, 'red': 2, 'blue': 3}

    def __getitem__(self, name):
        print name , 'MyColors.__getitem__' 
        return self._colors.get(name, "not found")

    def __setitem__(self, name , value):
        print name , 'MyColors.__setitem__' , value 
        self._colors[name] = value

    def __delitem__(self , name):
        print name , 'MyColors.__delitem__' 
        self._colors.pop(name)

print '============__getitem__, __setitem__, __delitem__ ====='       
colors = MyColors()
print colors['yellow']   #yellow MyColors.__getitem__  \n  1
colors['red'] = 9999     #red MyColors.__setitem__ 9999
print colors._colors     #{'blue': 3, 'red': 9999, 'yellow': 1}
del colors['red']        #red MyColors.__delitem__
print colors._colors     #{'blue': 3, 'yellow': 1}


#__getattr__,__setattr__, __delattr__ 操作对象属性x.name  x.name = value  del x.name
#Are methods that can be defined to customize the meaning of attribute access
#(use of, assignment to, or deletion of x.name) for class instances. 
#注意属性查找  首先检查实例本身的字典__dict__，如果存在直接返回，否则调用__getattr__

class Foo(object):
    def __init__(self):
        self.x = 10
        
    def __getattr__(self, name):
        print name , 'Foo.__getattr__'
        return name

    def __setattr__(self, name , value):
        print name , 'Foo.__setattr__' , value
        object.__setattr__(self,name,value)

    def __delattr__(self , name):
        print name , 'Foo.__delattr__'
        object.__delattr__(self,name)

print '\n\n========__getattr__  __setattr__  __delattr__==='
f = Foo()
print f.__dict__  #{'x': 10}
print f.x         #10
print f.bar       #bar Foo.__getattr__  \n bar
f.x = 1000        #x Foo.__setattr__ 1000
f.newx = 8888     #newx Foo.__setattr__ 8888
print f.__dict__  #{'x': 1000, 'newx': 8888}
del f.x           #x Foo.__delattr__
print f.__dict__  #{'newx': 8888}


# __getattribute__:Called unconditionally to implement attribute accesses for instances of the class.
#意思是这个方法在访问实例对象中的数据时，无条件地被调用的。
#这说明了getattribute在这里的最主要的作用就是一个dispatcher，我们通过重载来模拟dispatcher的效果：

# 注意如果__getattribute__ 抛出 则接着调用__getattr__
class Foo2(object):
    def __init__(self):
        self.x = 10
        
    def __getattr__(self, name):
        print name , 'Foo.__getattr__'
        return name , name

    def __getattribute__(self, name):
        print name , 'Foo.__getattribute__' 
        return object.__getattribute__(self,name)#如果没有name raise AttributeError

print '\n\n========__getattribute__ ======='
f = Foo2()
print f.x         #x Foo.__getattribute__  \n  10
print f.bar       #bar Foo.__getattribute__ \n  bar Foo.__getattr__  \n ('bar', 'bar')


"""
见文档  Descriptor HowTo Guide

 a descriptor is an object attribute with “binding behavior”,
属性的访问通过重写 __get__(), __set__(), and __delete__() 方法
定义
a data descriptor : If an object defines both __get__() and __set__()
non-data descriptors :  only define __get__()



前面已经知道__getattribute__ 总是会调用的，descriptor 是有__getattribute__ 调用的

关于obj.d

如果obj 是一个类class
    type.__getattribute__() 大概方式如下
    def __getattribute__(self, key):
        "Emulate type_getattro() in Objects/typeobject.c"
        v = object.__getattribute__(self, key)
        if hasattr(v, '__get__'):
           return v.__get__(None, self)
        return v
        
如果obj是一个对象
    object.__getattribute__() which transforms b.x into type(b).__dict__['x'].__get__(b, type(b))
    查找优先权
    data descriptors > instance variables > non-data descriptors > __getattr__()
    也就是说如果obj.d 是 data descriptors 那么会会在type(obj).__dict__ 查 ，调用descriptors 的__get__ 方法、没有则在obj.__dict__...
    也就是说如果obj.d 是 non-data descriptors 那么会在 obj.__dict__ 里面查找，如果没有在type(obj).__dict__ 查调用__get__ 方法
"""

print '\n\n ========= descriptors ======'
print '""""data descriptors"""'
import random
class Die(object):
    """"data descriptors"""
    def __init__(self, sides = 6):
        self.sides = sides

    def __get__(self, obj, objtype=None):
        print 'Die.__get__' , obj , objtype , self.sides
        return int( random.random() * self.sides) + 1

    def __set__(self, obj, value):
        print 'Die.__set__' , obj, value
        self.sides = value.sides

    def __delete__(self, obj):
        pass


class Game(object):
    d6 = Die()


Game.d6           #Die.__get__ None <class '__main__.Game'> 6
g = Game()
print g.__dict__  #{}
g.d6              #Die.__get__ <__main__.Game object at 0x02087F90> <class '__main__.Game'> 6
g.d6 =  Die(1000) #Die.__set__ <__main__.Game object at 0x02087F90> <__main__.Die object at 0x020962D0>
#注意Game.d6 和 g.d6 的值同时修改（修改的是类属性）
Game.d6           #Die.__get__ None <class '__main__.Game'> 1000
g.d6              #Die.__get__ <__main__.Game object at 0x02087F90> <class '__main__.Game'> 1000

print g.__dict__  #{}

#添加对象"d6"
g.__dict__["d6"] = "None None"
print g.__dict__  #{'d6': 'None None'}
#访问g.d6  没有改变  data descriptors  > instance variables
g.d6              #Die.__get__ <__main__.Game object at 0x02137F90> <class '__main__.Game'> 1000

 


print '""""not data descriptors"""'
class Die2(object):
    """"not data descriptors"""
    def __init__(self, sides = 6):
        self.sides = sides

    def __get__(self, obj, objtype=None):
        print 'Die2.__get__' , obj , objtype , self.sides
        return int( random.random() * self.sides) + 1

class Game2(object):
    d6 = Die2()


Game2.d6           #Die2.__get__ None <class '__main__.Game2'> 6
g = Game2()
print g.__dict__   #{}
g.d6               #Die2.__get__ <__main__.Game2 object at 0x02176B90> <class '__main__.Game2'> 6

#添加对象"d6"
g.__dict__["d6"] = "None None"
print g.__dict__   #{'d6': 'None None'}
#在__dict__中查找 instance variables > non-data descriptors
print g.d6

