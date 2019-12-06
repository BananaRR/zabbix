#coding=utf-8
import requests,json,csv,codecs,datetime,time
ApiUrl = 'http://192.168.99.50/zabbix/api_jsonrpc.php'
header = {"Content-Type":"application/json"}
user="Admin"
password="zabbix"
csvheader=['Hostname','IP','磁盘C:Total(B)','磁盘最大C:Used(B)','内存Total(B)','内存最大Used(B)','内存平均used(B)','CPU负载最大值','CPU负载平均值','CPU 核数','clock']
x=(datetime.datetime.now()-datetime.timedelta(minutes=120)).strftime("%Y-%m-%d %H:%M:%S")
y=(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
def gettoken():
    data = {"jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": user,
                    "password": password
                },
                "id": 1,
                "auth": None
            }
    auth=requests.post(url=ApiUrl,headers=header,json=data)
    return json.loads(auth.content)['result']
def timestamp(x,y):
    p=time.strptime(x,"%Y-%m-%d %H:%M:%S")
    starttime = str(int(time.mktime(p)))
    q=time.strptime(y,"%Y-%m-%d %H:%M:%S")
    endtime= str(int(time.mktime(q)))
    return starttime,endtime
def logout(auth):
    data={
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": 1,
            "auth": auth
            }
    auth=requests.post(url=ApiUrl,headers=header,json=data)
    return json.loads(auth.content)
def get_hosts(groupids,auth):
    data ={
            "jsonrpc": "2.0",
             "method": "host.get",
             "params": {
             "output": [ "name"],
             "groupids": groupids,
             "filter":{
                 "status": "0"
             },
             "selectInterfaces": [   
                        "ip"
                    ],
            },
            "auth": auth,  # theauth id is what auth script returns, remeber it is string
            "id": 1
        }
    gethost=requests.post(url=ApiUrl,headers=header,json=data)
    return json.loads(gethost.content)["result"]
def gethist(hosts,auth,timestamp):
    #item1=[]
    host=[]
    print(hosts)
    for i in hosts:
        item1=[]
        item2=[]
        #print(i)
        dic1={}
        for j in ['vfs.fs.size[C:,total]','vm.memory.size[total]','system.cpu.num']:
            data={
                "jsonrpc": "2.0",
                "method": "item.get",
                "params": {
                    "output": [
                        "itemid"
                          
                    ],
                    "search": {
                        "key_": j  
                    },
                    "hostids": i['hostid']
                },
                "auth":auth,
                "id": 1
            }
            getitem=requests.post(url=ApiUrl,headers=header,json=data)
            item=json.loads(getitem.content)['result']
            
            hisdata={
                "jsonrpc":"2.0",
                "method":"history.get",
                "params":{
                    "output":"extend",                    
                    "time_from":timestamp[0],
                    #"time_till":timestamp[1],
                    "history":0,
					"sortfield": "clock",
                    "sortorder": "DESC",
                    "itemids": '%s' %(item[0]['itemid']),
                    "limit":1
                },
                "auth": auth,
                "id":1
                }
            gethist=requests.post(url=ApiUrl,headers=header,json=hisdata)
            hist=json.loads(gethist.content)['result']
            item1.append(hist)
        for j in ['vfs.fs.size[C:,used]','vm.memory.size[used]','system.cpu.load']:
            data={
                "jsonrpc": "2.0",
                "method": "item.get",
                "params": {
                    "output": [
                        "itemid"
                           
                    ],
                    "search": {
                        "key_": j  
                    },
                    "hostids": i['hostid']
                },
                "auth":auth,
                "id": 1
            }
            getitem=requests.post(url=ApiUrl,headers=header,json=data)
            item=json.loads(getitem.content)['result']
            
            trendata={
                "jsonrpc":"2.0",
                "method":"trend.get",
                "params":{
                    "output": [
                        "itemid",
                        "value_max",
                        "value_avg"
                    ],                    
                    "time_from":timestamp[0],
                    "time_till":timestamp[1],
                    "itemids": '%s' %(item[0]['itemid']),
                    "limit":1
                },
                "auth": auth,
                "id":1
                }
            gettrend=requests.post(url=ApiUrl,headers=header,json=trendata)
            trend=json.loads(gettrend.content)['result']
            item2.append(trend) 
        print(item1) 
        print(item1)
        dic1['Hostname']=i['name']
        dic1['IP']=i['interfaces'][0]['ip']
        dic1['磁盘C:Total(B)']=round(float(item1[0][0]['value'])/1024**3,2)
        dic1['磁盘最大C:Used(B)']=round(float(item2[0][0]['value_max'])/1024**3,2)
        dic1['内存Total(B)']=round(float(item1[1][0]['value'])/1024**3,2)
        dic1['内存最大Used(B)']=round(float(item2[1][0]['value_max'])/1024**3,2)
        dic1['内存平均used(B)']=round(float(item2[1][0]['value_avg'])/1024**3,2)
        dic1['CPU负载最大值']=item2[2][0]['value_max']
        dic1['CPU负载平均值']=item2[2][0]['value_avg']
        dic1['CPU 核数']=item1[2][0]['value']
        x = time.localtime(int(item1[2][0]['clock']))
        item1[2][0]['clock'] = time.strftime("%Y-%m-%d %H:%M:%S", x)
        dic1['clock']=item1[2][0]['clock']
        host.append(dic1)  
        print(item)
    print(host)
    return host       
def writecsv(getitem1):
    with open('data.csv','w',encoding='utf-8-sig') as f:
        #f.write(codecs.BOM_UTF8)
        writer = csv.DictWriter(f,csvheader)
        writer.writeheader()

        for row in getitem1:
            writer.writerow(row)
token=gettoken()
timestamp=timestamp(x,y)
gethost=get_hosts(6,token)
gethist=gethist(gethost,token,timestamp)
writecsv=writecsv(gethist)
logout(token)

