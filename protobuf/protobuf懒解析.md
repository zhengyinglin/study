protobuf 懒解析
====================
###　　 Date:2014-9-2
###　　 EMail: 979762787@qq.com

===========================
参考[protobuf-2.4.1懒解析补丁](http://download.csdn.net/detail/gongyiling3468/4609851)

<font color=red>
** 对于目前懒解析，pb的反射功能 不能用 **
</font>

##对message 添加lazy 选项

```proto
message SubMsg
{
    optional int32   id   = 1;
    optional bytes   name = 2; 
}
message MyMsg
{ 
    optional uint32   id = 1;
    optional SubMsg   msg = 2 [lazy=true];
}
```


##原理

对于MyMsg, 如果很少使用（访问）msg 域的话，可以添加lazy=true，在解析MyMsg对象时，不去解析其具体值，只保留其原始数据，等到访问时在解析（延迟解析）



##实现基本原理
对于 lazy=true 的message 

在类代码里 除了定义  SubMsg *msg_; 
同时也添加 std::string  msg_content_; 存储该msg的序列化字符串

在获取该字段时
```cpp
    if(!msg_content_.empty())
    {
       msg_->ParsePartialFromString(msg_content_);
       msg_content_.clear();
    }
```
在保存该字段时
```cpp
    if(!msg_content_.empty())
    {
       ::google::protobuf::internal::WireFormatLite::WriteBytes(number, msg_content_, output);
    }
    else
    {
        ::google::protobuf::internal::WireFormatLite::WriteMessageMaybeToArray(number, this->msg(), output);
    }
```


##新增函数
```cpp
    //判断是否已经解析了该msg
    inline bool is_$name$_parsed() const
    {
        return $name$_content_.empty();
    }

    //解析该msg的值
    inline void lazy_parse_$name$()
    {
        if (!is_$name$_parsed())
        {
            if ($name$_ == NULL) $name$_ = new $type$;
            $name$_->ParsePartialFromString($name$_content_);
            $name$_content_.clear();
        }
    }
```

##性能测试
100 W 次测试  数据大小 1469 字节

|版本     |ParseFromString|ParseFromString one obj|ParseFromArray|ParseFromArray one obj|SerializeToString|SerializeToString one string|SerializeToArray|
|---------|---------------|-----------------------|--------------|----------------------|-----------------|----------------------------|----------------|
|2.6.0    |   15480 MS    |       6180 MS         |   15610 MS   |      6200 MS         |    3120 MS      |         2860 MS            |    2480 MS     |
|2.6.0lazy|   11730 MS    |       4890 MS         |   12050 MS   |      4770 MS         |    2240 MS      |         1980 MS            |    1840 MS     | 
 
 
##补丁下载
[protobuf-2.6.0-lazy.patch](/protobuf-2.6.0-lazy.patch)

