**说明**：发送zabbix告警信息到qq邮箱，参考：[链接](http://www.ttlsa.com/linux/use-sendemail/ "链接")，另外163邮箱需要开通POP3/IMAP/SMTP

* 安装sendEmail wget http://caspian.dotconf.net/menu/Software/SendEmail/sendEmail-v1.56.tar.gz //下载1.56版本
* tar -xzvf sendEmail-v1.56.tar.gz //解压后就可以使用了
* mv sendEmail /usr/local/bin/
* 测试发邮件：sendEmail -f *******@163.com -t *******@qq.com -s smtp.163.com -u "邮件主题" -o message-content-type=html #邮件格式
-o message-charset=utf8#邮件内容编码 -xu *******@163.com#发件人邮箱用户 -xp xxx#发件人邮箱密码 -m "邮件内容"
