'''
protobuf obj <--> dict obj
protobuf obj --> html inputs

protobuf obj --> html inputs ==> html ==> post form ==> dict obj --> protobuf obj
'''
#coding=utf-8
#from google.protobuf.descriptor import FieldDescriptor
from  google.protobuf import descriptor
import json

def message2HtmlInputs(message, parent_full_name='', repeaded_field=False, repeaded_index=0):
    ''' 把protobuf message类转成 一个html简单的<input> 标签
        args:
        message:要转换和message类
        parent_full_name： 该message所在message的名称，调用者可以不用关心该值
        repeaded_field： 该message是否是所在message的repeated域，调用者可以不用关心该值
        repeaded_index： 该message是所在message的repeated域的下标，调用者可以不用关心该值
    '''
    msg_str = ''
    for field, value in message.ListFields():
        if field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            msg_str += '<br></br><label>%s:</label><div><input type="hidden" name="%s|%s" value="1"/>\n'  %(field.full_name , parent_full_name, field.full_name)
            index = 0
            for element in value:
                msg_str += _field2HtmlInput(field, element, parent_full_name, True, index)
                index += 1
            msg_str += '</div>\n'
        else:
            msg_str +=  _field2HtmlInput(field, value, parent_full_name, repeaded_field, repeaded_index)
    msg_str += '\n'
    return msg_str


def _field2HtmlInput(field, value, parent_full_name, repeaded_field, repeaded_index):
    field_str = ''
    if repeaded_field:
        parent_full_name = "%s|%s_%d" %(parent_full_name ,field.full_name ,repeaded_index)
    else:
        parent_full_name = "%s|%s" %(parent_full_name ,field.full_name )
    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
        if repeaded_field:
            field_str = '<br></br><label>%s_%d:</label>\n' %(field.full_name , repeaded_index)
        else:
            field_str = '<br></br><label>%s:</label>\n' % field.full_name
        field_str += '<div>\n<input type="hidden" name="%s" value="1"/>%s\n</div>\n' %(parent_full_name,
                                                                                      message2HtmlInputs(value , parent_full_name, repeaded_field ,repeaded_index ) )
    else:
        if repeaded_field:
            field_str = '<label>%s_%d:</label>' % (field.name,repeaded_index)
        else:
            field_str = '<label>%s:</label>' % field.name
        field_str += '<input type="text" name="%s" value="%s"/>\n' %(parent_full_name,value )
    return field_str



def dict2Message(message_cls, dict_obj, parent_full_name='', repeaded_field=False, repeaded_index=0):
    '''
        把dict_obj 转成 message_cls的对象
        args:
        message_cls, dict_obj, parent_full_name='', repeaded_field=False, repeaded_index=0
        message_cls:要生成message的类或生成类
        dict_obj： post的字典对象
        parent_full_name： 该message所在message的名称，调用者可以不用关心该值
        repeaded_field： 该message是否是所在message的repeated域，调用者可以不用关心该值
        repeaded_index： 该message是所在message的repeated域的下标，调用者可以不用关心该值
    '''
    msg_obj = message_cls()
    for field in message_cls.DESCRIPTOR.fields:
        if field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            index = -1 #约定好repeated 有_index 后缀
            copy = field._default_constructor(msg_obj)
            while True:
                index += 1
                if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
                    repeated_field_cls = copy._message_descriptor._concrete_class 
                    field_val = _dict2Field(dict_obj, repeated_field_cls, field, parent_full_name, True, index)
                    if field_val is None:
                        break
                    copy.add().MergeFrom(field_val)
                else:
                    field_val = _dict2Field(dict_obj, None, field, parent_full_name, True, index)
                    if field_val is None:
                      break
                    copy.append(field_val)
            if index >= 0:
                msg_obj._fields[field] = copy
        else:
            if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:# Composite
                copy = field._default_constructor(msg_obj)
                field_cls = copy.__class__
                field_val = _dict2Field(dict_obj, field_cls, field, parent_full_name, repeaded_field, repeaded_index)
                if field_val != None:          
                    copy.MergeFrom(field_val)
                    msg_obj._fields[field] = copy
            else:
                field_val = _dict2Field(dict_obj, None, field, parent_full_name, repeaded_field, repeaded_index)
                if field_val != None:
                    setattr(msg_obj, field.name, field_val)
    return msg_obj
        

def _dict2Field(dict_obj, field_cls, field, parent_full_name, repeaded_field, repeaded_index):
    if repeaded_field:
        fieldname = "%s|%s_%d" %(parent_full_name, field.full_name, repeaded_index)
    else:
        fieldname = "%s|%s" %(parent_full_name, field.full_name)
    field_val = dict_obj.get(fieldname)
    if field_val is None:
        return None
    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
        return dict2Message(field_cls, dict_obj, fieldname , repeaded_field,repeaded_index )
    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_STRING:
        return str(field_val)
    elif field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_BOOL:
        return 1 if field_val else 0
    else:
        return int(field_val)



HTML_HEAD =  '''
<html lang="en">
<head>
<link rel="stylesheet" href="style.css" />
<title>pb_form</title>
<style type="text/css">
*{padding:0;margin:0;}	
div{border:solid 1px }
	
</style>
</head><body>
<form method="post" action=".">
'''
HTML_TAIL = '''
<input type="submit" value="submit" />
</form>
</body>
</html>
'''


def message2Dict(message):
    ''' 把message  转成  dict_obj'''
    msg_dict = {}
    for field, value in message.ListFields():
        if field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            msg_dict[field.name] = [ _getFieldValue(field, element) for element in value ]
        else:
            msg_dict[field.name] = _getFieldValue(field, value)
    return msg_dict


def _getFieldValue(field, value):
    '''不支持直接获取repeated 的值'''
    if field.cpp_type == descriptor.FieldDescriptor.CPPTYPE_MESSAGE:
        return message2Dict(value)
    else:
        return value


def dict2Json(dict_obj, encoding='UTF-8'):
    return json.dumps(dict_obj, encoding=encoding)


