---
title: Zabbix配置动作执行远程命令和发送邮件
date: 2019-03-15 19:31:09
tags: zabbix
catagorize: zabbix
---
当有事件发生，我们可以根据事件来执行相应的动作，根据事件来源可以分为触发器动作，自动发现动作，自动注册动作，内部事件动作，自动发现动作在之前的自动发现那里讲过了，这里介绍一下触发器动作，当触发器事件达到执行动作的必要条件，会执行相应的动作
### 1.配置邮件告警动作
首先创建一个触发器动作，触发报警会发送邮件
![](https://s1.51cto.com/images/blog/201903/15/bec77ec964ee1ca8ea33702d021693f1.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
定义动作触发条件
![](https://s1.51cto.com/images/blog/201903/15/4d236b3bea064d542570f85925167534.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
定义动作执行的操作，这里是执行发送消息的操作，步骤1-5表示会发送5次消息，默认每次的间隔是30分钟
![](https://s1.51cto.com/images/blog/201903/15/ebf1dba4c3c83b09a91104432c49e4b0.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
这里我们定义了1-5步执行的操作，就是每隔30分钟，将消息通过‘zabbix_send.py’这个脚本发送给Admin用户
![](https://s1.51cto.com/images/blog/201903/15/118e46c361fbfcde675ae4b43979a52e.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
如果问题两个小时之内没有确认，则会将在两个小时之后每隔十五分钟一次通知zabbix管理组，共发送两次消息
![](https://s1.51cto.com/images/blog/201903/15/95f84e87e22bb88669eb2317d4719d08.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
这里看到两个操作的步骤五重叠了，这里较短的自定义步骤持续时间为10分钟的会覆盖较长的步骤持续时间，也就是说第二个操作的5步骤会覆盖第一个操作的5步骤
![](https://s1.51cto.com/images/blog/201903/15/bd95689932ce806d74057992f95abc1d.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
定义恢复操作，问题解决之后会发送消息给Admin用户
![](https://s1.51cto.com/images/blog/201903/15/e3a46f7fa771a7c6f2082d7a9d43a51f.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
定义更新操作，当其他用户更新问题时收到通知，比如问题被关闭，或者问题严重程度发生变化
![](https://s1.51cto.com/images/blog/201903/15/b6ecc7729efe9c916e004b850305f005.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
到这里动作部分就完成了，如果要让其成功发送邮件，还需要配置用户和报警媒介
#### 配置用户
![](https://s1.51cto.com/images/blog/201903/15/c329db7b54acf164bd8346f4cdbdbc31.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
配置用户报警媒介
![](https://s1.51cto.com/images/blog/201903/15/5a404ff44f5384a66c9905b0b39234c2.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
配置用户的收件人等信息
![](https://s1.51cto.com/images/blog/201903/15/6b8bf3170c1b722346cf3df3379b8630.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 创建报警媒介类型
![](https://s1.51cto.com/images/blog/201903/15/5f54c13a0eaa44f20e76086ba8d4aae2.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
配置报警媒介类型，传入的三个参数分别为收件人，邮件主题，邮件内容
![](https://s1.51cto.com/images/blog/201903/15/51d32240010ff362964a98b2eabebd8d.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
zabbix邮件报警的web界面配置完成了，还需要修改zabbix_server的配置文件，来支持使用脚本
vim /etc/zabbix/zabbix_server.conf
`AlertScriptsPath=/usr/lib/zabbix/alertscripts`
修改完成后重启zabbix-server
在/usr/lib/zabbix/alertscripts目录下添加要使用的报警脚本
并给邮件授予执行权限
`chmod +x zabbix_send.py`
创建一个graph目录，并授予权限
`mkdir graph chmod 777 -R graph`
![](https://s1.51cto.com/images/blog/201903/15/5f042282646447e948b7d0b616f78199.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
 
邮件内容及详细注释如下：
```python
#!/usr/bin/python
#coding=utf-8
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib,sys,os,time,re,requests
from smtplib import SMTP

user='Admin'    #定义zabbix用户名
password='zabbix'    #定义zabbix用户密码
graph_path='/usr/lib/zabbix/alertscripts/graph'   #定义图片存储路径
graph_url='http://192.168.179.132/chart.php'     #定义图表的url
#api_url ="http://10.127.0.119/api_jsonrpc.php"    #定义api的url
#header = {"Content-Type":"application/json" }     #定义api的headers
loginurl="http://192.168.179.132/index.php"          #定义登录的url
host='192.168.179.132'
to_email=sys.argv[1]    #传入的第一个参数为收件人邮箱
subject=sys.argv[2]  #传入的第二个参数为邮件主题   
subject=subject.decode('utf-8')
smtp_host = 'smtp.163.com'  #定义smtp主机地址
from_email = 'wanger@163.com'     #定义发件人地址
mail_pass = 'asd1234'       #发件人邮箱校验码


def get_itemid():
    #获取报警的itemid
    itemid=re.search(r'ITEM ID:(\d+)',sys.argv[3]).group(1)
    return itemid

def get_graph(itemid):
    #获取报警的图表并保存
    session=requests.Session()   #创建一个session会话
    try:
        loginheaders={            
        "Host":host,            
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
        #定义请求消息头
        
        payload = {            
        "name":user,
        "password":password,  
        "autologin":"1",            
        "enter":"Sign in",
        }
        #定义传入的data
        login=session.post(url=loginurl,headers=loginheaders,data=payload)
        #进行登录
        graph_params={
            "from" :"now-10m",
	        "to" : "now",           
            "itemids" : itemid,                       
            "width" : "400",
        }
        #定义获取图片的参数
        graph_req=session.get(url=graph_url,params=graph_params)
        #发送get请求获取图片数据
        time_tag=time.strftime("%Y%m%d%H%M%S", time.localtime())
        graph_name='baojing_'+time_tag+'.png'
        #用报警时间来作为图片名进行保存
        graph_name = os.path.join(graph_path, graph_name)
        #使用绝对路径保存图片
        with open(graph_name,'wb') as f:
            f.write(graph_req.content)
            #将获取到的图片数据写入到文件中去
        return graph_name
    
    except Exception as e:        
        print e        
        return False
def text_to_html(text):
    #将邮件内容text字段转换成HTML格式
    d=text.splitlines()   
    #将邮件内容以每行作为一个列表元素存储在列表中
    html_text=''
    for i in d:
        i='' + i + '<br>'
        html_text+=i + '\n'
    #为列表的每个元素后加上html的换行标签
    return html_text

def send_mail(graph_name):
    #将html和图片封装成邮件进行发送
    msg = MIMEMultipart('related')  #创建内嵌资源的实例

    with open(graph_name,'rb') as f:
        #读取图片文件
        graph=MIMEImage(f.read())  #读取图片赋值一个图片对象
    graph.add_header('Content-ID','imgid1')  #为图片对象添加标题字段和值
    text=text_to_html(sys.argv[3])
    html="""
    <html> 
      <body>
      %s  <br><img src="cid:imgid1">
      </body>
    </html>
    """ % text
    html=MIMEText(html,'html','utf-8')  #创建HTML格式的邮件体
    msg.attach(html)   #使用attach方法将HTML添加到msg实例中
    msg.attach(graph)  #使用attach方法将图片添加到msg实例中
    msg['Subject'] = subject
    msg['From'] = from_email
    try:
        server=SMTP(smtp_host,"25")   #创建一个smtp对象
        server.starttls()    #启用安全传输模式
        server.login(from_email,mail_pass)  #邮箱账号登录
        server.sendmail(from_email,to_email,msg.as_string())  #发送邮件  
        server.quit()   #断开smtp连接
    except smtplib.SMTPException as a:
        print a

def run():
    itemid=get_itemid()
    graph_name=get_graph(itemid)
    send_mail(graph_name)

if __name__ =='__main__':
    run()
```
### 2.配置执行远程命令的动作
当触发器达到阈值报警时，我们可以根据相关的报警来执行相关的命令使故障达到自我恢复的效果
这里我举一个ssh端口关闭并执行重启ssh的例子
#### 在系统上配置
在zabbix客户端配置文件中取消注释下面语句，以支持zabbix客户端执行远程命令
vim /etc/zabbix/zabbix_agentd.conf
EnableRemoteCommands=1
zabbix执行远程命令使用的是zabbix用户，确保'zabbix'用户具有已配置命令的执行权限。
vim /etc/sudoers
Defaults    !requiretty   #不需要提示终端登录 zabbix  ALL=(ALL)     NOPASSWD: ALL   ＃允许'zabbix'用户在没有密码的情况下运行所有命令。
配置完成后，使用zabbix-get测试是否可以运行远程命令，如果返回数据，则表示远程命令可用
zabbix_get -s 192.168.179.132 -k "system.run[sudo df -h]"
![](https://s1.51cto.com/images/blog/201903/15/c1182c311fabcbdc1d5d7c932ae517fe.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
 
#### 配置脚本
vim /restart_ssh.sh
```
#/bin/bash 
systemctl restart sshd
```
对脚本授予可执行权限
`chmod +x /restart_sshd.sh`
#### 创建ssh的监控项
![](https://s1.51cto.com/images/blog/201903/15/8c8fe8c443c6fa4cc1ed7217ca02c587.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 创建触发器
![](https://s1.51cto.com/images/blog/201903/15/a1c5371158e77f50c3b0b0b6643be330.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
![](https://s1.51cto.com/images/blog/201903/15/f09933f5fd1ad3354bebe7cf2ffb56fc.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
 
#### 配置动作
创建动作
![](https://s1.51cto.com/images/blog/201903/15/8946fa581094fd278a6180fdaabc09fb.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
配置动作触发条件
![](https://s1.51cto.com/images/blog/201903/15/bb749c0fa4c094d14beca9c65cdc8091.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
配置动作执行的命令，这里为了方便查看效果，延迟两分钟执行
![](https://s1.51cto.com/images/blog/201903/15/b8880072177d5d68e9cdf130dab2fd01.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 触发报警
这里关闭ssh服务，使报警触发
`systemctl stop sshd`
#### 报警触发，两分钟后执行脚本
这里可以使用zabbix-get来获取监控的值。来查看是否成功执行命令
zabbix_get -s 192.168.179.132 -k net.tcp.port[192.168.179.132,22]
可以看到，zabbix已经成功执行脚本，重启ssh
![](https://s1.51cto.com/images/blog/201903/15/b024964935f204d646ecdfa452c177e6.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)


