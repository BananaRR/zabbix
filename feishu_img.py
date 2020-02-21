import requests,json,sys,re,time,os
mobiles=sys.argv[1]
subject=sys.argv[2]
messages=sys.argv[3]
# mobiles="15101171027"
# messages="test"
# subject="test"
user='Admin'    #定义zabbix用户名
password='zabbix'    #定义zabbix用户密码
graph_path='/usr/lib/zabbix/alertscripts/graph'   #定义图片存储路径
graph_url='http://192.168.99.2/chart.php'     #定义图表的url
host="192.168.99.2"
loginurl="http://192.168.99.2/index.php"          #定义登录的url
image_path=r"C:\Users\Administrator\Desktop\4.png"
def get_itemid():
    #获取报警的itemid
    itemid=re.search(r'ITEM ID:(\d+)',sys.argv[3]).group(1)
    return itemid
def gettenant_access_token():
    tokenurl="https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    headers={"Content-Type":"application/json"}
    data={
        "app_id":"cli_9ec62123e80b5d00e",
        "app_secret":"f716Gi27Yi25n5wertaKpfrty0j81ujl"

    }
    request=requests.post(url=tokenurl,headers=headers,json=data)
    response=json.loads(request.content)['tenant_access_token']
    return response
def getuserid(tenant_access_token):
    #mobiles="15101171027"
    userurl="https://open.feishu.cn/open-apis/user/v1/batch_get_id?mobiles=%s"%mobiles
    headers={"Authorization":"Bearer %s"%tenant_access_token}
    request=requests.get(url=userurl,headers=headers)
    response=json.loads(request.content)['data']['mobile_users'][mobiles][0]['user_id']
    return response

def get_graph(itemid):
    #获取报警的图表并保存
    session=requests.Session()   #创建一个session会话
    try:
        loginheaders={            
        "Host":host,            
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
        #定义请求消息头
        
        payload = {            
        "name":user,
        "password":password,  
        "autologin":"1",            
        "enter":"Sign in",
        }
        #定义传入的data
        login=session.post(url=loginurl,headers=loginheaders,data=payload)
        #进行登录
        graph_params={
            "from" :"now-10m",
	        "to" : "now",           
            "itemids" : itemid,                       
            "width" : "400",
        }
        #定义获取图片的参数
        graph_req=session.get(url=graph_url,params=graph_params)
        #发送get请求获取图片数据
        time_tag=time.strftime("%Y%m%d%H%M%S", time.localtime())
        graph_name='baojing_'+time_tag+'.png'
        #用报警时间来作为图片名进行保存
        graph_name = os.path.join(graph_path, graph_name)
        #使用绝对路径保存图片
        with open(graph_name,'wb',) as f:
            f.write(graph_req.content)
            #将获取到的图片数据写入到文件中去
        
        return graph_name
    
    except Exception as e:        
        print (e)        
        return False

def uploadimg(tenant_access_token,graph_name):
    with open(graph_name,'rb') as f:
        image = f.read()
    imgurl='https://open.feishu.cn/open-apis/image/v4/put/'
    headers={'Authorization': "Bearer %s"%tenant_access_token}
    files={
            "image": image
        }
    data={
            "image_type": "message"
        }
    
    resp = requests.post(
        url=imgurl,
        headers=headers,
        files=files,
        data=data)
    resp.raise_for_status()
    content = resp.json()
    return content['data']['image_key']
    

def getchatid(tenant_access_token):
    #获取chatid
    chaturl="https://open.feishu.cn/open-apis/chat/v4/list?page_size=20"
    headers={"Authorization":"Bearer %s"%tenant_access_token,"Content-Type":"application/json"}
    request=requests.get(url=chaturl,headers=headers)
    response=json.loads(request.content)['data']['groups'][0]['chat_id']
    return response
def sendmes(user_id,chat_id,tenant_access_token,image_key=None):
    sendurl="https://open.feishu.cn/open-apis/message/v4/send/"
    headers={"Authorization":"Bearer %s"%tenant_access_token,"Content-Type":"application/json"}
    #向群里发送富文本消息
    data={
        "chat_id":chat_id,
        "msg_type":"post",
        "content":{
            "post":{
                "zh_cn":{
                    "title":subject,
                    "content":[
                        [
                        {
                            "tag": "text",
                            "un_escape": True,
                            "text": messages
                        },
                        {
                            "tag": "at",
                            "user_id": user_id

                        }
                    ],
                    [
                        {
                            "tag": "img",
                            "image_key": image_key,
                            "width": 500,
                            "height": 300
                        }
                    ]
                ]
            }
        }
    }
    }
    #向群里发送消息
    
    # data={"chat_id":chat_id,
    #     "msg_type":"text",
    #     "content":{
    #         "text":"%s<at user_id=\"%s\">test</at>"%(messages,user_id)
    #     }
    # }
    #给个人发送消息
    # data={"user_id":user_id,
    #     "msg_type":"text",
    #     "content":{
    #         "text":"%s<at user_id=\"%s\">test</at>"%(messages,user_id)
    #     }
    # }
    request=requests.post(url=sendurl,headers=headers,json=data)
    print(request.content)

itemid=get_itemid()
tenant_access_token=gettenant_access_token()
user_id=getuserid(tenant_access_token)
graph_name=get_graph(itemid)
chat_id=getchatid(tenant_access_token)
image_key=uploadimg(tenant_access_token,graph_name)
sendmes(user_id,chat_id,tenant_access_token,image_key=image_key)

