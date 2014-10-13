python 库打包
===========================
###　　Data: 2014-10-13
###　　E-mail: 979762787@qq.com

===========================


#文件夹布局
```Shell
mypackage/
|-- mypackage
|   |-- __init__.py
|   |-- module.py
|   `-- test
|       `-- test.py
|-- demos
|   `-- example.py
|-- MANIFEST.in
|-- README
`-- setup.py
```

* mypackage: 顶层目录，包文件名这类
* mypackage/mypackage：具体python 包 源文件
    * `__init__.py`
        The `__init__.py` python 包必须的，内容可以是空，或者做一些检查处理工作
* README
    写一些描述或者文档

* MANIFEST.in
    记录哪一些文件需要打包到发布安装包里面（mypackage-1.xx.tar.gz）

* setup.py
    具体打包程序



## MANIFEST.in

```Text
include demos/*.py
recursive-include mypackage/test  *.py
```

* include  file  - 哪一些文件会被打包到安装包里面
* recursive-include path file - 递归查找，满足条件会被打包到安装包里面

具体语法 ([可以查看文档](https://docs.python.org/2/distutils/sourcedist.html#commands))


## setup.py

setup.py [官方文档](https://docs.python.org/2/distutils/setupscript.html)
```Python
#coding=utf-8
from distutils.core import setup

setup(name = "mypackage", 
    version = "1.2.0",
    description = "for exmaple",
    author = "zhengyinglin",
    author_email = "979762787@qq.com",
    url = "whatever",
    packages = ['mypackage'], #具体包，默认会去掉test
    long_description = """Really long text here.""" 
) 
#最终会生成 mypackage-1.2.0.tar.gz (name + version + tar.gz) 
```


生成安装包，简单运行：

python setup.py sdist


```Shell
[~/mypackage]$ python setup.py sdist
running sdist
reading manifest template 'MANIFEST.in'
writing manifest file 'MANIFEST'
creating mypackage-1.2.0
creating mypackage-1.2.0/demos
creating mypackage-1.2.0/mypackage
creating mypackage-1.2.0/mypackage/test
making hard links in mypackage-1.2.0...
hard linking README -> mypackage-1.2.0
hard linking setup.py -> mypackage-1.2.0
hard linking demos/example.py -> mypackage-1.2.0/demos
hard linking mypackage/__init__.py -> mypackage-1.2.0/mypackage
hard linking mypackage/module.py -> mypackage-1.2.0/mypackage
hard linking mypackage/test/__init__.py -> mypackage-1.2.0/mypackage/test
hard linking mypackage/test/test.py -> mypackage-1.2.0/mypackage/test
creating dist
tar -cf dist/mypackage-1.2.0.tar mypackage-1.2.0
gzip -f9 dist/mypackage-1.2.0.tar
tar -cf dist/mypackage-1.2.0.tar mypackage-1.2.0
gzip -f9 dist/mypackage-1.2.0.tar
removing 'mypackage-1.2.0' (and everything under it)
```

会生成MANIFEST 文件和 dist和目录

```Shell
mypackage/
|-- MANIFEST
|-- dist
|   `-- mypackage-1.2.0.tar.gz


cd dist && tar xvf mypackage-1.2.0.tar.gz 

mypackage-1.2.0
|-- PKG-INFO
|-- README
|-- demos
|   `-- example.py
|-- mypackage
|   |-- __init__.py
|   |-- module.py
|   `-- test
|       |-- __init__.py
|       `-- test.py
`-- setup.py

```


## 例子(C扩展 cython)
```Python
#coding=utf-8

##################  for pypy 
import distutils.unixccompiler
exetable = distutils.unixccompiler.UnixCCompiler.executables
exetable['compiler'][0] = 'g++'
exetable['compiler_so'][0] = 'g++'
exetable['compiler_cxx'][0] = 'g++'
exetable['linker_so'][0] = 'g++'
exetable['linker_exe'][0] = 'g++'


###############  for python 
import os
os.environ['CC'] = 'g++'


from distutils.core import setup
from distutils.extension import Extension

#http://stackoverflow.com/questions/4505747/how-should-i-structure-a-python-package-that-contains-cython-code/4515279#4515279
try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True


ROOT_PATH =  os.path.split( os.path.abspath(__file__) )[0]
cmdclass = { }

if use_cython:
    PROJECT = os.path.abspath( os.path.join( ROOT_PATH , '../../' ) )
    EXT_LIB_PATH = os.path.join( PROJECT , 'ext/xxx_libs/' )
    cmdclass.update({ 'build_ext': build_ext })
    sources = [  'pkg/xxx_api.pyx' ]
else:
    EXT_LIB_PATH = 'ext' 
    sources = [  'pkg/xxx_api.cpp' ]

ext_modules = [   Extension(
                             "pkg.xxx_api",  sources, 
                             language="c++",  
                             include_dirs=[ EXT_LIB_PATH, 'pkg'] ,
                             # for xxx_api static lib
                             extra_objects = [ os.path.join( EXT_LIB_PATH , 'libxxx.a' ) ]
                            )
             ]


setup(
  name = 'pkg',
  description='......', 
  cmdclass = cmdclass ,
  ext_modules = ext_modules,
  packages = ["pkg"],
  version="1.2.3",
  author="zhengyinglin",
  author_email = '979762787@qq.com',
  url = 'xx.yy.com'
)


```