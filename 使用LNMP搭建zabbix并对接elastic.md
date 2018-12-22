### 安装zabbix-server
#### 添加zabbix存储库
```
rpm -ivh https://repo.zabbix.com/zabbix/4.0/rhel/7/x86_64/zabbix-release-4.0-1.el7.noarch.rpm
yum -y install yum-utils
yum-config-manager --enable rhel-7-server-optional-rpm
```
#### 安装zabbix-server  zabbix-web
```
yum install zabbix-server-mysql
yum install zabbix-web-mysql
```
### 安装MySQL5.7数据库
#### 卸载mariadb包
```
rpm -qa |grep mariadb    #查看当前安装的mariadb的包
rpm -e --nodeps mariadb-libs-5.5.52-1.el7.x86_64     #卸载mariadb的包
```
#### 下载并解压MySQL源码包
```
wget https://dev.mysql.com/get/archives/mysql-5.7/mysql-5.7.21-linux-glibc2.12-x86_64.tar.gz  #从官网下载源码包
tar -xzvf  mysql-5.7.21-linux-glibc2.12-x86_64.tar.gz     #解压源码包
mv  mysql-5.7.21-linux-glibc2.12-x86_64  /usr/local/mysql
```
#### 创建MySQL用户并对MySQL文件进行授权
```
groupadd mysql   --创建mysql用户组
useradd -r -g mysql mysql     --创建mysql用户并添加到mysql用户组中
chown -R mysql.mysql mysql/  --将mysql目录访问权限赋为myql用户
```
#### 创建MySQL配置文件
```
cat >>/etc/my.cnf  <<EOF   #写入配置文件
[client]
port = 3306
socket = /tmp/mysql.sock
[mysqld]
character_set_server=utf8
init_connect='SET NAMES utf8'
basedir=/usr/local/mysql
datadir=/usr/local/mysql/data
socket=/tmp/mysql.sock
log-error=/var/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid
#不区分大小写
lower_case_table_names = 1
sql_mode=STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
max_connections=5000
default-time_zone = '+8:00‘
EOF
```
#### 初始化数据库
```
touch /var/log/mysqld.log    #创建日志文件并授权
chmod 777 /var/log/mysqld.log
chown mysql.mysql mysqld.log
/usr/local/mysql/bin/mysqld   --initialize --user=mysql   --basedir=/usr/local/mysql --datadir=/usr/local/mysql/data
```
#### 查看初始化密码
```
cat /var/log/mysqld.log|grep root@localhost
```
#### 执行如下操作开启MySQL服务，并设置相应权限
```
mkdir /var/run/mysqld
touch /var/run/mysqld/mysqld.pid
chmod -R 777 /var/run/mysqld
chown -R mysql.mysql /var/run/mysqld
/usr/local/mysql/support-files/mysql.server start  #启动MySQL
```
#### 修改MySQL密码
vim /etc/my.cnf   #修改配置文件
```
skip-grant-tables    #跳过密码认证
default_password_lifetime=360    #修改密码超时时间
不然修改密码之后密码会过期，会提示让你重新设置密码
You must reset your password using ALTER USER statement before executing this statement.
/usr/local/mysql/bin/mysql -uroot -p        #登录MySQL
use mysql    #切换MySql数据库
update mysql.user set authentication_string =password('root'), host = '%' where user = 'root';   #修改MySQL密码
flush privileges;
```
#### 将MySQL加入环境变量
```
echo 'PATH=/usr/local/mysql/bin:$PATH' >>/etc/profile      #将MySQL二进制文件加入环境变量
ln -s usr/local/mysql/support-files/mysql.server /usr/local/mysql/bin/    将MySQL的启动文件软连接到MySQL的环境变量中
```
#### 进入数据库并创建zabbix数据库以及创建授权用户
```
mysql>  create database zabbix character set utf8 collate utf8_bin;
mysql> grant all privileges on zabbix.* to zabbix@localhost identified by 'zabbix'；
mysql> flush privileges;
```
#### 编辑zabbix-server配置文件
修改以下参数为创建数据库时的信息，并重启zabbix-server
vim /etc/zabbix/zabbix_server.conf
```
DBName=zabbix
DBHost=192.168.179.132
DBUser=zabbix
DBPassword=zabbix
systemctl enable zabbix-server
systemctl start zabbix-server
```
启动的时候启动失败，查看系统日志，查找关键词
```
usr/sbin/zabbix_server: error while loading shared libraries: libmysqlclient.so.18: cannot open shared object file: No such file or directory
```
原来是缺少一个文件，yum安装解决
`yum -y install mysql-libs`
#### 将初始数据导入MySQL中
```
zcat /usr/share/doc/zabbix-server-mysql*/create.sql.gz | mysql -uzabbix -p zabbix
```
### 安装Nginx
#### 关掉防火墙和selinux 
```
systemctl stop firewalld
systemctl disable firewalld
sed -i 's/SELINUX=enforcing/SELINUX=disable/g' /etc/selinux/config
```
#### 安装依赖
```
yum -y install wget vim lsof lrzsz pcre-devel zlib-devel make gd-devel libjpeg-devel libpng-devel libxml2-devel bzip2-devel libcurl-devel libmcrypt libmcrypt-devel mcrypt mhash net-snmp-devel
yum -y install gcc bison bison-devel openssl-devel readline-devel libedit-devel sqlite-devel freetype freetype-devel libevent-devel mysql-devel
```
#### 配置Nginx的yum仓库
```
cat >>/etc/yum.repos.d/nginx.repo <<EOF
[nginx]
name=nginx.repo
baseurl=http://nginx.org/packages/centos/7/$basearch/
gpgcheck=0
enabled=1
skip_if_unavailable = 1
keepcache = 0
EOF
```
#### 启动Nginx
```
nginx -t  测试配置是否有错
systemctl start nginx
systemctl enable nginx
```
### 安装PHP
#### 添加PHP用户
`useradd -s /sbin/nologin php-fpm`
#### 安装PHP依赖库
```
yum install -y gcc gcc-c++ make zlib zlib-devel pcre pcre-devel libjpeg libjpeg-devel libpng libpng-devel freetype freetype-devel libxml2 libxml2-devel glibc glibc-devel glib2 glib2-devel bzip2 bzip2-devel ncurses ncurses-devel curl curl-devel e2fsprogs e2fsprogs-devel krb5 krb5-devel openssl openssl-devel openldap openldap-devel nss_ldap openldap-clients openldap-servers
```
#### 编译安装php
```
wget http://mirrors.sohu.com/php/php-7.2.6.tar.gz
tar zxvf php-7.2.6.tar.gz
cd php-7.2.6
./configure --prefix=/usr/local/php --with-config-file-path=/usr/local/php/etc --enable-fpm --with-fpm-user=php-fpm --with-fpm-group=php-fpm --with-mysql=mysqlnd  --with-pdo-mysql=mysqlnd --with-mysqli=mysqlnd --with-libxml-dir --with-gd --with-jpeg-dir --with-png-dir --with-freetype-dir --with-iconv-dir --with-zlib-dir --with-mcrypt --enable-soap --enable-gd-native-ttf --enable-ftp --enable-mbstring --enable-exif --disable-ipv6 --with-pear --with-curl --enable-bcmath --enable-mbstring --enable-sockets --with-gd --with-libxml-dir=/usr/local --with-gettext
make && make install
echo $? #每执行完上条命令就运行一下，如果返回0，则执行成功
cp php.ini-production /usr/local/php/etc/php.ini
```
#### 更改PHP配置文件
```
sed -i 's/post_max_size = 8M/post_max_size = 32M/g' /usr/local/php/etc/php.ini
sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 50M/g' /usr/local/php/etc/php.ini
sed -i 's/;date.timezone =/date.timezone =PRC/' /usr/local/php/etc/php.ini
sed -i 's/max_execution_time = 30/max_execution_time = 600/g' /usr/local/php/etc/php.ini
sed -i 's/max_input_time = 60/max_input_time = 600/g' /usr/local/php/etc/php.ini
sed -i 's/memory_limit = 128M/memory_limit = 256M/g' /usr/local/php/etc/php.ini
```
#### 启动php-fpm
```
cp /usr/local/php/etc/php-fpm.conf.default /usr/local/php/etc/php-fpm.conf
cp /usr/local/php/etc/php-fpm.d/www.conf.default  /usr/local/php/etc/php-fpm.d/www.conf
/usr/local/php/sbin/php-fpm -c /usr/local/php/etc/php.ini -y /usr/local/php/etc/php-fpm.conf
```
vim phpinfo.php
```
<?php
phpinfo();
?>
```
测试是否能连接nginx，这里出现一个错误，访问动态页面一直显示文件没有发现，修改nginx配置文件的PHP脚本路径变量和修改文件权限后一直没有用，后来我将路径的变量去掉，添加网站真实路径后解决

![](http://i2.51cto.com/images/blog/201812/22/c22be03880286ecb2b5f0fca2241a988.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
### 安装zabbix-agent
```
yum install zabbix-agent
vim /etc/zabbix/zabbix-agentd.conf     #Server和ServerActive分别代表zabbix的被动模式和主动模式，这里都填server端的IP
最后一行是开启脚本采集数据
```
![](http://i2.51cto.com/images/blog/201812/22/6a453336a86a21df49bb85fab7c44465.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
### 安装zabbix-web
#### 将zabbix的php源文件拷贝到网站目录上
```
cp -r /usr/share/zabbix/.* /usr/share/nginx/html/
```
#### 修改nginx配置
egrep -v '(^.*#|^$)' /etc/nginx/conf.d/default.conf
```
server {
    listen       80;
    server_name  192.168.179.132;
    access_log  /var/log/nginx/host.access.log  main;
    location / {
       root   /usr/share/nginx/html;
       index  index.html index.htm index.php;
    }
    error_page  404              /404.html;
    location ~ \.php$ {
        root           html;
        fastcgi_pass   127.0.0.1:9000;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME  /usr/share/nginx/html$fastcgi_script_name;
        include        fastcgi_params;
	
    }
}
```
重启nginx访问会报这个错
![](http://i2.51cto.com/images/blog/201812/22/71827edbecc7603594797229c93f708e.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
百度之后得知是权限不足引起的，运行一下命令可以解决，这里一定要777，不然到时候安装完成不能创建配置文件
```
chmod -R 777 /etc/zabbix/web
```
在访问浏览器的时候不出图，请教我学长之后得出是因为nginx上配置了图片缓存，去掉缓存解决

#### 访问192.168.179.132/index.php安装zabbix-web
![](http://i2.51cto.com/images/blog/201812/22/131e24ea6ab369a41548385e7dfca88d.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
![](http://i2.51cto.com/images/blog/201812/22/75c7b18db89872244730618ec8b6ae2b.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
安装完成可能会遇到连接不上zabbix-server的错误，查看zabbix-server日志如下，这个解决方法有两种，第一种就是创建一个mysql.sock然后重启mysql服务器
```
mkdir /var/lib/mysql
ln -s /tmp/mysql.sock /var/lib/mysql/mysql.sock
```
第二种就是编辑zabbix_server.conf文件，将DBSocket修改为自己数据库的mysql.sock,然后重启 zabbix_server
![](http://i2.51cto.com/images/blog/201812/22/ef87718cf7eb2ce4d66316833261e58b.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
### 监控zabbix 本机的CPU idle
监控CPU idle
基本就是图形界面，创建监控项之前先测试一下key值是否可用，当然需要安装zabbix_get工具，使用yum install zabbix-get来安装
```
zabbix_get -s 192.168.179.132 -k system.cpu.util[all,idle,avg1]
```
![](http://i2.51cto.com/images/blog/201812/22/7b721127f982e1c282281addd30daaee.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
### 自建模板监控磁盘IO
监控磁盘IO利用的工具是iostat
yum install -y sysstat
#### 首先zabbix-agent端要开启允许脚本收集监控数据
编辑zabbix-agent的配置文件
vim /etc/zabbix/zabbix_agentd.d/userparameter.conf
```
UserParameter=disk.status[*],/usr/local/zabbix/scripts/disk-status.sh $1
```
#### 编写收集脚本
vim /usr/local/zabbix/scripts/disk-status.sh
```sh
#!/bin/bash 
if [ $# -ne 1 ];then
        echo "Follow the script name with an argument" 
fi

case $1 in

        rrqm)
                iostat -dxk 1 1|grep -w sda |awk '{print $2}'
                ;;
        wrqm)
                iostat -dxk 1 1|grep -w sda |awk '{print $3}'
                ;;
        rps)
                iostat -dxk 1 1|grep -w sda|awk '{print $4}'
                ;;
        wps)
                iostat -dxk 1 1|grep -w sda |awk '{print $5}'
                ;;
        rKBps)
                iostat -dxk 1 1|grep -w sda |awk '{print $6}'
                ;;
        wKBps)
                iostat -dxk 1 1|grep -w sda |awk '{print $7}'
                ;;
        avgrq-sz)
                iostat -dxk 1 1|grep -w sda |awk '{print $8}'
                ;;
        avgqu-sz)
                iostat -dxk 1 1|grep -w sda |awk '{print $9}'
                ;;
        await)
     		iostat -dxk 1 1|grep -w sda|awk '{print $10}'
                ;;
        svctm)
                iostat -dxk 1 1|grep -w sda |awk '{print $13}'
                ;;
        util)
                iostat -dxk 1 1|grep -w sda |awk '{print $14}'
                ;;
        *)
                echo -e "\e[033mUsage: sh $0 [rrqm|wrqm|rps|wps|rKBps|wKBps|avgqu-sz|avgrq-sz|await|svctm|util]\e[0m"
esac
```
touch +x /usr/local/zabbix/scripts/disk-status.sh   #给脚本添加执行权限
#### 打开zabbix-web，创建模板
浏览器打开192.168.179.132/index.php
依次点击配置——>模板——>创建模板
添加模板名称以及群组，最后点击添加
![](http://i2.51cto.com/images/blog/201812/22/7d1a9ec810d43fd3ac3b96035e614462.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 创建应用集
在创建的模板上点击创建应用集，名字最好与磁盘io相关
![](http://i2.51cto.com/images/blog/201812/22/3afd023482262bb9e0d5efb104c419e9.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 创建监控项
这里所有的数据类型都是浮点数
![](http://i2.51cto.com/images/blog/201812/22/b0b7be9592f230d84b4af20d3d836c7a.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
![](http://i2.51cto.com/images/blog/201812/22/422898faaa5e65124708ec372a778a1a.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 创建图形
这需要为每一个监控项都创建图形
![](http://i2.51cto.com/images/blog/201812/22/0cb47b32e68157b2d31986d9b3fb6b03.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 为需要监控的主机链接模板
点击需要监控的主机，然后单击模板，为主机添加模板链接
![](http://i2.51cto.com/images/blog/201812/22/b907c205e6f11ddab034b94205e82d99.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
![](http://i2.51cto.com/images/blog/201812/22/362c7670800766f29834777ea1fdf065.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 解决图形名字乱码问题
可以看到我收集到的图形是乱码的
首先查看zabbix字体目录，它定义的路径是“fonts”，它是一个相对路径，绝对路径为/usr/share/zabbix/fonts，
vim /usr/share/zabbix/include/defines.inc.php //搜索ZBX_FONTPATH
![](http://i2.51cto.com/images/blog/201812/22/932e09e8b21bbf94e7c00e2aa1beb43a.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
而字体文件为“ZBX_GRAPH_FONT_NAME”所定义的“graphfont”，它是一个文件，绝对路径为/usr/share/zabbix/fonts/graphfont.ttf
我们可以从Windows系统中选择一个中文字体然后放到zabbix的字体目录下
Windows字体目录位于C:\Windows\Fonts下，找到仿宋常规字体将他拷入zabbix字体目录下
然后修改PHP文件，将字体文件修改为simsong
![](http://i2.51cto.com/images/blog/201812/22/81e28a872b25a4a0145869b6b837346f.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
### 安装elastic6.1
#### 下载源码包并解压，修改es配置
```
yum install java    #elastic需要安装Java依赖
curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.1.4.tar.gz
tar -xvf elasticsearch-6.1.4.tar.gz
```
vim /root/elasticsearch-6.1.4/config/elasticsearch.yml   #主要修改es的一些配置信息
![](http://i2.51cto.com/images/blog/201812/22/f8409627b383f3bfd8c0ebc759e07e9f.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
启动过程出现的报错
```
[WARN ][o.e.b.BootstrapChecks    ] [PWm-Blt] max file descriptors [4096] for elasticsearch process is too low, increase to at least [65536]
```
解决办法：
vim /etc/security/limits.conf 
```
* soft nofile 65536
* hard nofile 131072
* soft nproc 2048
* hard nproc 4096
```
```
[WARN ][o.e.b.BootstrapChecks    ] [PWm-Blt] max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
```
解决办法：
vim /etc/sysctl.conf
`vm.max_map_count=655360`
修改完成执行命令：
sysctl -p
cd elasticsearch-6.1.4/bin
这里不能使用root用户运行elastic，可以自己新建一个普通用户，还要把目录授予普通用户权限
./elasticsearch
然后我们可以打开浏览器输入192.168.179.133:9200可以查看es的状态，或者可以装一个head插件
### 安装head插件
#### 安装node.js
这里我采用的源码安装，其实二进制安装是比较简单的，但我执行到最后node的二进制文件无法执行，因此只能源码安装，时间有点长，打了两局王者荣耀才装完
```bash
yum groupinstall "Development Tools"    #安装编译必要的工具
wget https://nodejs.org/dist/v8.11.4/node-v8.11.4.tar.gz  #下载node的源码包
tar -zxvf node-v8.11.4.tar.gz             #解压源码包
cd node-v8.11.4
./configure && make && make install             #执行编译安装
echo $?    #查看执行结果，输出0表示安装成功
```
node.js默认安装路径在/usr/local/bin/目录下

#### 安装grunt
grunt是基于Node.js的项目构建工具，可以进行打包压缩、测试、执行等等的工作，head插件就是通过grunt启动
`npm install -g grunt-cli`
#### 下载并安装head插件
```bash
git clone git://github.com/mobz/elasticsearch-head.git       #克隆head插件仓库
cd elasticsearch-head/
npm install          #执行完会报一些错误，不要管执行下一条命令就会解决
npm install phantomjs-prebuilt@2.1.14 --ignore-scripts
```
#### 修改elasticsearch的配置
vim /elasticsearch/elasticsearch-6.4.0/config/elasticsearch.yml 
```
http.cors.enabled: true                                    # elasticsearch中启用CORS
http.cors.allow-origin: "*"                                 # 允许访问的IP地址段，* 为所有IP都可以访问
```
#### 启用head插件并在浏览器上打开
npm run start    #启动head插件
在浏览器输入http://192.168.179.133:9100/ 即可使用head插件
### 使用es存储zabbix的历史数据
#### 修改/etc/zabbix/zabbix_server.conf
添加如下内容
```
HistoryStorageURL=192.168.179.133:9200
HistoryStorageTypes=str,text,log,uint,dbl
HistoryStorageDateIndex=1
```
#### 修改/etc/zabbix/web/zabbix.conf.php
添加如下内容
```
global $DB, $HISTORY;
$HISTORY['url']   = 'http://192.168.179.133:9200';
// Value types stored in Elasticsearch.
$HISTORY['types'] = ['str', 'text', 'log','uint','dbl'];
```
![](http://i2.51cto.com/images/blog/201812/22/7e12d7a1ded4d024ef1a111001b2be1c.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
#### 修改完成后重启zabbix,并查看zabbix是否有数据
`systemctl restart zabbix-server`
![](http://i2.51cto.com/images/blog/201812/22/f9f2abb28c4bd2b1fa464e802bf7b7ab.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
至此，es收集zabbix历史数据完成

