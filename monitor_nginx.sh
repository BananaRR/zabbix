#/bin/bash
ping() {
    /sbin/pidof nginx | wc -l
}
active(){
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
