#!/usr/bin/python
#conding=utf-8
import requests,json,sys
mobiles=sys.argv[1]
subject=sys.argv[2]
messages=sys.argvp[3]
def gettenant_access_token():
    tokenurl="https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    headers={"Content-Type":"application/json"}
    data={
        "app_id":"cli_9ec6258e80b12340e",
        "app_secret":"f716Gi27Yi25n5K0WbaKpfrfsretgsg1ujl"

    }
    request=requests.post(url=tokenurl,headers=headers,json=data)
    response=json.loads(request.content)['tenant_access_token']
    return response
def getuserid(tenant_access_token):
    #mobiles="15101456278"
    userurl="https://open.feishu.cn/open-apis/user/v1/batch_get_id?mobiles=%s"%mobiles
    headers={"Authorization":"Bearer %s"%tenant_access_token}
    request=requests.get(url=userurl,headers=headers)
    response=json.loads(request.content)['data']['mobile_users'][mobiles][0]['user_id']
    return response
def getchatid(tenant_access_token):
    #获取chatid
    chaturl="https://open.feishu.cn/open-apis/chat/v4/list?page_size=20"
    headers={"Authorization":"Bearer %s"%tenant_access_token,"Content-Type":"application/json"}
    request=requests.get(url=chaturl,headers=headers)
    response=json.loads(request.content)['data']['groups'][0]['chat_id']
    return response
def sendmes(user_id,chat_id,tenant_access_token):
    #向群里发送消息
    sendurl="https://open.feishu.cn/open-apis/message/v4/send/"
    headers={"Authorization":"Bearer %s"%tenant_access_token,"Content-Type":"application/json"}
    data={"chat_id":chat_id,
        "msg_type":"text",
        "content":{
            "text":"%s<at user_id=\"%s\">test</at>"%(messages,user_id)
        }
    }
    #给个人发送消息
    # data={"user_id":user_id,
    #     "msg_type":"text",
    #     "content":{
    #         "text":"%s<at user_id=\"%s\">test</at>"%(messages,user_id)
    #     }
    # }
    request=requests.post(url=sendurl,headers=headers,json=data)
    print(request.content)


tenant_access_token=gettenant_access_token()
user_id=getuserid(tenant_access_token)
chat_id=getchatid(tenant_access_token)
sendmes(user_id,chat_id,tenant_access_token)
