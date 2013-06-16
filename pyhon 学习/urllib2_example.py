#coding=utf-8
'''
下载 画旅途 某个主题的所有图片
'''

import urllib2
import re
import time

#设置代理
#proxy_handler = urllib2.ProxyHandler({"http" : 'http://xxx.xxxx.xxx/xxx'})
#opener = urllib2.build_opener(proxy_handler)
#urllib2.install_opener(opener)

headers = {
    'User-Agent':'Magic Browser',
}

def get_photo(url , timeout=10):
    req = urllib2.Request(url=url , headers=headers)
    string = urllib2.urlopen(req , timeout = timeout).read()
    #图片url
    re_url = "photo='http[^\s]*\.jpg'"

    for path in re.findall(re_url , string):
        path = path[7:-1]
        filename = path.rpartition('/')[2]
        print path , '\n' , 'start down ...'
        start_t = time.time()
        req = urllib2.Request(path, headers=headers)
        data = urllib2.urlopen(req).read()
        with open(filename , 'wb') as f:
            f.write(data)
        proc_t = ( time.time() - start_t ) * 1000 # ms 
        print 'down done  size = %.3f KB  time %.0fms' % ( len(data)/1024.0 , proc_t )

if __name__ == '__main__':
    #画旅途 每个主题url
    url = 'http://rugui.hualvtu.com/10120719210000001687'
    get_photo( url )

