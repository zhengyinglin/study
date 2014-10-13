lite-protocol buffer
====================
###　　 Date:2014-9-2
###　　 EMail: 979762787@qq.com

===========================
 

###优化选项
   
有3个选项SPEED, CODE_SIZE, or LITE_RUNTIME

* SPEED: 是默认的，
* CODE_SIZE: 感觉没什么用，（要以运行效率为代价）
* LITE_RUNTIME: 是精简版的protobuf

优化选项详细见[文档](https://developers.google.com/protocol-buffers/docs/proto?hl=zh-CN#options)



###关于LITE_RUNTIME

在proto文件加入下面代码，即可生成精简版的protobuf

```proto
option optimize_for = LITE_RUNTIME;
```

生成的代码会去掉protobuf的一些功能：descriptors and reflection （unknown_fields也去掉了，也就是说，用精简版的不会保留未知域）

编译时要注意：
```Text
The protocol buffer compiler will generate classes that depend only on the "lite" runtime library (libprotobuf-lite instead oflibprotobuf).
```

###类继承关系

一般我们定义的message如 MyMsg 继承关系是：

```Cpp
class  MyMsg: public Message
class  Message : public MessageLite 
```

使用这个LITE_RUNTIME选项后的继承关系是

```Cpp
class  MyMsg: public MessageLite
```

关于类的简单说明
```Text
MessageLite ： light weight protocol messages
Message ：adds descriptors and reflection  and Heavy I/O
```


###测试

文件test.proto内容如下：
```Proto
package  mypkg;
//option optimize_for = LITE_RUNTIME;
message TestMsg
{
   required uint32  uin = 1;
   optional string  name = 2;
   repeated int32   ids = 3;
}
message TestMsg2
{
   required uint32  uin = 1;
   optional string  name = 2;
   repeated int32   ids = 3;
   optional string  new_add_name = 4;
}
```

测试函数SerializeToString和ParseFromString用对象TestMsg
          
|数据量大小10069 |SerializeToString|| |ParseFromString||   |
|----------------|-----|------|-------|-----|------|-------|
|运行次数        |10000|100000|1000000|10000|100000|1000000|
|没有LITE_RUNTIME|0.04s|0.46s |4.68s  |0.04s|0.38s |3.81s  |
|加LITE_RUNTIME  |0.02s|0.28s |2.83s  |0.03s|0.22s |2.19s  |


|数据量大小1069  |SerializeToString |||ParseFromString||   |
|----------------|-----|------|-------|-----|------|-------|
|运行次数        |10000|100000|1000000|10000|100000|1000000|
|没有LITE_RUNTIME|0.02s|0.24s |2.45s  |0.02s|0.16s |1.57s  |
|加LITE_RUNTIME  |0.02s|0.19s |1.92s  |0.01s|0.13s |1.38s  |




###结论

* lite版的编译后二进制文件大大缩小。
* 编解码速度有一点提升，数据量越大越明显。
* 解码时会丢弃未知域，即TestMsg 解TestMsg2数据时， 域new_add_name = 4;会丢失
