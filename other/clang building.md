编译clang
===========================

###　　　Author: 
###　　　E-mail: 979762787@qq.com
###　　　Date: 2014-9-24

===========================

传说中clang比gcc强，速度快、体检小。。。

#clang代码下载

http://clang.llvm.org/get_started.html

clang svn checkout 时间2014-09-18
	clang version 3.6.0 (trunk)
	Target: x86_64-unknown-linux-gnu
	Thread model: posix


clang gcc 要求4.7+ 这里gcc版本低需要编译高版本gcc


#编译新的gcc
http://llvm.org/docs/GettingStarted.html#requirements

```Text
Easy steps for installing GCC 4.8.2:

% wget ftp://ftp.gnu.org/gnu/gcc/gcc-4.8.2/gcc-4.8.2.tar.bz2
% tar -xvjf gcc-4.8.2.tar.bz2
% cd gcc-4.8.2
% ./contrib/download_prerequisites
% cd ..
% mkdir gcc-4.8.2-build
% cd gcc-4.8.2-build
% $PWD/../gcc-4.8.2/configure --prefix=$HOME/toolchains --enable-languages=c,c++
% make -j$(nproc)
% make install
```

./contrib/download_prerequisites 下载需要依赖，没有网络手动下载gcc依赖


```Text
http://gcc.parentingamerica.com/releases/gcc-4.9.1/
gcc-4.9.1.tar.gz

GCC 需要的额外依赖
ftp://gcc.gnu.org/pub/gcc/infrastructure/
mpc-0.8.1.tar.gz 
mpfr-2.4.2.tar.bz2
gmp-4.3.2.tar.bz2

解压文件
tar xf gcc-4.9.1.tar.gz
tar xf mpc-0.8.1.tar.gz 
tar xf mpfr-2.4.2.tar.bz2
tar xf gmp-4.3.2.tar.bz2

mv mpc-0.8.1  gcc-4.9.1/mpc
mv mpfr-2.4.2  gcc-4.9.1/mpfr
mv gmp-4.3.2  gcc-4.9.1/gmp
```


#开始编译gcc（编译时间有点久）

下面 YourPath 来代替 你的安装编译路径

```Bash
mkdir gcc-build      
cd gcc-build/
../gcc-4.9.1/configure --prefix=YourPath/build_clang/toolchains --enable-languages=c,c++
make -j$(nproc)
make install
cd ..
```
ok 程序安装到 YourPath/build_clang/toolchains/                 



#编译Clang（编译时间有点久）

http://clang.llvm.org/get_started.html

我是window svn checkup下来的的所以要转一下格式（要不configure是会出错）

```Bash
cd llvm
find . -type f | xargs dos2unix
chmod +x configure autoconf/*
cd ..
mkdir build
cd build

导入环境变量
CXX=YourPath/build_clang/toolchains/bin/g++
CC=YourPath/build_clang/toolchains/bin/gcc
export  CXX  CC

../LLVM/configure --prefix=YourPath/build_clang/clang  --with-gcc-toolchain=YourPath/build_clang/toolchains  
  --with-extra-ld-options="-Wl,-rpath,YourPath/build_clang/toolchains/toolchains/lib64 -LYourPath/build_clang/toolchains/lib64"  

make

上面编译会错误
YourPath/build_clang/build/Release+Asserts/bin/llvm-tblgen: /usr/lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found (required by YourPath/build_clang/build/Release+Asserts/bin/llvm-tblgen)
make[1]: *** [YourPath/build_clang/build/lib/IR/Release+Asserts/Intrinsics.gen.tmp] Error 1
make[1]: Leaving directory `YourPath/build_clang/build/lib/IR'

把YourPath/build_clang/toolchains/lib64 添加到gcc 路径里面
LD_LIBRARY_PATH=YourPath/build_clang/toolchains/lib64:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH

rm -rf *

../LLVM/configure --prefix=YourPath/build_clang/clang  --with-gcc-toolchain=YourPath/build_clang/toolchains  
  --with-extra-ld-options="-Wl,-rpath,YourPath/build_clang/toolchains/toolchains/lib64 -LYourPath/build_clang/toolchains/lib64"  


make  #time make VERBOSE=1
make install
```

编译好后的clang 还依赖gcc的2个lib库（可以拷到clang/lib下面）


===========clang 依赖 gcc 2个lib库
cd YourPath/build_clang/clang/bin
ldd ./clang

        linux-vdso.so.1 =>  (0x00007fffaa582000)
        libz.so.1 => /lib64/libz.so.1 (0x00007f2efea8b000)
        libpthread.so.0 => /lib64/libpthread.so.0 (0x00007f2efe86e000)
        libtinfo.so.5 => /lib64/libtinfo.so.5 (0x00007f2efe64d000)
        librt.so.1 => /lib64/librt.so.1 (0x00007f2efe445000)
        libdl.so.2 => /lib64/libdl.so.2 (0x00007f2efe240000)
        libstdc++.so.6 => YourPath/build_clang/toolchains/lib64/libstdc++.so.6 (0x00007f2efdf2e000)
        libm.so.6 => /lib64/libm.so.6 (0x00007f2efdcaa000)
        libgcc_s.so.1 => YourPath/build_clang/toolchains/lib64/libgcc_s.so.1 (0x00007f2efda93000)
        libc.so.6 => /lib64/libc.so.6 (0x00007f2efd703000)
        /lib64/ld-linux-x86-64.so.2 (0x00007f2efecb0000)


#查看查找路径

YourPath/build_clang/clang/bin/clang++ --print-search-dirs


