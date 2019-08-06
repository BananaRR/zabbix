首次开通短信套餐包的腾讯云每月会赠送100条的免费短信数量，我们可以拿这100条短信进行测试
### 开通之后需要添加一个应用
![](https://s1.51cto.com/images/blog/201908/03/78fd3f758fb08f71fec1e1819af280b9.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

### 进入创建好的应用
这里需要记住应用的ID还有key，后面接入的时候需要用到
![](https://s1.51cto.com/images/blog/201908/03/009b19fa362fba3d6e20f609a214d690.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

### 创建应用签名以及模板
#### 单击创建签名
![](https://s1.51cto.com/images/blog/201908/03/07f43e7e16f59afbc48df27871013aa8.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

首先腾讯云只支持以下类型的签名，个人用的话可以使用自己已经备案的网站或者自己注册一个公众号，这里再说一下，阿里云的是不支持个人公众号的只能是企业号，由于我的网站还没备案，这里就只能使用公众号来认证了，使用公众号证明材料只需要公众号的后台截图就可以了，比其他类型的要方便，申请说明要写公众号的名字。不然审核不通过
![](https://s1.51cto.com/images/blog/201908/03/f3f05d0b3c1f00bbed63f6147c3259fe.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

#### 创建应用模板
模板内容使用{}作为变量，创建完模板之后会生成一个模板ID，这个后面接入的时候也会用到，由于个人用户单个模板变量最大长度不超过12个字符，因此需要多定义几个变量，最后用正则取出

> 注意：模板变量之间使用,分隔的话，那么在触发器里名字就不要包含,了，否则会发生转义，导致由于变量太长而发送短信失败  

![](https://s1.51cto.com/images/blog/201908/03/97f9168906e4b69db863f13d89eba366.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)
### 开始接入腾讯云短信服务
腾讯云支持多种语言的SDK和api，使用SDK会更加的方便一点，腾讯云的python SDK为qcloudsms_py，可以直接使用pip安装，腾讯云的SDK文档地址为：https://cloud.tencent.com/document/product/382/11672 ，因此我选择了使用api来接入，
由于腾讯的模板单个变量长度最长不能超过12个字符，且模板变量之间不能有空字符，所以我们需要在传入模板之前进行文本处理
#### 实现思路：
1. 将获取到的信息前五行进行正则匹配，因为前五行的内容比较短，方便处理，将"："与换行符之间的内容进行匹配，并添加到列表中
1. 将获取到的信息最后一行也就是事件信息进行正则匹配，由于内容比较长，所以需要将字符串分成五组，每组长度不超过十二个字符，并存放在列表中，将两个列表进行相加，并作为模板参数传给短信服务的api
1. 将传入列表中的元素作为参数post请求给api，平台发送短信  


#### 代码如下：  
```python  
#!/usr/bin/python3
#coding=utf-8
#author：wanger
import requests,re
import time,sys,json,hashlib,random

rand=random.randint(100000,999999)
mobile=sys.argv[1]
message=sys.argv[2]
message="""%s""" %message
times=time.time()
times=int(times)
tpl_id=225686
appkey='f545bc772b396c41df6da4c4442ce085'
raw_text="appkey={}&random={}&time={}&mobile={}".format(appkey,rand,times,mobile)
sig=hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
def rest(message):
    #获取报警内容，方便后续调试
    with open('/tmp/message','w',encoding='utf-8') as f:
         s=json.dump(message,f,ensure_ascii=False)
    res=re.findall(r'：(.*)\r\n',message,re.M)
    hostname=res[0]
    ip1=re.match(r'(\d+\.\d+)\.(.*)',res[1]).group(1)
    ip2=re.match(r'(\d+\.\d+)\.(.*)',res[1]).group(2)
    date1=re.match(r'(.*)-(.*)',res[2]).group(1)
    time1=re.match(r'(.*)-(.*)',res[2]).group(2) 
    level=res[3]
    id1=res[4]
    alert=[hostname,ip1,ip2,date1,time1,level,id1]
    #获取处理后的前五行内容，方便调试
    with open('tmp/messages','a',encoding='utf-8') as f:
         for i in alert:
             f.write(i)

    return alert
def remes(alert,message):
    res=re.search('报警信息：(.*)$',message).group(1)
    event=[]
    a,b=0,11
    for i in range(5):
        s1=res[a:b]
        if len(s1)==0:
            s1='\r'
        event.append(s1)
        a,b=a+11,b+11
    var=alert+event
    #获取处理后的报警信息，方便调试
    with open('/tmp/messages1','a',encoding='utf-8') as f:
        for i in event:     
            s=json.dump(i,f,ensure_ascii=False)
    return var  
#print(sig)
def sendsms(remes):
    url='https://yun.tim.qq.com/v5/tlssmssvr/sendsms?sdkappid=1400238944&random={}'.format(rand)
    header={"Content-Type": "application/json"}
    data={
        "ext": "123",
        "extend": "",
        "params": [
            remes[0],
            remes[1],
            remes[2],
            remes[3],
            remes[4],
            remes[5],
            remes[6],
            remes[7],
            remes[8],
            remes[9],
            remes[10],
            remes[11]
        ],
        "sig": sig,
        "sign": "没有故事的陈师傅",
        "tel": {
            "mobile": mobile,
            "nationcode": "86"
        },
        "time": times,
        "tpl_id": 387120
    }
    request=requests.post(url=url,headers=header,json=data)
    return json.loads(request.content)

rest=rest(message)
remes=remes(rest,message)
sendsms(remes)
```

### 接入zabbix报警
将脚本放到/usr/lib/zabbix/alertscripts/目录下，并授予脚本操作权限，然后在zabbix页面进行配置
#### 定义报警媒介类型
![](https://s1.51cto.com/images/blog/201908/03/f8de04796c81b9f2ca1c73c8ac4ba3e6.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

#### 配置用户接收的手机号
![](https://s1.51cto.com/images/blog/201908/03/3ba42575ec694cca11034e885ea755a1.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

#### 添加动作
消息内容的顺序不能乱，因为是与短信模板进行匹配的
![](https://s1.51cto.com/images/blog/201908/03/e9e8592e0c2e211c0a990d41f8131d9f.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

### 进行zabbix报警测试
停止zabbix-agent，使其产生报警
```
systemctl stop zabbix-agent
```  

#### 可以看到报警短信已经收到
![](https://s1.51cto.com/images/blog/201908/03/cad9012d39e046ba782e73c233049cdf.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

如果要查看短信的报错信息，可以在腾讯云短信服务的统计分析中查看
![](https://s1.51cto.com/images/blog/201908/03/8ce0119be6b2b468d6bb02390739e40a.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)  

### 踩过的坑
1. 尽量使用python3，python2在Linux环境下匹配数据可能会存在问题
1. 短信模板中变量的分隔符尽量不要出现在触发器中，否则会造成转义
1. 腾讯云同一手机号的发送短信频率为30秒内发送短信条数不超过1条，1小时内发送短信条数不超过5条，1个自然日内发送短信条数不超过10条，所以以后可以试试其他厂商的产品或者进行企业认证
1. 传入的模板变量不能为空字符，可以先将空字符串转为"\r"，模板变量之间也不能用空字符分隔



-----

欢迎关注个人公众号“没有故事的陈师傅”
![](https://s1.51cto.com/images/blog/201908/03/30da148b8ff01622822cc3437f653456.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)