#encoding=utf-8
import requests,json
import sys
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"}
response=requests.get("http://192.168.179.133:9200/_cluster/health",headers=headers)
s=json.loads(response.content.decode())
parm=sys.argv[1]

itemlist=["cluster_name","status","timed_out","number_of_nodes","number_of_data_nodes","active_primary_shards","active_shards","relocating_shards","initializing_shards","unassigned_shards","delayed_unassigned_shards","number_of_pending_tasks","number_of_in_flight_fetch","task_max_waiting_in_queue_millis","active_shards_percent_as_number"]

if parm not in itemlist:
    print("parm failed")
    sys.exit(1)
else:
    print(s[parm])
