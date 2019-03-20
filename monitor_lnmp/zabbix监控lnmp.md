> 由于zabbix服务是由lnmp搭建的，所以需要监控nginx，mysql，zabbix以及服务器的性能

### 监控nginx
#### 首先开启nginx的status状态  

需要用到ngx_http_stub_status_module模块，提供对基本状态信息的访问默认情况下不构建此模块，应使用--with-http_stub_status_module 配置参数启用它 。
修改nginx配置文件，在server下添加
vim /etc/nginx/conf.d/zabbix.conf 
```
location /status{ 
        stub_status;
    } 
```
重载nginx配置
`systemctl  reload nginx`
配置完成后访问127.0.0.1/status可以查看nginx运行状态

![](https://s1.51cto.com/images/blog/201903/20/f3d4f3c82495b83da1674c43cc341fac.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

**参数解释：**  

> Active connections：当前活动客户端连接数，包括Waiting连接数。
> accepts：已接受的客户端连接总数。
> handled：已处理连接的总数。
> requests：客户端请求的总数。
> Reading：nginx正在读取请求标头的当前连接数。
> Writing：nginx将响应写回客户端的当前连接数。
> Waiting：当前等待请求的空闲客户端连接数。  

#### 编写脚本监控nginx
```bash
#/bin/bash
ping() {
    /sbin/pidof nginx | wc -l
}
nginx_active(){
    /usr/bin/curl -s "http://127.0.0.1/status/" |awk '/Active/ {print $NF}'
}
reading(){
    /usr/bin/curl -s "http://127.0.0.1/status/" |awk '/Reading/ {print $2}'
}
writing(){
    /usr/bin/curl -s "http://127.0.0.1/status/" |awk '/Writing/ {print $4}'
       }
waiting(){
    /usr/bin/curl -s "http://127.0.0.1/status/" |awk '/Waiting/ {print $6}'
       }
accepts(){
    /usr/bin/curl -s "http://127.0.0.1/status/" |awk 'NR==3 {print $1}'
       }
handled(){
    /usr/bin/curl -s "http://127.0.0.1/status/" |awk 'NR==3 {print $2}'
       }
requests(){
    /usr/bin/curl -s "http://127.0.0.1/status/" |awk 'NR==3 {print $3}'
       }
$1
```  

##### 给脚本授予执行权限
`chmod +x /usr/lib/zabbix/alertscripts/monitor_nginx.sh`

##### 修改zabbix-agent配置文件
vim /etc/zabbix/zabbix_agentd.d/userparameter_mysql.conf
`UserParameter=nginx.[*],/usr/lib/zabbix/alertscripts/monitor_nginx.sh $1`

##### 重启zabbix-agent
`systemctl restart zabbix-agent`

##### 使用zabbix-get测试一下
`zabbix_get -s 192.168.179.132 -k nginx.[ping]`

#### 创建nginx监控模板

![](https://s1.51cto.com/images/blog/201903/20/3011d8a3153047a39db803b7ff9657ac.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 配置模板

![](https://s1.51cto.com/images/blog/201903/20/852ffeae176b25446c4f6ddf715cfec0.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

![](https://s1.51cto.com/images/blog/201903/20/054e10e6d318c4703b462b826ecd96fe.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 创建一个nginx的应用集

![](https://s1.51cto.com/images/blog/201903/20/7a4a0779e8acbce97fcd86462947ff91.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 添加监控项
将nginx的status的内容添加监控项，这里以nginx.ping为例

![](https://s1.51cto.com/images/blog/201903/20/d812534d4a0abf8660633f4acdad82ae.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 创建触发器
![](https://s1.51cto.com/images/blog/201903/20/14af956e7e7c3c1172ce7ad2d6619bd1.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
![](https://s1.51cto.com/images/blog/201903/20/c8f293088c0142de31d377ccf3ebb7b2.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 创建图形
![](https://s1.51cto.com/images/blog/201903/20/ee877aa7e1737de3fb939923b9b67311.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 将模板链接到监控的主机
![](https://s1.51cto.com/images/blog/201903/20/cc2f5915cf201e76beb28927d865db02.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

可以看到nginx的状态信息已经出现在了nginx上
![](https://s1.51cto.com/images/blog/201903/20/b7febe9567dc95f8451ff004882b0300.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

### 监控mysql
mysql的状态信息可以通过以下命令获取
```
mysqladmin -uroot -proot extended-status
mysqladmin -uroot -proot status
```

但是使用明文密码会有如下警告信息，zabbix也会取到这个报错，导致监控项错误，解决方法可以将用户名密码写入到mysql配置文件的mysqladmin中，然后在运行命令时指定配置文件就可以了，命令如下：
```
mysqladmin --defaults-extra-file=/etc/my.cnf status
```

但是修改完配置文件需要重启mysql，这在生产环境中显然不太现实，这里我有两种方法，两种方法都是在系统上配置脚本的不同，web页面配置相同，个人推荐使用第一种方法，简单方便

>1.直接将错误信息重定向为空
>2.将取到的值输出到特定文件里

![](https://s1.51cto.com/images/blog/201903/20/98f84fc43513aea1deca5d3e98a0f521.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 系统配置

**第一种方法：**
编写监控脚本
vim /usr/lib/zabbix/alertscripts/monitor_mysql.sh
```bash
#/bin/bash
MYSQL_USER='root'
# 密码
MYSQL_PWD='root'
# 主机地址/IP
MYSQL_HOST='192.168.179.132'
# 端口
MYSQL_PORT='3306'
# 数据连接
MYSQL_CONN="/usr/local/mysql/bin/mysqladmin -u${MYSQL_USER} -p${MYSQL_PWD} -h${MYSQL_HOST} -P${MYSQL_PORT}"

if [ $# -ne "1" ];then 
    echo "arg error!" 
    exit 1
fi 

case $1 in 
    Uptime) 
        result=`${MYSQL_CONN} status 2>/dev/null|cut -f2 -d":"|cut -f1 -d"T"` 
        echo $result
        ;; 
    Com_update) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Com_update"|cut -d"|" -f3` 	  
	echo $result
        ;; 
    Slow_queries) 
        result=`${MYSQL_CONN} status 2>/dev/null|cut -f5 -d":"|cut -f1 -d"O"` 
        echo $result 
        ;; 
    Com_select) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Com_select"|cut -d"|" -f3` 	  
	echo $result
        ;; 
    Com_rollback) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Com_rollback"|cut -d"|" -f3` 
        echo $result 
        ;; 
    Questions) 
        result=`${MYSQL_CONN} status 2>/dev/null|cut -f4 -d":"|cut -f1 -d"S"` 
        echo $result 
        ;; 
    Com_insert) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Com_insert"|cut -d"|" -f3`
        echo $result 
        ;; 
    Com_delete) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Com_delete"|cut -d"|" -f3`
        echo $result 
        ;; 
    Com_commit) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Com_commit"|cut -d"|" -f3`
        echo $result 
        ;; 
    Bytes_sent) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Bytes_sent" |cut -d"|" -f3` 
        echo $result 
        ;; 
    Bytes_received) 
        result=`${MYSQL_CONN} extended-status 2>/dev/null|grep -w "Bytes_received" |cut -d"|" -f3` 
        echo $result 
        ;; 
    Com_begin) 
        result=`${MYSQL_CONN} extended-status 2>/dev/mull|grep -w "Com_begin"|cut -d"|" -f3`  
        echo $result 
        ;; 
    Open_tables)
        result=`${MYSQL_CONN} extended-status 2>/dev/mull|grep -w "Open_tables"|cut -d"|" -f3`
        echo $result 
	     ;;
    *) 
        echo "Usage:$0(Uptime|Com_update|Slow_queries|Com_select|Com_rollback|Questions|Com_insert|Com_delete|Com_commit|Bytes_sent|Bytes_received|Com_begin|Open_tables)" 
        ;;
esac

```
##### 给脚本授予可执行权限
`chmod +x /usr/lib/zabbix/alertscripts/monitor_mysql.sh`

##### 修改zabbix-agent配置文件
vim /etc/zabbix/zabbix_agentd.d/userparameter_mysql.conf
```
UserParameter=mysql.status[*],/usr/lib/zabbix/alertscripts/monitor_mysql.sh $1
UserParameter=mysql.ping,/usr/local/mysql/bin/mysqladmin -uroot -proot ping 2>/dev/null |grep -c alive
UserParameter=mysql.slave,mysql -uroot -proot -e 'show slave status\G' 2>/dev/null|grep -E "Slave_IO_Running|Slave_SQL_Running"|awk '{print $2}'|grep -c Yes
```

##### 重启zabbix-agent
`systemctl restart zabbix-agent`

##### 使用zabbix_get测试是否成功获取值
```
zabbix_get -s 192.168.179.132 -k mysql.ping
zabbix_get -s 192.168.179.132 -k mysql.[Uptime]
```
![](https://s1.51cto.com/images/blog/201903/20/3ae3ef79b7cb45830913bf4c4ea638d4.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

**第二种方法：**
编写监控脚本
vim /usr/lib/zabbix/alertscripts/monitor_mysql.sh
```
#!/bin/bash
# -------------------------------------------------------------------------------
# FileName:    check_mysql.sh
# -------------------------------------------------------------------------------
MYSQL_USER='root'
# 密码
MYSQL_PWD='root'
# 主机地址/IP
MYSQL_HOST='192.168.179.132'
# 端口
MYSQL_PORT='3306'
# 数据连接
MYSQL_CONN="/usr/local/mysql/bin/mysqladmin -u${MYSQL_USER} -p${MYSQL_PWD} -h${MYSQL_HOST} -P${MYSQL_PORT}"
#MYSQL_CONN="/usr/local/mysql/bin/mysqladmin "
# 参数是否正确
if [ $# -ne "1" ];then 
    echo "arg error!" 
fi 
# 获取数据
case $1 in 
    Uptime) 
        result=`${MYSQL_CONN} status|cut -f2 -d":"|cut -f1 -d"T"` 
        echo $result 
        ;; 
    Com_update) 
        result=`${MYSQL_CONN} extended-status |grep -w "Com_update"|cut -d"|" -f3` 
        echo $result 
        ;; 
    Slow_queries) 
        result=`${MYSQL_CONN} status |cut -f5 -d":"|cut -f1 -d"O"` 
        echo $result 
        ;; 
    Com_select) 
        result=`${MYSQL_CONN} extended-status |grep -w "Com_select"|cut -d"|" -f3` 
        echo $result 
                ;; 
    Com_rollback) 
        result=`${MYSQL_CONN} extended-status |grep -w "Com_rollback"|cut -d"|" -f3` 
                echo $result 
                ;; 
    Questions) 
        result=`${MYSQL_CONN} status|cut -f4 -d":"|cut -f1 -d"S"` 
                echo $result 
                ;; 
    Com_insert) 
        result=`${MYSQL_CONN} extended-status |grep -w "Com_insert"|cut -d"|" -f3` 
                echo $result 
                ;; 
    Com_delete) 
        result=`${MYSQL_CONN} extended-status |grep -w "Com_delete"|cut -d"|" -f3` 
                echo $result 
                ;; 
    Com_commit) 
        result=`${MYSQL_CONN} extended-status |grep -w "Com_commit"|cut -d"|" -f3` 
                echo $result 
                ;; 
    Bytes_sent) 
        result=`${MYSQL_CONN} extended-status |grep -w "Bytes_sent" |cut -d"|" -f3` 
                echo $result 
                ;; 
    Bytes_received) 
        result=`${MYSQL_CONN} extended-status |grep -w "Bytes_received" |cut -d"|" -f3` 
                echo $result 
                ;; 
    Com_begin) 
        result=`${MYSQL_CONN} extended-status |grep -w "Com_begin"|cut -d"|" -f3` 
                echo $result 
                ;; 

        *) 
        echo "Usage:$0(Uptime|Com_update|Slow_queries|Com_select|Com_rollback|Questions|Com_insert|Com_delete|Com_commit|Bytes_sent|Bytes_received|Com_begin)" 
        ;; 
esac

```  

给脚本授予执行权限
`chmod +x /usr/lib/zabbix/alertscripts/monitor_mysql.sh`

将脚本放入后台运行
`nohup /usr/lib/zabbix/alertscripts/monitor_mysql.sh &`

修改zabbix-agent配置文件
vim /etc/zabbix/zabbix_agentd.d/userparameter_mysql.conf
```
UserParameter=mysql.version,/usr/local/mysql/bin/mysql -V
UserParameter=mysql.Uptime,cat /monitor_mysql/Uptime.txt
UserParameter=mysql.Com_update,cat /monitor_mysql/Com_update.txt
UserParameter=mysql.Slow_queries,cat /monitor_mysql/Slow_queries.txt
UserParameter=mysql.Com_select,cat /monitor_mysql/Com_select.txt
UserParameter=mysql.Com_rollback,cat /monitor_mysql/Com_rollback.txt
UserParameter=mysql.Questions,cat /monitor_mysql/Questions.txt
UserParameter=mysql.Com_insert,cat /monitor_mysql/Com_insert.txt
UserParameter=mysql.Com_delete,cat /monitor_mysql/Com_delete.txt
UserParameter=mysql.Com_commit,cat /monitor_mysql/Com_commit.txt
UserParameter=mysql.Bytes_sent,cat /monitor_mysql/Bytes_sent.txt
UserParameter=mysql.Bytes_received,cat /monitor_mysql/Bytes_received.txt
UserParameter=mysql.Com_begin,cat /monitor_mysql/Com_begin.txt
UserParameter=mysql.ping,cat /monitor_mysql/ping.txt
```  

##### 重启zabbix-agent
`systemctl  restart zabbix-agent`

##### 使用zabbix_get测试键值是否可用
```
zabbix_get -s 192.168.179.132 -k mysql.Com_begin
zabbix_get -s 192.168.179.132 -k mysql.Questions
```  

![](https://s1.51cto.com/images/blog/201903/20/3461905a103a5051a1e581f1e62ed13c.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 添加模板
zabbix自带了一个mysql的模板，我们只需要在原有模板上修改一下就可以了
![](https://s1.51cto.com/images/blog/201903/20/3dbd15944c878b78546b7b37a5eaa4e4.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

##### 修改监控项，与配置文件的相同
![](https://s1.51cto.com/images/blog/201903/20/00728b37655cce296b27fbf619352a3c.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
##### 修改完的监控项如下所示
![](https://s1.51cto.com/images/blog/201903/20/4f4a25d4e71a089ecfc25e20256debcf.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
##### 将数据库模板链接到lnmp模板上
![](https://s1.51cto.com/images/blog/201903/20/1f85f8653da23570402c19eccb14f25f.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
### 监控php-fpm
#### 修改PHP配置文件，启用php-fpm的状态功能
vim /usr/local/php/etc/php-fpm.d/www.conf，添加以下字段，以启用php-fpm的状态功能
`pm.status_path = /php_status`

vim /usr/local/php/etc/php-fpm.conf，将下面字段取消注释，这样就可以使用pid文件进行重启php-fpm
`pid = run/php-fpm.pid`


##### 重启php-fpm
```
kill -USR2 `cat /usr/local/php/var/run/php-fpm.pid`
```  

#### 修改nginx配置文件
##### 在nginx中开启对php-fpm的状态访问
```
location ~ ^/(php_status|ping)$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME /usr/share/nginx/html$fastcgi_script_name;
        include fastcgi_params;
}        
```  

##### 重载nginx
`systemctl reload nginx`

##### 测试配置是否成功
`curl 127.0.0.1/php_status`  

![](https://s1.51cto.com/images/blog/201903/20/69ce45c74dddbe467bac2f7106ac7cf5.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
##### 访问带参数的页面
`curl 127.0.0.1/php_status?full`

![](https://s1.51cto.com/images/blog/201903/20/18976ac73e86e85993ecbeaf4d16916a.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

**php-fpm状态参数解释：**  

> pool：php-fpm池名称，大多数为www
> process manager：进程管理方式,值：static, dynamic or ondemand. dynamic
> start time：启动日期,如果reload了php-fpm，时间会更新
> start since：运行时长
> accepted conn：当前池接受的请求数
> listen queue：请求等待队列，如果这个值不为0，那么要增加FPM的进程数量
> max listen queue：请求等待队列最高的数量
> listen queue len：socket等待队列长度
> idle processes：空闲进程数量
> active processes：活跃进程数量
> total processes：总进程数量
> max active processes：最大的活跃进程数量（FPM启动开始算）
> max children reached：进程最大数量限制的次数，如果这个数量不为0，那说明你的最大进程数量太小了，请改大一点。
> slow requests：启用了php-fpm slow-log，缓慢请求的数量

**full详解：**  

> pid – 进程PID，可以单独kill这个进程.
> state – 当前进程的状态 (Idle, Running, …)
> start time – 进程启动的日期
> start since – 当前进程运行时长
> requests – 当前进程处理了多少个请求
> request duration – 请求时长（微妙）
> request method – 请求方法 (GET, POST, …)
> request URI – 请求URI
> content length – 请求内容长度 (仅用于 POST)
> user – 用户 (PHP_AUTH_USER) (or ‘-’ 如果没设置)
> script – PHP脚本 (or ‘-’ if not set)
> last request cpu – 最后一个请求CPU使用率。
> last request memorythe - 上一个请求使用的内存  

#### 配置zabbix-agent文件，添加php-fpm监控
```
vim /etc/zabbix/zabbix_agentd.d/userparameter_mysql.conf
UserParameter=php-fpm.status[*],/usr/bin/curl -s "http://127.0.0.1/php_status?xml"| grep "<$1>"|/usr/bin/cut -d '>' -f2 |cut -d '<' -f1 UserParameter=php-fpm.ping,/sbin/pidof php-fpm | wc -l UserParameter=php-fpm.version,/usr/local/php/sbin/php-fpm -v | awk 'NR==1{print $1,$2}'
```  

##### 重启zabbix-agent
`systemctl restart zabbix-agent`
##### 使用zabbix_get测试
![](https://s1.51cto.com/images/blog/201903/20/e5c6fec4dad77b6d1407d2fd822f9aa5.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

#### 添加监控项到模板
![](https://s1.51cto.com/images/blog/201903/20/fb060b6b2976843d4dfdaf13d867c6f5.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=) 


##### 以添加php-fpm启停状态监控为例
![](https://s1.51cto.com/images/blog/201903/20/518875a4fff82395077c3077337d4863.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  
##### php-fpm所有监控如下所示
![](https://s1.51cto.com/images/blog/201903/20/9dba17df79f1d94fd6f72adf6e216ed0.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
##### 创建触发器
![](https://s1.51cto.com/images/blog/201903/20/8dde03ebfcb0fb132af5f603ac9f7ef6.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
##### 创建图形
![](https://s1.51cto.com/images/blog/201903/20/af92c115394655ed25eb83e7bb312f1e.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)

### 监控zabbix-server
zabbix自带了监控自身的模板，因此只要在模板上链接zabbix-server的模板就可以了，zabbix-agent的模板已经链接到os的模板上了，因此无需添加zabbix-agent模板
![](https://s1.51cto.com/images/blog/201903/20/b5d0fb31b5bc696de7a8a06a9c856c63.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

文中的模板已经上传到GitHub，访问链接获取
> https://github.com/zhouhua-amei/zabbix/  



-----
欢迎各位关注个人公众号"没有故事的陈师傅"
