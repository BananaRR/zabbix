### 安装并配置mailx
#### 安装mailx
`yum install -y mailx`
#### 修改mailx配置文件
`vim vim /etc/mail.rc`
```
set from=wang210@163.com  #定义发件人
set smtp=smtp.163.com  #定义smtp服务器
set smtp-auth-user=wang210@163.com 
set smtp-auth-password=asdASD123
set smtp-auth=login
```
#### 发送测试邮件
`echo 'test1'|mail -s "testmail" wang210@126.com`
#### 编写邮件告警脚本
`vim /usr/lib/zabbix/alertscripts/mail.sh`
这是zabbix默认的脚本路径，可以通过zabbix_server配置文件修改
```bash
#/bin/bash
to=$1
subject=`echo $2|tr '\r\n' '\n'`
message=`echo $3|tr '\r\n' '\n'`
echo "$message"|mail -s "$subject" $to >>/var/log/mailx.log 2>&1
```
touch /var/log/mailx.log
chown -R zabbix.zabbix /var/log/mailx.log
chmod +x /usr/lib/zabbix/alertscripts/mail.sh
./mail.sh wang210@126.com "主题" "内容"

#### 编辑zabbix_web，配置报警媒介
![](http://i2.51cto.com/images/blog/201812/26/4b30209d2fd8e34fddbede58eb5d0e59.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
脚本参数的变量全为大写，是zabbix内置的宏
更多关于zabbix的宏可以查看 [官方文档宏的介绍](https://www.zabbix.com/documentation/4.0/manual/appendix/macros/supported_by_location)
除了使用脚本媒介，也可以使用email作为媒介，相比之下，使用email更简单
![](http://i2.51cto.com/images/blog/201812/26/0dd2ee62175b57174231f0243ce868df.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 编辑zabbix_web,配置用户
![](http://i2.51cto.com/images/blog/201812/26/6dfce1ea7e91282c2af003f9240ff0e3.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

![](http://i2.51cto.com/images/blog/201812/26/d89d480b672450d5266347f765884b65.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 配置报警动作
操作，恢复操作，或者更新操作必须存在一个
##### 配置条件
可以根据自己的需要配置触发条件
![](http://i2.51cto.com/images/blog/201812/26/8014d73a490f194019802c26c0291111.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 配置操作
默认标题：

```
{TRIGGER.STATUS}:{TRIGGER.NAME}
```

消息内容：

```
报警主机：{HOST.NAME}
报警IP：{HOST.IP}
报警时间：{EVENT.DATE}-{EVENT.TIME}
报警等级：{TRIGGER.SEVERITY}
报警信息：{TRIGGER.NAME}：{ITEM.VALUE}
事件ID：{EVENT.ID}
```

![](http://i2.51cto.com/images/blog/201812/26/bd22df3fccc6b83f94d0b0068dcab6ba.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 配置恢复操作
默认标题：

```
{TRIGGER.STATUS}:{TRIGGER.NAME}

```

消息内容：

```
恢复主机：{HOST.NAME}
恢复IP：{HOST.IP}
恢复时间：{EVENT.DATE}-{EVENT.TIME}
恢复等级：{TRIGGER.SEVERITY}
恢复信息：{TRIGGER.NAME}:{ITEM.VALUE}
恢复ID：{EVENT.ID}
```

![](http://i2.51cto.com/images/blog/201812/26/3fe7d7252ec3ed0619515cccea210c51.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 关闭agent，测试报警
`systemctl stop zabbix_agent`
![](http://i2.51cto.com/images/blog/201812/26/66f5765e3a51d384d19f892129900e38.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
`systemctl start zabbix_agent`
![](http://i2.51cto.com/images/blog/201812/26/7b610b3290faf31421b7f75f7a4c572b.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

### 配置微信报警
#### 注册企业微信
配置微信报警需要注册[企业微信](https://work.weixin.qq.com/wework_admin/frame)
#### 获取企业ID
点击‘我的企业’到最下面获取
![](http://i2.51cto.com/images/blog/201812/26/b6599f09a564f242de833497f2b8d930.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

####  获取AgentID和Secret
单击应用与小程序，选择下面的创建应用，应用名字自己随便起，最好有象征意义
![](http://i2.51cto.com/images/blog/201812/26/3ff5841c77954523003a60bd00a65de8.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

![](http://i2.51cto.com/images/blog/201812/26/9762e8c984e502cc155f5a0fa6e4500b.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
然后打开新创建的应用，记录下AgentID和Secret
### 配置脚本
#### 从GitHub克隆微信报警脚本
```bash
git clone https://github.com/X-Mars/Zabbix-Alert-WeChat.git
cp Zabbix-Alert-WeChat/wechat.py /usr/local/zabbix34/alertscripts/
chmod +x wechat.py && chown zabbix:zabbix wechat.py
```
#### 安装requests库
使用pip安装，需要先下载pip
```
python  get-pip.py
```
安装requests库
```bash 
pip install requests
```
#### 修改wechat.py脚本
Corpid，Secret，Agentid填写自己企业微信的信息，修改这三个参数即可，当然也可以选择使用标签ID，部门ID，取消注释即可
![](http://i2.51cto.com/images/blog/201812/26/133026e0013bd3ff66cb257c40ac4a4b.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

修改完成后测试脚本是否可用
```
python wechat.py 企业微信ID test text
{u'invaliduser': u'', u'errcode': 0, u'errmsg': u'ok'}
```
### 在zabbix_web上配置报警媒介和用户
#### 配置报警媒介
![](http://i2.51cto.com/images/blog/201812/26/9be9b96ea260b5481765943ce41aee93.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 配置用户
收件人填写企业微信的用户ID
![](http://i2.51cto.com/images/blog/201812/26/c428cbc26995e56fe763d76be730f51f.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

### 配置动作
#### 配置操作
消息内容与标题与邮件报警配置相同，只要把发送的媒介通过WeChat发送即可
![](http://i2.51cto.com/images/blog/201812/26/75504adfad809b4fbdb3e99fa63e157c.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 配置恢复操作
恢复操作也是把媒介改成通过WeChat发送
![](http://i2.51cto.com/images/blog/201812/26/7e18c7cc7a52fccf8974d470cbc24129.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

### 测试微信报警
重启虚拟机测试,企业微信收到邮件

![](http://i2.51cto.com/images/blog/201812/26/7682e523da05b253535a4df4d54be955.jpg?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)