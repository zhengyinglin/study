sublime Text 2 配置
===========================

---------------------------
###　　　　　　　　　 DATE: 2014-10-30
###　　　　　　　　　 E-mail:979762787@qq.com

===========================


##下载安装
官网：http://www.sublimetext.com

下载连接[sublime Text 2](http://www.sublimetext.com/2)

##手动安装包
个人还是偏向手动安装第三方包
通过菜单条打开包路径
Preference --> Browse Packages  
把第三方包放到该路径下面即可


##我的常用包与配置
代码静态检查：[SublimeLinter](https://github.com/SublimeLinter/SublimeLinter-for-ST2) 
代码提示： [SublimeCodeIntel](https://github.com/SublimeCodeIntel/SublimeCodeIntel)
生成MarkDown：[Markdown Preview](https://github.com/revolunet/sublimetext-markdown-preview)

修改配置文件的方法 Preference --> Packages Setting --> 选择你具体的包 --> Settings User

SublimeLinter 配置
```json
{

    "sublimelinter": "load-save",
    "sublimelinter_popup_errors_on_save": true
}
```

SublimeCodeIntel 配置
```json
{
    "codeintel_config": {
        "Python": {
            "env": {
                "PATH": "C:\\Python27"
            }
        }
    }
}
```

Markdown Preview 配置
```json
{
    "browser": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "enabled_parsers": ["markdown"],
    "enable_highlight": true
}
```

##sublime 执行命令
ctrl + shift + p 

  
Markdown 文件生成html文件
可以简单输入： mdp


