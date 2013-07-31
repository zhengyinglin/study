#coding=utf-8
#email:979762787@qq.com

sshrun 依赖 paramiko 库 ，基于 paramiko .SSHClient 实现简单跨机运行shell命令，和拷贝更新文件
其配置风格模仿Fabric库（功能很强大）


========================安装的运行脚本==============================
安装  
python setup.py build
python setup.py install


见sshrun/demo/sshfile.py    

运行任务

sshrun getfile        ( 默认 读取 sshfile.py )
或者  sshrun -f sshfile.py   getfile




=======================paramiko .SSHClient  封装===============
class SSH2(object):
     def getfile(self, remotepath , localpath , callback = None , ip_suffix=False):
         拷贝远程文件remotepath  到本地目录localpath 
         callback 参数是sftp.get 函数参数，拷贝过程的回调（有2个参数 size  filesize）  可以不填
         ip_suffix ： True 文件后面添加ip地址 ， Flase 文件后面不添加任何东西

     def putfile(self, localpath , remotepath , callback = None):
         本地文件localpath  拷贝远程目录 remotepath  
         callback 参数 getfile。callback 一样
         
     def exec_command(self, cmd , timeout=None):
         远程执行shell命令

     def local_command(self,cmd):
         执行本地shell命令



======================目标机器配置：
#更新定义配置
SSH2Conf.update(

    #自己的配置
    {
        'test':{ 
            'hosts':[ ('user@172.25.40.53:36000' , 'yourpasswd' )  ],
        } ,
        'other_task':{ 
            'hosts':[ "ip_list_file" ],
            'default_user':'user',
            'default_port':36000,
            'default_passwd':'yourpasswd'
        } ,
        #添加其他任务目标机器host
    }

)

     'hosts' 对应的字段 可以是下面3种格式： ip，ip文件列表 , (user@ip:port , passwd)



=====================编写任务（拷贝远程文件）：

@runhosts("test")
def getfile(ssh):
    ssh.getfile('/tmp/xxx.xml' , '.')

上面相当于  cp  SSH2Conf["test"]["hosts"]:/tmp/xxx.xml  .


====================运行任务
sshrun getfile  



