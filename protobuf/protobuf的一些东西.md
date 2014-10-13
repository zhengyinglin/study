protobuf其他东西
====================
###　　 Date:2014-9-2
###　　 EMail: 979762787@qq.com

===========================
 

###Base 128 Varints编码 （7位有效位数）
   对于8字节 第一位0 表示后面没有数字了 1表示后面还有数字
```Text
   数值1    ==》 00000001
                  0000001  --》1
  
   数值300  ==》 10101100 00000010 
                  0101100  0000010  --》 000101100 0000010  --》  300

   1个字节编码数值  0 -- 127      2^7
   2个字节编码数值  128 -- 16383  2^14
   3个字节编码数值                2^21
```
   也就是说 小于128的整数只需要1个字节存储，小于16383 需要2个字节。。。


###存储结构
   key-value , key-value ... 使用128编码

   key =  (field_number << 3) | wire_type
   wire_type 域的类型 3位表示（[见域类型表](#table)） 
   field_number  定义类型的域数值   
   
   由128编码可知道
   1个字节编码field_number范围：0 -- 15 , (2^4 - 1  类型占3位, 剩下4位, 共7位)
   2个字节编码field_number范围：16 -- 2047 ,  (2^11 - 1 )

<a name="table"/>
域类型表

|Type|     Meaning    |             Used For                                     |
|----|----------------|----------------------------------------------------------|
| 0  |     Varint     | int32, int64, uint32, uint64, sint32, sint64, bool, enum |
| 1  |     64-bit     | fixed64, sfixed64, double                                |
| 2  |Length-delimited| string, bytes, embedded messages, packed repeated fields |
| 3  |   Start group  | groups (deprecated)                                      |
| 4  |    End group   | groups (deprecated)                                      |
| 5  |    32-bit      | fixed32, sfixed32, float                                 |

###最小化存储空间

* 一个message里域数量
    * 最好在15个内（标签是1--15，那样标签只需一个字节空间即可）
    * 超过16个可以考虑分message
    * 存储整数数据尽量使用小数据，占空间少

* string、message（类型2） 需要额外一个长度字段表示有后面有多少数据
    * 对于0--127 长度需要 1个字节
    * 对于128--16383  长度需要 2个字节


###类型的兼容

  * int32, uint32, int64, uint64, and bool are all compatible
  * sint32 and sint64 are compatible 
  * string and bytes are compatible as long as the bytes are valid UTF-8.
  * fixed32 is compatible with sfixed32, and fixed64 with sfixed64.
  * optional is compatible with repeated. 

  也就是兼容的message字段类型可以互换，不会破坏message数据的结构。[具体看官方文档](https://developers.google.com/protocol-buffers/docs/proto#updating)

###数据的向前和向后兼容性
```Text
    protobuf data  
        old--- new
               +entry

        old--->new  新的字段entry 没有

        new--> old 忽略新的域，未能识别的域（unknown fields）没有被抛弃，新的域还是可以利用
```

###PB实现的一些优化技巧
    * 函数内联
    * 函数调用去虚拟化
```cpp
       //a qualified member access expression designed to avoid virtual dispatch.
       //Note that using the qualified name will disable dynamic dispatch, 
       //and that means that it will not be dispatched to the runtime type of the object, 
       //but to the type that you tell it to call.
       template <typename StaticType>
       inline void DoSthNoVirtual(StaticType*  value)
       {
            value->StaticType::DoSth();
       }
```
    * 预判条件(快速路径)

```cpp
    bool Msg::MergePartialFromCodedStream(::google::protobuf::io::CodedInputStream* input) {
      ::google::protobuf::uint32 tag;
      for (;;) {
        ::std::pair< ::google::protobuf::uint32, bool> p = input->ReadTagWithCutoff(127);
        tag = p.first;
        if (!p.second) goto handle_unusual;
        switch (::google::protobuf::internal::WireFormatLite::GetTagFieldNumber(tag)) {
          // optional int32 val = 1 [default = 99];
          case 1: {
            if (tag == 8) {
              DO_((::google::protobuf::internal::WireFormatLite::ReadPrimitive<
                       ::google::protobuf::int32, ::google::protobuf::internal::WireFormatLite::TYPE_INT32>(
                     input, &val_)));
              set_has_val();
            } else {
              goto handle_unusual;
            }
            if (input->ExpectTag(18)) goto parse_desc;
            break;
          }
          // required bytes desc = 2;
          case 2: {
            if (tag == 18) {
             parse_desc:
              DO_(::google::protobuf::internal::WireFormatLite::ReadBytes(
                    input, this->mutable_desc()));
            } else {
              goto handle_unusual;
            }
            if (input->ExpectTag(26)) goto parse_sub;
            break;
          }
          .....
```

