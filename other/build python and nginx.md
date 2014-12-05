编译python（ssl）和 nginx
===========================

###　　　Author:
###　　　E-mail: 979762787@qq.com
###　　　Date: 2014-12-05

===========================


#Python
下载[python](https://www.python.org/downloads/)
这里下载Python 2.7.8 源代码包 [Gzipped source tar ball (2.7.8)](https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz)
  


##编译Python

tar xvf Python-2.7.8.tgz 
cd Python-2.7.8
编译  需要几分钟
./configure  --prefix=/data/app/python
make
看有几个库没有安装，下面ssl没有安装
 
```Text
Python build finished, but the necessary bits to build these modules were not found:
_bsddb             _sqlite3           _ssl            
_tkinter           bsddb185           bz2             
dl                 imageop            readline        
sunaudiodev                                           
To find the necessary bits, look in setup.py in detect_modules() for the module's name.


Failed to build these modules:
dbm                gdbm                               
```

##安装openssl （不安装到系统默认）
下载[openssl](http://www.openssl.org/source/)
这里下载openssl-1.0.1e.tar.gz
编译安装

```Shell
tar xvf openssl-1.0.1e.tar.gz
cd  openssl-1.0.1e
./config  shared  --prefix=/data/app/openssl
make
make  install
cd ..
rm -rf openssl-1.0.1e
```


##重新编译Python
rm -rf Python-2.7.8
tar xvf Python-2.7.8.tgz 
cd Python-2.7.8

###修改编译文件
cd Python-2.7.8
vim Modules/Setup.dist

```Shell
# Socket module helper for SSL support; you must comment out the other
# socket line above, and possibly edit the SSL variable:
#SSL=/usr/local/ssl
#_ssl _ssl.c \
#       -DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
#       -L$(SSL)/lib -lssl -lcrypto
```
去掉注释 修改正ssl 路径
```Shell
# Socket module helper for SSL support; you must comment out the other
# socket line above, and possibly edit the SSL variable:
SSL=/data/app/openssl
_ssl _ssl.c \
        -DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
        -L$(SSL)/lib -lssl -lcrypto
```

vim setup.py

可以搜索ssl
```Shell

        # Detect SSL support for the socket module (via _ssl)
        search_for_ssl_incs_in = [
                              '/usr/local/ssl/include',
                              '/usr/contrib/ssl/include/'
                             ]
```
去掉注释 修改正ssl 路径
```Shell
        # Detect SSL support for the socket module (via _ssl)
        search_for_ssl_incs_in = [
                              '/data/app/openssl/include',
                              '/data/app/openssl/'
                             ]
```

```Shell
        ssl_libs = find_library_file(self.compiler, 'ssl',lib_dirs,
                                     ['/usr/local/ssl/lib',
                                      '/usr/contrib/ssl/lib/'
                                     ] )
```
去掉注释 修改正ssl 路径
```Shell
        ssl_libs = find_library_file(self.compiler, 'ssl',lib_dirs,
                                     ['/data/app/openssl/lib',
                                     ] )
```


###添加环境变量
由于openssl没有安装到系统指定路径

```Shell
export  C_INCLUDE_PATH=/data/app/openssl/include:$C_INCLUDE_PATH
export  LD_LIBRARY_PATH=/data/app/openssl/lib:$LD_LIBRARY_PATH
export  LIBRARY_PATH=/data/app/openssl/lib:$LIBRARY_PATH

```

###编译Python
make clean
./configure  --prefix=/data/app/python
make

 
```Text
Python build finished, but the necessary bits to build these modules were not found:
_bsddb             _sqlite3           _tkinter        
bsddb185           bz2                dl              
imageop            readline           sunaudiodev     
To find the necessary bits, look in setup.py in detect_modules() for the module's name.


Failed to build these modules:
dbm                gdbm                                                    
```

OK 了ssl 安装成功了


make install
```Shell
[/data/app/build/Python-2.7.8]$ /data/app/python/bin/python
Python 2.7.8 (default, Dec  5 2014, 14:15:13) 
[GCC 4.4.6 20110731 (Red Hat 4.4.6-3)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import ssl
>>> 
```

这个方式安装有个问题就是 openssl lib 库路径问题
每次使用都要export  LD_LIBRARY_PATH=/data/app/openssl/lib:$LD_LIBRARY_PATH
可以把他加到bash里面
 vim ~/.bashrc  最后一行
 export  LD_LIBRARY_PATH=/data/app/openssl/lib:$LD_LIBRARY_PATH



#Ngnix安装

依赖2个库 openssl 和pcre

##下载源代码
[nginx](http://nginx.org/en/download.html)
[openssl](http://www.openssl.org/source/)
[pcre](http://sourceforge.net/projects/pcre/)
这里下载
nginx-1.4.4.tar.gz
openssl-1.0.1e.tar.gz
pcre-8.34.zip

##编译
```Shell
mkdir build_nginx
cp ../nginx-1.4.4.tar.gz  ../openssl-1.0.1e.tar.gz ../pcre-8.34.zip .
tar xvf nginx-1.4.4.tar.gz
tar xvf openssl-1.0.1e.tar.gz
unzip pcre-8.34.zip

cd nginx-1.4.4/
./configure --with-http_stub_status_module --with-http_ssl_module --with-openssl=../openssl-1.0.1e/   --with-http_gzip_static_module  --with-pcre=../pcre-8.34/  --prefix=/data/app/nginx
make
make install
```

##nginx 配置文件
http://www.cnblogs.com/xiaogangqq123/archive/2011/03/02/1969006.html

