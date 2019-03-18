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
#MYSQL_CONN="/usr/local/mysql/bin/mysqladmin "
# 参数是否正确
#if [ $# -ne "1" ];then 
 #   echo "arg error!" 
#fi 

while true
do
  for vargs in Uptime Com_update Slow_queries Com_select Com_rollback Questions Com_insert Com_delete Com_commit Bytes_sent Bytes_received Com_begin;do
	i="/monitor_mysql/${vargs}.txt"
	case $vargs in 
    	  Uptime) 
        	result=`${MYSQL_CONN} status|cut -f2 -d":"|cut -f1 -d"T"` 
        	echo $result >$i
         	;; 
       	  Com_update) 
          	result=`${MYSQL_CONN} extended-status |grep -w "Com_update"|cut -d"|" -f3` 
        	echo $result >$i
        	;; 
    	  Slow_queries) 
        	result=`${MYSQL_CONN} status |cut -f5 -d":"|cut -f1 -d"O"` 
        	echo $result >$i
        	;; 
    	  Com_select) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Com_select"|cut -d"|" -f3` 
        	echo $result >$i
                ;; 
    	  Com_rollback) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Com_rollback"|cut -d"|" -f3` 
                echo $result >$i
                ;; 
    	  Questions) 
        	result=`${MYSQL_CONN} status|cut -f4 -d":"|cut -f1 -d"S"` 
                echo $result >$i
                ;; 
    	  Com_insert) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Com_insert"|cut -d"|" -f3` 
                echo $result >$i
                ;; 
    	  Com_delete) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Com_delete"|cut -d"|" -f3` 
                echo $result >$i
                ;; 
    	  Com_commit) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Com_commit"|cut -d"|" -f3` 
                echo $result >$i
                ;; 
    	  Bytes_sent) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Bytes_sent" |cut -d"|" -f3` 
                echo $result >$i
                ;; 
    	  Bytes_received) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Bytes_received" |cut -d"|" -f3` 
                echo $result >$i
                ;; 
    	  Com_begin) 
        	result=`${MYSQL_CONN} extended-status |grep -w "Com_begin"|cut -d"|" -f3` 
                echo $result >$i
                ;; 

          *) 
        	echo "Usage:$0(Uptime|Com_update|Slow_queries|Com_select|Com_rollback|Questions|Com_insert|Com_delete|Com_commit|Bytes_sent|Bytes_received|Com_begin)" 
        	;; 
	esac
      
  done
      /usr/local/mysql/bin/mysqladmin  -uroot -proot ping |grep -c alive >/monitor_mysql/ping.txt
      ping=`cat /monitor_mysql/ping.txt`
      if [ $ping == "" ];then
	echo 0 >/monitor_mysql/ping.txt
      else
     	echo $ping >/monitor_mysql/ping.txt
      fi
sleep 600
done

