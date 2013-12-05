#! /usr/bin/env python
#coding=utf-8
'''
@file: ld2_deploy_tool.py  乐斗2配置工具
      参考jameyli 的 tnt_comm_deploy_tool.py (TNT统一配置工具)

@brief:  
 主要功能：
     1 配置定义生成，根据excel 自动生成配置的PB定义
     2 配置数据导入，将配置数据生成PB的二进制格式

 说明:
   1 excel 的前五行用于结构定义, 其余则为数据，按第一行区分, 分别解释：
       required 必有属性
       optional 可选属性
           第二行: 属性类型
           第三行：属性名
           第四行：数值——如果是基本类型可以忽略该选项，否则填充该类型在excel包含（占用）的列数
           第五行：注释
           数据行：属性值
       repeated 表明下一个属性是repeated,即数组
           第二行: 属性类型
           第三行：属性名
           第四行：数值——格式是2,4（中间用逗号分开，非中文逗号）: 第一个数2表示最多repeated的个数，第二个数是每个"属性名"类型在excel包含（占用）的列数
           第五行：注释
           数据行：实际的重复次数

########====================修改历史==================################################
 2012-3-22 ：写入数据文件时如果是空（没有填） int or uint 默认0  string or bytes 默认 

##依赖外部库
    xlrd
    protobuf

#运行例子
    python ld2_deploy_tool.py exmple.xls  Task 
    会产生2个文件
        ld2_task.proto (proto 文件 里面有 Task  TaskArray  等message)
        ld2_task.data (xls 里面配置数据 二进制格式 TaskArray().ParseFromString(...) )

'''


#设置编码格式

import xlrd # for read excel
import sys
import os
import logging

# ====================================全局定义=================================
gFilePrefix = 'ld2_'  #生成文件名的前缀
gPackageName = 'LD2'  #包名
TAP_BLANK_NUM = 4  # TAP的空格数



def set_repeatedfield(message, field_type, field_name, datas):
    for val in datas:
        if field_type in ('int32', 'uint32','int64', 'uint64'):
            getattr(message, field_name).append(int_val(val))
        elif  field_type in ('string', 'bytes'):
            getattr(message, field_name).append(str_val(val))
        else:
            raise Exception('invalide field_type %s err..', field_type)

def set_baseField(message, field_type, field_name, val):
    if field_type in ('int32', 'uint32'):
        setattr(message, field_name, int_val(val))
    elif  field_type in ('string', 'bytes'):
        setattr(message, field_name, str_val(val))
    else:
        raise Exception('invalide field_type %s err..', field_type)
    

def str_val(val):
    if val == None:
        return ""
    if  isinstance(val, unicode):
        return val.strip().encode('utf-8')
    if isinstance(val, str):
        return val.strip()
    return str(int(val))

def int_val(val):
    if val == None:
        return 0
    if  isinstance(val, basestring) and val.strip() == "":
        return 0
    return int(val)

FileHeadFMT  = '''/**
* @file:   %s.proto
* @author: ghostzheng
* @brief:  这个文件是通过工具自动生成的，建议不要手动修改
**/
'''

class SheetInterpreter(object):
    '''通过excel配置生成配置的protobuf定义文件和配置的配置的二进制数据'''
    def __init__(self, xls_file_path, sheet_name):
        workbook = xlrd.open_workbook(xls_file_path)
        self._sheet_name = sheet_name
        self._sheet = workbook.sheet_by_name(sheet_name)
        print sheet_name , ' : ' , self._sheet.nrows, ' X ' , self._sheet.ncols
        # 将所有的输出先写到一个list， 最后统一写到文件
        self._output = []
        # 排版缩进空格数
        self._indentation = 0
        # 保存自定义有结构的名字
        self._struct_name_list = []
        self.file_name = gFilePrefix.lower() + sheet_name.lower()
        
    def interpreter_and_parser(self, show = True):
        self._interpreter()
        self._data_parser(show)

    def _interpreter(self) :
        logging.info("begin Interpreter, row_count = %d, col_count = %d", self._sheet.nrows, self._sheet.ncols)
        self._layout_file_header()
        self._output.append('package %s;\n' % gPackageName )
        self._define_new_message(self._sheet_name , 0  , self._sheet.ncols)
        self._layout_array()
        self._write_proto2file(self._output , self.file_name + '.proto')
    
    def _layout_file_header(self) :
        """生成PB文件的描述信息"""
        self._output.append(FileHeadFMT % self.file_name )

    def _layout_message_head(self, msg_name) :
        """生成结构头"""
        indentation = ' ' * self._indentation
        self._output.append( '\n%smessage %s\n%s{\n' %(indentation, msg_name, indentation ) )

    def _layout_message_tail(self) :
        """生成结构尾"""
        self._output.append(" "*self._indentation + "}\n\n")

    def _layout_comment(self, comment) :
        '''注释'''
        indentation = ' ' * self._indentation
        if comment.strip() != "":
            self._output.append( "%s/* %s */\n" %(indentation, comment ) )
        
    def _inc_indentation(self) :
        """增加缩进"""
        self._indentation += TAP_BLANK_NUM

    def _dec_indentation(self) :
        """减少缩进"""
        self._indentation -= TAP_BLANK_NUM

    def _is_basetype(self, field_type):
        '''是否是基本类型'''
        return field_type in ( 'int32', 'uint32', 'string', 'bytes' )
    
    def _has_define_message(self, message_type):
        '''该类型是否已经定义'''
        return  message_type in self._struct_name_list 

    def _define_new_message(self, message_name, start_col, end_col):
        '''定义新的类型结构  参数：消息名称 、 所在列的范围[start_col , end_col) '''
        if self._has_define_message(message_name)  or self._is_basetype(message_name):
            return
        logging.info("%s|[%d,%d)", message_name, start_col, end_col)
        self._struct_name_list.append(message_name)
        self._layout_message_head(message_name)
        self._inc_indentation()
        self._gen_message_fields(start_col , end_col)
        self._dec_indentation()
        self._layout_message_tail()
        
    def _gen_message_fields(self, start_col, end_col) :
        '''生成message的域  参数:message所在列的范围[start_col , end_col) '''
        logging.info("col[%d , %d)", start_col, end_col)
        cur_col = start_col
        field_index = 0 #域下标
        while cur_col < end_col:
            field_index += 1
            col_data = self._sheet.col_values(cur_col) #取前面5个
            field_rule = str_val(col_data[0])
            field_type = str_val(col_data[1])
            field_name = str_val(col_data[2])
            #col_data[3] for repeated
            field_comment = str_val(col_data[4])

            repeated_field_num = 0
            repeated_num = 1 #最少一个
            if field_rule == 'repeated' :
                temp = str_val(col_data[3])
                num = temp.split(',')
                assert len(num) == 2
                repeated_num = int(num[0])
                repeated_field_num = int(num[1])
            elif not self._is_basetype(field_type):
                repeated_field_num = int_val( col_data[3] )
                
            if not self._has_define_message(field_type):
                self._define_new_message(field_type , cur_col+1, cur_col + repeated_field_num + 1)
            
            self._layout_comment(field_comment)
            self._output.append(' '*self._indentation + '%s %s %s = %d;\n' % (field_rule, field_type, field_name, field_index)  )
            cur_col += repeated_num * repeated_field_num + 1
            logging.info("%s|%s|%s|%d|%s",field_rule, field_type, field_name,field_index, field_comment)

    def _layout_array(self) :
        """输出数组定义"""
        self._output.append("message " + self._sheet_name + "Array \n{\n")
        self._output.append("    repeated " + self._sheet_name + " items = 1;\n}\n")

    def _write_proto2file(self, datas, filename) :
        """输出到文件"""
        with open(filename, "w") as fp:
            fp.writelines(datas)

    def _write_data2file(self, data_str, filename) :
        """输出到文件"""
        pb_file = open(filename, "wb")#二进制格式
        pb_file.write(data_str)
        pb_file.close()

    def _data_parser(self, if_print = True):
        '''把配置的数据转成protobuf类型的二进制文件'''
        logging.info("begin DataParser, row_count = %d, col_count = %d", self._sheet.nrows, self._sheet.ncols)
        os.system('protoc --python_out=.  ' + self.file_name + '.proto'  )
        module = self.file_name +  '_pb2'
        logging.info("gen python Proto[%s]", module)
        item_array = None
        exec('from '+ module + ' import *')
        exec('item_array = ' + sheet_name + 'Array()')
        for cur_row in range(5, self._sheet.nrows):
            item = item_array.items.add()
            row_data = self._sheet.row_values(cur_row)
            self._parse_message(item ,row_data, 0, self._sheet.ncols)
        data_file = self.file_name +  '.data'
        self._write_data2file(item_array.SerializeToString() , data_file)
        if if_print:
            tasks = None
            exec('tasks = ' + sheet_name + 'Array()')
            tasks.ParseFromString(open(data_file, 'rb').read())
            print tasks

            
    def _parse_message(self, message, row_data, start_col, end_col):
        '''转换区域内的消息'''
        logging.info("%s|col[%d , %d)", message.__class__.__name__ ,start_col , end_col)
        cur_col = start_col
        while cur_col < end_col:
            col_data = self._sheet.col_values(cur_col)[:4] #取前面4个
            field_rule = str_val(col_data[0])
            field_type = str_val(col_data[1])
            field_name = str_val(col_data[2])
            #col_data[3] for repeated
            repeated_field_num = 0
            repeated_num = 1 #最少是1
            if field_rule == 'repeated' :
                num = str_val(col_data[3]).split(',')
                assert len(num) == 2
                repeated_num = int(num[0])
                repeated_field_num = int(num[1])
                actual_repeated_num = int_val(row_data[cur_col])
                assert actual_repeated_num <= repeated_num
                if  self._is_basetype(field_type):
                    set_repeatedfield(message , field_type , field_name , 
                                                 row_data[cur_col+1:cur_col + actual_repeated_num*repeated_field_num+ 1])
                else:
                    cur_start_col = cur_col+1
                    for i in xrange(actual_repeated_num):
                        repeated_msg = getattr(message, field_name).add()
                        self._parse_message(repeated_msg , row_data , cur_start_col, cur_start_col + repeated_field_num )
                        cur_start_col += repeated_field_num
            else:
                if  self._is_basetype(field_type):
                    set_baseField(message , field_type , field_name , row_data[cur_col] )
                else:
                    repeated_field_num = int_val(col_data[3])
                    self._parse_message( getattr(message, field_name), row_data ,
                                       cur_col+1, cur_col + repeated_num * repeated_field_num+ 1)                  
            cur_col += repeated_num * repeated_field_num + 1


if __name__ == '__main__' :
    if len(sys.argv) < 3 :
        print "Usage: %s  xls_file  sheet_name" %(sys.argv[0])
        sys.exit(-1)
    logging.basicConfig(level = logging.INFO)
    xls_file, sheet_name =  sys.argv[1:3]
    try :
        SheetInterpreter(xls_file, sheet_name).interpreter_and_parser()
    except Exception, e :
        logging.exception("InterpreterAndDataParser Failed!!! , exception %s" , e)
    else:
        print "InterpreterAndDataParser Success!!!"
    
