#coding=utf-8
"""
email: 979762787@qq.com


简单把excel 表（2维表） 转成xml
example.xls 中的工作簿——物品表，有如下内容
id	name	sell	price	desc
2001	耐力丸	1	100	增加20点耐力值。
2002	中耐力丸	1	200	增加50点耐力值。
2003	大耐力丸	1	400	增加110点耐力值。

XLS2XML().genXml( u"example.xls" , #excel文件
                  u"物品表" ,  #工作簿名称
                  u"props.xml" , #要生成xml的文件名
                  u"Props" ,  # xml根元素名称
                  u'Prop')   #xml子元素名称
会生成xml 文件 props.xml
<Props>
   <Prop id="2001" name="耐力丸" sell="1" price="100" desc="增加20点耐力值。"/>
   <Prop id="2002" name="中耐力丸" sell="1" price="200" desc="增加50点耐力值。"/>
   <Prop id="2003" name="大耐力丸" sell="1" price="400" desc="增加110点耐力值。"/>
</Props>
"""

import sys
reload(sys) 
sys.setdefaultencoding('utf-8') 
import xlrd
#https://pypi.python.org/pypi/xlrd/0.9.2

class XLS2XML(object):
    
    def __init__(self , encoding='utf-8'):
        self._xml = []
        self._encoding = encoding

    @classmethod
    def val2str(cls , val):
        if  isinstance(val,basestring):
            return val.strip()
        else:
            return str(int(val))
        
    def _getXmlHead(self , root):
        self._xml.append( u'<?xml version="1.0" encoding="%s" ?>\n' % self._encoding )
        self._xml.append( u'<%s>\n' % root )

    def _genXmlTail(self, root):
        self._xml.append( u'</%s>\n' % root)

    def _genXMLBody(self, fname , sheet_name , element):
        #获取工作簿
        bk = xlrd.open_workbook(fname)
        sh = bk.sheet_by_name(sheet_name)
        nrows , ncols = sh.nrows , sh.ncols
        #从第3行开始读 字段名称
        member = [ XLS2XML.val2str(_name) for _name in sh.row_values(2) ]
        for row in range(3, nrows):
            attrs = ''
            row_data = sh.row_values(row)
            assert len(row_data) == len(member) , 'field not equation'
            for i in xrange(len(member)):
                attrs += '%s="%s" ' %(member[i] ,  XLS2XML.val2str(row_data[i]) )
            self._xml.append('\t<%s %s/>\n' %(element , attrs) )

    def genXml(self , fname , sheet_name , xml_name , root , child):
        self._xml = []
        self._getXmlHead(root)
        self._genXMLBody(fname , sheet_name, child)
        self._genXmlTail(root)
        if self._encoding not in ('utf-8' , 'UTF-8'):
            self._xml = [ line.encode(self._encoding)  for line in self._xml ]
            #self._xml = [ line.decode('utf-8').encode(self._encoding)  for line in self._xml ]
        with open(xml_name , "w")  as fp:
            fp.writelines(self._xml)               


if __name__ == "__main__":
    try:
        XLS2XML().genXml( u"example.xls" , u"物品表" , u"props.xml" , u"Props" , u'Prop')
    except Exception ,e :
        print e
        import traceback
        print traceback.format_exc()   
    raw_input('to be continue..')


