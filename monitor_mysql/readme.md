**监控Mysql**

我在监控mysql的时候使用mysqladmin，老是提示密码问题，最后我通过skip-grant-tables修改了密码，赋予了相关权限就正常了。在/etc/my.cnf中需要添加mysqladmin的相关配置。

```
/usr/bin/mysqladmin --defaults-file=/etc/my.cnf -h192.168.40.200 -P3306  extended-status |grep -w "Bytes_sent" |cut -d"|" -f3
mysqladmin: connect to server at '192.168.40.200' failed
error: 'Access denied for user 'root'@'192.168.40.200' (using password: YES)'
[root@ansible-k8s1 mysql]# !248
/usr/bin/mysqladmin --defaults-file=/etc/my.cnf -hlocalhost -P3306  extended-status |grep -w "Bytes_sent" |cut -d"|" -f3
mysqladmin: connect to server at 'localhost' failed
error: 'Access denied for user 'root'@'localhost' (using password: YES)'
```
