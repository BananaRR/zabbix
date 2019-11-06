---
title: 在zabbix中实现发送带有图片的邮件和微信告警
grammar_cjkRuby: true
---

# 1 python实现在4.2版本zabbix发送带有图片的报警邮件
> 我们通常收到的报警，都是文字，把动作中的消息内容当成了正文参数传给脚本，然后邮件或者微信进行接收，往往只能看到当前值，无法直观的获取到历史当天的运行曲线图，因此根据此需求，使用python编写脚本来分别对邮件告警和微信告警，进行升级，报警内容中加入了当天的历史趋势图，功夫不负有心人，已成功解锁，并实践成功，因此分享出来供大家参考，另外得非常感谢脚本编写中刚哥大神和王二基友给予的帮助

## 1.1 实现思路
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1572961264766.png)

- 首先报警信息里第一行要有itemid，这是前提，根据信息里传入的参数使用正则匹配到itemid
- 使用脚本创建一个zabbix会话，来根据itemid来获取图片，并将获取到的图片保存到本地
- 将传入的参数信息的text字段转换成HTML格式，然后将HTML格式的信息和图片作为邮件进行发送

## 1.2 准备环境

- 脚本是使用python脚本，运行环境为python 2.7.5
- 依赖库：requests

## 1.3 脚本实现

``` python
[root@5804703917ad zabbix]# cd /usr/lib/zabbix/alertscripts/  #进入zabbix默认的脚本路径
[root@5804703917ad alertscripts]# mkdir graph #创建一个存放图片的文件夹
[root@5804703917ad alertscripts]# chmod 777 graph #给文件夹赋予权限
[root@5804703917ad alertscripts]# vim zabbix_email_pic.py #编写实现脚本
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
graph_url='http://192.168.73.133/chart.php'     #定义图表的url
loginurl="http://192.168.73.133/index.php"          #定义登录的url
host='192.168.73.133'
to_email=sys.argv[1]    #传入的第一个参数为收件人邮箱
subject=sys.argv[2]  #传入的第二个参数为邮件主题
subject=subject.decode('utf-8')
smtp_host = 'smtp.163.com'  #定义smtp主机地址
from_email = 'xxxx@163.com.cn'     #定义发件人地址
mail_pass = 'xxx'       #发件人邮箱校验码

def get_itemid():
    #获取报警的itemid
    itemid=re.search(r'监控ID:(\d+)',sys.argv[3]).group(1)
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
        print(e)
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
        server=SMTP(smtp_host,"587")   #创建一个smtp对象
        server.starttls()    #启用安全传输模式
        server.login(from_email,mail_pass)  #邮箱账号登录
        server.sendmail(from_email,to_email,msg.as_string())  #发送邮件
        server.quit()   #断开smtp连接
    except smtplib.SMTPException as a:
        print(a)

def run():
    itemid=get_itemid()
    graph_name=get_graph(itemid)
    send_mail(graph_name)

if __name__ =='__main__':
    run()
```
## 1.4 定义报警媒介类型
- 打开zabbix监控web，在管理菜单中选择报警媒介类型，创建媒体类型，选择脚本，添写刚才编写的邮件带图脚本名称zabbix_email_pic.py，脚本参数，最后添加
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1572966471006.png)

- 打开管理中的用户，点击需要设置邮件告警的用户，然后在报警媒介中添加报警媒介，在弹框中选择刚才定义的类型，然后填写想要发送的邮箱地址，最后添加
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1572966530657.png)
## 1.5 定义告警动作
- 点击配置菜单中的动作，创建动作，然后根据图片进行填写

``` mathematica
操作
默认标题 Zabbix告警：服务器:{HOSTNAME}发生: {TRIGGER.NAME}故障!
监控ID:{ITEM.ID}
告警主机:{HOST.NAME}
告警主机:{HOST.IP}
告警时间:{EVENT.DATE} {EVENT.TIME}
告警等级:{TRIGGER.SEVERITY}
告警信息: {TRIGGER.NAME}
告警项目:{TRIGGER.KEY}
问题详情:{ITEM.NAME}:{ITEM.VALUE}
当前状态:{TRIGGER.STATUS}:{ITEM.VALUE}
事件ID:{EVENT.ID}
恢复操作
Zabbix告警：服务器:{HOST.NAME}发生: {TRIGGER.NAME}已恢复!
监控ID:{ITEM.ID}
告警主机:{HOST.NAME}
告警主机:{HOST.IP}
告警时间:{EVENT.DATE} {EVENT.TIME}
告警等级:{TRIGGER.SEVERITY}
告警信息: {TRIGGER.NAME}
告警项目:{TRIGGER.KEY}
问题详情:{ITEM.NAME}:{ITEM.VALUE}
当前状态:{TRIGGER.STATUS}:{ITEM.VALUE}
事件ID:{EVENT.ID}
```

![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1572966970402.png)
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573047709672.png)
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573047749670.png)
## 1.6 最终效果
可以手动触发一个报警测试效果
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1572967317080.png)

# 2 python实现在4.2版本zabbix发送带有图片的微信告警
## 2.1 实现思路
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573047524724.png)

- 首先创建企业公众号获取agentId，secret和部门id
- 然后根据报警信息获取itemid,使用正则匹配到itemid
- 使用脚本创建一个zabbix会话，来根据itemid来获取图片，并将获取到的图片保存到本地
- 调用企业微信api接口，把图片当成临时素材上传，返回一个media_id，给发送消息和图片调用使用，最后使用mpnews消息类型把图片和报警内容进行推送到微信上
## 2.2 准备环境
- 脚本是使用python脚本，运行环境为python 2.7.5
- 依赖库提前安装：requests

## 2.3 创建企业公众号获取agentid，secret
这部分内容，可以查看前面不带图的文章有详细描述

## 2.4 脚本实现

``` python
[root@5804703917ad zabbix]# cd /usr/lib/zabbix/alertscripts/  #进入zabbix默认的脚本路径
[root@5804703917ad alertscripts]# mkdir graph #创建一个存放图片的文件夹
[root@5804703917ad alertscripts]# chmod 777 graph #给文件夹赋予权限
[root@5804703917ad alertscripts]# vim zabbix_weixin_pic.py #编写实现脚本
#!/usr/bin/python
#coding=utf-8
_author__ = 'zhangdongdong'
import requests, json
import urllib3
import smtplib,sys,os,time,re,requests
from email.mime.image import MIMEImage
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
urllib3.disable_warnings()
class WechatImage(object): # 根据企业微信api接口文档，定义一个类，使用mpnews类型，https://qydev.weixin.qq.com/wiki/index.php?title=%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F

    def get_token(self, corpid, secret): # 获取token
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        data = {"corpid": corpid,
                "corpsecret": secret}
        r = requests.get(url=url, params=data, verify=False)
        token = r.json()['access_token']
        return token

    def get_image_url(self, token, path): # 上传临时素材图片，然后返回media_id
        url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image" % token
        data = {"media": open(path, 'rb')}
        r = requests.post(url=url, files=data)
        dict_data = r.json()
        return dict_data['media_id']
    def get_messages( self,subject,content,path): #定义mpnews类型中的参数字典
        data = ''
        messages = {}
        body = {}
        content_html=text_to_html(content)
        token = self.get_token(corpid, secret)
        image = self.get_image_url(token, path)
        content_html += "<br/> <img src='https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s'>" % (token, image)
        body["title"] = subject
        body['digest'] = content
        body['content'] = content_html
        body['thumb_media_id'] = image
        data = []
        data.append(body)
        messages['articles'] = data
        return messages
    def send_news_message(self, corpid, secret,to_user, agentid,path): #定义发送mpnews类型的数据
        token = self.get_token(corpid, secret)
        messages = self.get_messages( subject, content,path)
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % token
        data = {"toparty": to_user,                                 # 企业号中的用户帐号
                "agentid": agentid,                             # 企业号中的应用id
                "msgtype": "mpnews",
                "mpnews": messages,
                "safe": "0"}
        headers = {'content-type': 'application/json'}
        data_dict = json.dumps(data, ensure_ascii=False).encode('utf-8')
        r = requests.post(url=url, headers=headers, data=data_dict)
        return r.text
def text_to_html(text): #将邮件内容text字段转换成HTML格式
    d=text.splitlines()
    #将邮件内容以每行作为一个列表元素存储在列表中
    html_text=''
    for i in d:
        i='' + i + '<br>'
        html_text+=i + '\n'
    #为列表的每个元素后加上html的换行标签
    return html_text
def get_itemid():
    #获取报警的itemid
    itemid=re.search(r'监控ID:(\d+)',sys.argv[3]).group(1)
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
            "width" : "290", #图片的高宽参数可以自行调整
            "height" : "40",
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
        print(e)
        return False
if __name__ == '__main__':
    user='Admin'    #定义zabbix用户名
    password='zabbix'    #定义zabbix用户i密
    graph_path='/usr/lib/zabbix/alertscripts/graph/'   #定义图片存储路径，图片需要定时清理
    graph_url='http://192.168.73.133/chart.php'     #定义图表的url
    loginurl="http://192.168.73.133/index.php"          #定义登录的url
    host='192.168.73.133'
    itemid=get_itemid()
    path =get_graph(itemid)
    to_user = str(sys.argv[1]) 
    subject = str(sys.argv[2]) 
    content = str(sys.argv[3])
    corpid= "xxxxx"
    secret = "xxxxxxx"
    agentid = "1000002"
    wechat_img = WechatImage()
    wechat_img.send_news_message(corpid, secret,to_user, agentid, path)
```
## 2.5 定义报警媒介类型
- 打开zabbix监控web，在管理菜单中选择报警媒介类型，创建媒体类型，选择脚本，添写刚才编写的微信带图脚本名称zabbix_weixin_pic.py，脚本参数，最后添加
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573049266721.png)

- 打开管理中的用户，点击需要设置邮件告警的用户，然后在报警媒介中添加报警媒介，在弹框中选择刚才定义的类型，然后填写企业微信中创建的部门id，最后添加
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573049389741.png)
## 2.6 定义告警动作
- 点击配置菜单中的动作，创建动作，然后根据图片进行填写

``` mathematica
操作
默认标题 Zabbix告警：服务器:{HOSTNAME}发生: {TRIGGER.NAME}故障!
监控ID:{ITEM.ID}
告警主机:{HOST.NAME}
告警主机:{HOST.IP}
告警时间:{EVENT.DATE} {EVENT.TIME}
告警等级:{TRIGGER.SEVERITY}
告警信息: {TRIGGER.NAME}
告警项目:{TRIGGER.KEY}
问题详情:{ITEM.NAME}:{ITEM.VALUE}
当前状态:{TRIGGER.STATUS}:{ITEM.VALUE}
事件ID:{EVENT.ID}
恢复操作
Zabbix告警：服务器:{HOST.NAME}发生: {TRIGGER.NAME}已恢复!
监控ID:{ITEM.ID}
告警主机:{HOST.NAME}
告警主机:{HOST.IP}
告警时间:{EVENT.DATE} {EVENT.TIME}
告警等级:{TRIGGER.SEVERITY}
告警信息: {TRIGGER.NAME}
告警项目:{TRIGGER.KEY}
问题详情:{ITEM.NAME}:{ITEM.VALUE}
当前状态:{TRIGGER.STATUS}:{ITEM.VALUE}
事件ID:{EVENT.ID}
```
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573049449988.png)
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573049474228.png)
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573049553801.png)
## 2.7 测试效果
可以手动触发一个报警测试效果，手机上就可以收到带图的报警了，点击消息之后的页面也可以看到历史的图片
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573050081734.png)
![enter description here](http://pz44s0bl5.bkt.clouddn.com/blog/1573050115728.png)