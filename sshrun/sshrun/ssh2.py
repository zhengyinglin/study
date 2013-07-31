#coding=utf-8
"""paramiko  SSHClient 的简单封装
    1、远程执行命令 ssh.exec_command  
    2、获取远程文件 ssh.getfile 
    3、更新远程文件 ssh.putfile """

import os
import logging
import paramiko
import subprocess

__all__ = [ 'SSH2' , 'runhosts' , 'log' , 'SSH2Conf' ]

#paramiko log
paramiko.util.log_to_file('paramiko.log')

#own log
def _init_mylog(loglevel = logging.DEBUG):
    logger = logging.getLogger("sshrunlog")
    logger.setLevel(loglevel)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s  %(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger , handler

log , _loghandler = _init_mylog()

def log2file(logfile , filemode='a' , loglevel = logging.DEBUG , formatter = None):
    global  _loghandler , log 
    log.setLevel(loglevel)
    stream = open(logfile , filemode)
    handler = logging.StreamHandler(stream)
    if formatter is None:
        formatter = logging.Formatter('%(asctime)s  %(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.removeHandler(_loghandler)
    _loghandler = handler
    
    



class SSH2(object):
    def __init__(self):
        self.ssh = None
        self.sftp = None
        self.conndesc = ""

    def connect(self, ip , port = 36000 , username = None, passwd = None):
        if self.ssh:
            self.ssh.close()
            self.ssh = None
            self.sftp = None
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try: 
            self.ssh.connect(ip , port , username, passwd , timeout=5 )#password
        except paramiko.BadAuthenticationType , e:
            log.warning('use password failed  try keyboard-interactive')
            #see SSHClient::connect
            from paramiko.resource import ResourceManager
            t = self.ssh._transport = paramiko.Transport((ip, port))
            t.start_client()
            ResourceManager.register(self.ssh, t)
            def handler(title, instructions, prompts):
               return [ passwd ]
            t.auth_interactive(username,handler)
        self.conndesc = "%s@%s:%d" % (username , ip , port )
        log.debug('==========>>>>>> %s connect  =====>>>>>' , self.conndesc )

    def close(self):
        if self.ssh:
            self.ssh.close()
        self.ssh = None
        self.sftp = None
        log.debug('==========>>>>>> %s close  <<<<<<<<==========\n\n\n' , self.conndesc )

    def getfile(self, remotepath , localpath , callback = None , ip_suffix=False):
        log.debug("---get  %s %s" , self.conndesc , remotepath)
        if os.path.isdir(localpath):
            localpath = os.path.join(localpath , os.path.basename(remotepath) )
        if ip_suffix:
            localpath += '_' + self.conndesc.partition('@')[2].partition(':')[0] # ip string
        if self.sftp is None:
            self.sftp = self.ssh.open_sftp()
        fstat = self.sftp.stat(remotepath)
        self.sftp.get(remotepath, localpath , callback=callback)
        os.chmod(localpath ,  fstat.st_mode )
        #QQQ  should  add md5 check  ??? 

    def putfile(self, localpath , remotepath , callback = None):
        if self.sftp is None:
            self.sftp = self.ssh.open_sftp()
        #是否是目录
        outstr = self._exec_command("test -d %s && echo yes || echo no" % remotepath)[0]
        if "yes" in outstr:
            remotepath = os.path.join(remotepath , os.path.basename(localpath) )
        log.debug("---put  %s %s" , self.conndesc , remotepath)
        fstat = os.stat(localpath)
        self.sftp.put(localpath , remotepath, callback=callback)
        self.sftp.chmod(remotepath ,  fstat.st_mode )
        #QQQ  should  add md5 check  ??? 

    def _exec_command(self, cmd , timeout=None):
        stdin , stdout , stderr = self.ssh.exec_command(cmd , timeout=timeout)
        return stdout.read() , stderr.read()

    def exec_command(self, cmd , timeout=None):
        log.debug('exec_command:[ %s ]\n' , cmd)
        out , err = self._exec_command(cmd , timeout)
        if out:
            log.debug('>>>>> %s' , out)
        if err:
            log.error( err )

    def local_command(self,cmd):
        return subprocess.check_output(cmd , shell=True)



def getssh2_conn(host, default_passwd=None, default_user=None , default_port = None ):
    '''通过host 和密码获取已经连接好的SSH2对象
        host = [user@]ip[:port]   or ([user@]ip[:port] , passwd)   
    '''
    if isinstance(host, tuple) or  isinstance(host, list):
        pw = host[1] if len(host) > 1 else default_passwd
        return getssh2_conn(host[0], pw, default_user, default_port)
    user, seq , host = host.rpartition('@')
    if not user: 
        user = default_user 
    ip , seq , port = host.partition(':')
    port =  int(port) if port else int(default_port)
    ssh = SSH2()
    ssh.connect(ip , port = port , username = user, passwd = default_passwd)
    return ssh

def genssh2(task):
    '''生成器：生成一组ssh2 对象'''
    d_user = task.get('default_user' , None)
    d_port = task.get('default_port' , None)
    d_passwd = task.get('default_passwd' , None)
    for host in task["hosts"]:
        if isinstance(host, basestring) and os.path.isfile(host): #支持文件ip列表
            raw_ips = ( line.strip() for line in open(host) )
            ips = ( ip for ip in raw_ips if ip and ip[0] not in ";#" )
            for ip in ips:
                yield getssh2_conn(ip , d_passwd , d_user , d_port)
        else:
            yield getssh2_conn(host , d_passwd , d_user , d_port)


def runhosts(taskname):
    '''装饰器：通过获取SSH2Conf的目标地址，返回SSH2对象 迭代运行目标函数'''
    def deco(func):
        def  _deco(*args, **kwargs):
            global SSH2Conf
            task = SSH2Conf[taskname]  #SSH2Conf 来自 外部文件 sshfile.py 
            for ssh in genssh2(task):
                func(ssh, *args, **kwargs)
                #QQQ close here ???
                ssh.close()
        return _deco
    return deco




#配置文件，新模块要更新他的值  即 SSH2Conf.update( myconf )
SSH2Conf = {
    #'ld2_test':{ 
    #   'hosts':[ '172.25.40.53' ],
    #    'default_user':'user',
    #    'default_port':36000,
    #    'default_passwd':'yourpasswd'
    #} ,
    #添加其他任务目标机器host
}
