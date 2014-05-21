//coding=utf-8


#include<iostream>
#include<assert.h>
#include<algorithm>

#include <google/protobuf/message.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/unknown_field_set.h>

#include "example.pb.h"
/*
package myproto;
message EmptyMessage
{
}

message UsersSet
{
	 repeated uint32   uins = 1;
	 optional bytes   desc = 2;
}

message Item
{
    required  int32    id = 1;
    optional  int32    num = 2;
    optional  bytes    name = 3;
}

message BagInfo
{
	optional  uint32   create_time = 1;
}

message Bag
{
   repeated  Item  items = 1;
   optional  BagInfo   info =2;
}
*/


#ifdef _DEBUG
  #pragma comment(lib , "libprotobuf.lib")
#else
  #pragma comment(lib , "-libprotobuf.lib")
#endif


void test_Field()
{
    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
    myproto::Item  objItem;
    const ::google::protobuf::Descriptor* descriptor = objItem.GetDescriptor();
    const ::google::protobuf::Reflection* reflection = objItem.GetReflection();

    std::cout << descriptor->FindFieldByName("id") << "===" << descriptor->FindFieldByName("xxxid")<<std::endl;

    const ::google::protobuf::FieldDescriptor* field = descriptor->FindFieldByName("id");
    assert(field != NULL);
    assert( reflection->HasField(objItem, field) == false );
    objItem.set_id(1000);
    assert( reflection->HasField(objItem, field) == true );
    objItem.set_name("hahahah");
    objItem.set_num(88);
    objItem.PrintDebugString();
    std::cout<< objItem.ShortDebugString() << std::endl;
    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
}

void test_Field2()
{
    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
    myproto::Bag  objBag;
    const ::google::protobuf::Descriptor* descriptor = objBag.GetDescriptor();
    const ::google::protobuf::Reflection* reflection = objBag.GetReflection();

    const ::google::protobuf::FieldDescriptor* field = descriptor->FindFieldByName("info");
    assert(field != NULL);

    myproto::BagInfo* pInfo =  dynamic_cast<myproto::BagInfo*>( reflection->MutableMessage(&objBag, field) );
    assert(pInfo != NULL);

    {
        myproto::Item* pItem =  dynamic_cast<myproto::Item*>( reflection->MutableMessage(&objBag, field) );
        assert(pItem == NULL);
    }

    pInfo->set_create_time(1<<16);
    objBag.PrintDebugString();
    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
}

void test_Msg()
{
    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
    myproto::UsersSet  obj;
    std::cout << obj.GetCachedSize() << std::endl;//GetCachedSize  last call ByteSize cache value
    for(int i=0;i<100;i++)
    {
        obj.add_uins(i);
    }
    std::cout << obj.ByteSize() << std::endl;

    std::string str_output;
    if( obj.SerializeToString(&str_output) ) 
    {
        std::cout << "c++ string length is : " << str_output.length() << std::endl;
    }
    std::cout<<obj.GetCachedSize()<<std::endl;


    const int MAX_VALUE_LEN = 100;
    char static_char[MAX_VALUE_LEN];
    memset(static_char, 0, MAX_VALUE_LEN);
    if( obj.SerializeToArray(static_char, MAX_VALUE_LEN) ) 
    {
        std::cout << "c char array length is :" << obj.ByteSize() << std::endl;
    }
    else
    {
        std::cout << "SerializeToArray faile "<< std::endl;
    }

    myproto::Item  objItem;
    if(false == objItem.ParseFromString("") )
    {
        std::cout << "ParseFromString faile "<< std::endl;
    }

    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
}






class ProtobufReader
{
public:
    static void ReadMessage(const std::string& strMsg)
    {
        //using emtpy Message print all field
        myproto::EmptyMessage  objMessage;
        if(false == objMessage.ParseFromString(strMsg) )
        {
            std::cout << "EmptyMessage ParseFromString faile "<< std::endl;
            return ;
        }

        std::cout << "------------------EmptyMessage----------------------" << std::endl;
        objMessage.PrintDebugString();
        std::cout << "------------------EmptyMessage----------------------" << std::endl;

        
        std::cout << "------------------Message ----------------------" << std::endl;
        ParseUnknownFieldSet( objMessage.unknown_fields() );
        std::cout << "------------------Message ----------------------" << std::endl;
    }

    static void ParseUnknownFieldSet(const ::google::protobuf::UnknownFieldSet&  objFieldSet)
    {
        typedef ::google::protobuf::UnknownField  UKField;
        int field_count = objFieldSet.field_count();
        for(int i=0; i<field_count; i++)
        {
            const UKField&  objField = objFieldSet.field(i);
            std::cout << "type " << objField.type()  << "  number  " << objField.number() <<  std::endl ;
            switch(objField.type())
            {
            case UKField::TYPE_VARINT:
                std::cout << "[TYPE_VARINT] value " << objField.varint() <<  std::endl ; 
                break;
            case UKField::TYPE_FIXED32:
                std::cout << "[TYPE_FIXED32] value " << objField.fixed32() <<  std::endl ; 
                break;
            case UKField::TYPE_FIXED64:
                std::cout << "[TYPE_FIXED64] value " << objField.fixed64() <<  std::endl ; 
                break;
            case UKField::TYPE_LENGTH_DELIMITED:
                std::cout << "[TYPE_LENGTH_DELIMITED] value " << objField.length_delimited() <<  std::endl ; 
                break;
            case UKField::TYPE_GROUP:
                std::cout << "[TYPE_GROUP] value " << std::endl;
                ParseUnknownFieldSet( objField.group() );
                break;
            default:
                assert(false);
            }
        }
    }
};

void test_Msg2()
{
    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
    myproto::Item  objItem;
    objItem.set_id(1000);
    objItem.set_name("hahahah");
    objItem.set_num(88);
    objItem.PrintDebugString();
    std::string str_output;
    if(false == objItem.SerializeToString(&str_output) ) 
    {
        std::cout << "Item SerializeToString failed " << std::endl;
        return ;
    }
    objItem.clear_name();

    ProtobufReader::ReadMessage(str_output);

    myproto::UsersSet  obj;
    for(int i=0;i<10;i++)
    {
        obj.add_uins(i);
    }
    if(false == obj.SerializeToString(&str_output) ) 
    {
        std::cout << " SerializeToString faile"<< std::endl;
        return ;
    }

    ProtobufReader::ReadMessage(str_output);

    std::cout << "------------------" << __FUNCTION__ <<"----------------------" << std::endl;
}


void ProtobufLogHandler(google::protobuf::LogLevel level, const char* filename, int line, const std::string& message)
{
  static const char* level_names[] = { "LOGLEVEL_INFO", "LOGLEVEL_WARNING", "LOGLEVEL_ERROR", "LOGLEVEL_FATAL",  "LOGLEVEL_DFATAL"};

  printf("[libprotobuf %s %s:%d] %s\n", level_names[level], filename, line, message.c_str());
}


int main()
{
    //set exception print handler 
    google::protobuf::SetLogHandler(ProtobufLogHandler);

    test_Field();
    test_Field2();
    test_Msg();
    test_Msg2();
    return 0;
}