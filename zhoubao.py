#coding=utf-8
import requests,json,codecs,datetime,time,pandas
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr
from smtplib import SMTP
import smtplib
ApiUrl = 'http://192.168.1.2/api_jsonrpc.php'
header = {"Content-Type":"application/json"}
user="Admin"
password="zabbix"
x=(datetime.datetime.now()-datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
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

def getevent(auth,timestamp):
    data={
        "jsonrpc": "2.0",
        "method": "event.get",
        "params": {
            "output": [
                "name",
                "severity"
            ],
            "value":1,
            "time_from":timestamp[0],
            "time_till":timestamp[1],
            "selectHosts":[
                #"hostid",
                "name"
            ]
        },
        "auth": auth,
        "id": 1
    }
    getevent=requests.post(url=ApiUrl,headers=header,json=data)
    triname=json.loads(getevent.content)['result']
    triggers=[]
    a={}
    for i in triname:
        triggers.append(i['name'])
    for i in triggers:
        a[i]=triggers.count(i)
    #for i in triname:
    #    i['count']=a[i['name']]
    
    list2=[]
    print(triname)
    #print(a)
    for key in a:
        b={}
        b['name']=key
        b['host']=[i['hosts'][0]['name'] for i in triname if i['name']==key][0]
        b['severity']=[i['severity'] for i in triname if i['name']==key][0]
        b['count']=a[key]
        list2.append(b)
        
    # host=[i['host'] for i in list2]
    # name=[i['name'] for i in list2]
    # severity=[i['severity'] for i in list2]
    # count=[i['count'] for i in list2]
    # result=[]
    # result.append(host)
    # result.append(name)
    # result.append(severity)
    # result.append(count)
    #print(result)
    #return result
    return list2
def convertohtml(result):
    d = {}
    title=['主机','触发器','告警级别','告警次数']
    index = 0
    for t in title:
        d[t]=result[index]
        index = index+1
    df = pandas.DataFrame(d)
    df = df[title]
    h = df.to_html(index=False)
    return h
def datatohtml(list2):
    tables = ''
    for i in range(len(list2)):
        name,host,severity,count = list2[i]['name'], list2[i]['host'], list2[i]['severity'], list2[i]['count']
        td = "<td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td>"%(name, host, severity, count)
        tables = tables + "<tr>%s</tr>"%td
    base_html="""
    <!DOCTYPE html>
    <html>
    <head> 
    <meta charset="utf-8"> 
    <title>zabbix监控告警</title> 
    </head>
    <body>
    <table width="900" border="0">
    <tr>
    <td colspan="2" style="background-color:#FFA500;">
    <h4>告警级别: 1 表示:信息 2 表示:告警 3 表示:一般严重 4 表示:严重 5 表示:灾难</h4>
    </td>
    </tr>
    <tr>
    <td style="background-color:#FFD700;width:100px;">
    <TABLE BORDER=1><TR><TH>主机</TH><TH>触发器</TH><TH>告警级别</TH><TH>告警次数</TH></TR>%s</TABLE>
    </td>
    </tr>
    <tr>
    <td colspan="2" style="background-color:#FFA500;text-align:center;">
    zabbix告警统计</td>
    </tr>
    </table>
    </body>
    </html>
    """ %tables
    return base_html
def sendmail(base_html):
    from_addr = 'wanger@qq.com'
    password = '没有故事的陈师傅'
    to_addr = 'wanger@163.com'
    smtp_server = 'smtp.qq.com'

    msg = MIMEText(base_html, 'html', 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = Header('Zabbix本周监控报表', 'utf-8').encode()
    
    try:
        server=SMTP(smtp_server,"25")   #创建一个smtp对象
        #server.starttls()    #启用安全传输模式
        server.login(from_addr,password)  #邮箱账号登录
        server.sendmail(from_addr,to_addr,msg.as_string())  #发送邮件  
        server.quit()   #断开smtp连接
    except smtplib.SMTPException as a:
        print (a)
auth=gettoken()
timestamp=timestamp(x,y)
getevent=getevent(auth,timestamp)
base_html=datatohtml(getevent)
sendmail(base_html)
logout(auth)
