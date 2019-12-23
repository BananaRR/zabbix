#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests,time
import json,sys,re,os



zabbixserver_url ='http://192.168.99.200/index.php'
pname_path='http://47.103.14.52/dingding_pic/'
host='192.168.99.200'
def get_itemid():
    #a=re.findall(r"ITEM ID: \d+",info2)
    #i=str(a)
    #itemid=re.findall(r"\d+",i)
    itemid=re.search(r'ITEM ID:(\d+)',sys.argv[2]).group(1)
    #return int("".join(itemid).lstrip('[\'').rstrip('\']'))
    print(itemid)
    return itemid
def get_picture(itemid,pname):
    myRequests = requests.Session()
    try:
        loginHeaders = {
            "Host":host,            
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"  
        }
        # 构建登录所需的信息
        playLoad = {
            "name": "Admin",
            "password": 'zabbix',
            "autologin": "1",
            "enter": "Sign in",
        }
        myRequests.post(url=zabbixserver_url, headers=loginHeaders, data=playLoad)
        testUrl = "http://192.168.99.200/chart.php"
        testUrlplayLoad = {
           "from": "now-10m",
           "to": "now",
           "itemids": itemid,
           "width": "700",
        }
        testGraph =  myRequests.get(url=testUrl,params=testUrlplayLoad)
        IMAGEPATH = os.path.join('/usr/lib/zabbix/alertscripts/dingding_pic/', pname)
        with open(IMAGEPATH,'wb') as f:
            f.write(testGraph.content)
            #将获取到的图片数据写入到文件中去
        #return graph_name 
        #f = open(IMAGEPATH,'wb')
        #f.write(testGraph.content)
        #f.close()
        #pname = 'D:/zyypython/' + pname
        os.system("sudo scp %s root@47.103.14.52:/usr/share/nginx/html/dingding_pic" %IMAGEPATH) 
        pname_url = pname_path+pname
        
        return pname_url
    except Exception as e:
        print(e)
        return False


def send_msg(pname_url,info3):
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    print(info3)
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": info1,
            "text": "通知:\n"+info3+"![screenshot](%s)\n"%(pname_url)
                
        },
        "at":{
            "atMobiles": reminders,
            "isAtAll": False,
        },
        }
    r = requests.post(url=webhook_url,json=data,headers=headers)
    print(r.text)
def info_text():
    new_text = ""
    x = info2.split('\n')
    for i in x:
        if re.search('ITEM ID',str(i)):
            pass
        else:
            new_text+="- "+str(i)+('\n')
    print(type(new_text)) 
    return new_text

if __name__ == '__main__':
    os.system("echo hello > /tmp/syslog.md")   
    pname = str(int(time.time()))+'.png'
    info1 = str(sys.argv[1])
    info2 = str(sys.argv[2])
    info3 = info_text()
    
    with open('/tmp/syslog.md','a') as f:
        f.write(info1)
        f.write(info2)
        #f.writelines(sys.argv[1])
        #f.writelines(sys.argv[2])
        f.close()
    reminders = []
    webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=771ded387e6be652c51a2b6c83cade4e048e3da4fdfe128f1db6b124b87df18a'
    itemid = get_itemid()
    print(itemid)       
    pname_url=get_picture(itemid,pname)
    print(pname_url)
    send_msg(pname_url,info3)
