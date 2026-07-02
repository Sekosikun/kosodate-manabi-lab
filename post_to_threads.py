import os, json, time, sys, datetime, urllib.parse, urllib.request
API="https://graph.threads.net/v1.0"; TOKEN=os.environ.get("THREADS_TOKEN")
QUEUE=os.path.join(os.path.dirname(__file__),"posts","queue.json")
SPACING=int(os.environ.get("POST_SPACING","60"))
def _call(m,path,params):
    params=dict(params); params["access_token"]=TOKEN
    if m=="GET": req=urllib.request.Request(f"{API}/{path}?"+urllib.parse.urlencode(params))
    else: req=urllib.request.Request(f"{API}/{path}",data=urllib.parse.urlencode(params).encode())
    with urllib.request.urlopen(req) as r: return json.load(r)
def uid_(): return _call("GET","me",{"fields":"id"})["id"]
def cont(uid,p): return _call("POST",f"{uid}/threads",p)["id"]
def pub(uid,cid):
    last=None
    for _ in range(12):
        try: return _call("POST",f"{uid}/threads_publish",{"creation_id":cid})["id"]
        except Exception as e: last=e; time.sleep(15)
    raise RuntimeError(f"publish failed: {last}")
def post_item(uid,it):
    text=it.get("text",""); imgs=it.get("images",[])
    if not imgs: cid=cont(uid,{"media_type":"TEXT","text":text})
    elif len(imgs)==1: cid=cont(uid,{"media_type":"IMAGE","image_url":imgs[0],"text":text})
    else:
        ch=[]
        for u in imgs: ch.append(cont(uid,{"media_type":"IMAGE","image_url":u,"is_carousel_item":"true"})); time.sleep(3)
        time.sleep(20); cid=cont(uid,{"media_type":"CAROUSEL","children":",".join(ch),"text":text})
    time.sleep(20); pid=pub(uid,cid)
    replies = it.get("reply_texts")
    if replies is None and it.get("reply_text"):
        replies = [it["reply_text"]]
    for r in (replies or []):
        time.sleep(5); rc=cont(uid,{"media_type":"TEXT","text":r,"reply_to_id":pid}); time.sleep(5); pub(uid,rc)
    return pid
def main():
    if not TOKEN: sys.exit("THREADS_TOKEN 未設定")
    now=datetime.datetime.now(datetime.timezone.utc); d=json.load(open(QUEUE,encoding="utf-8"))
    due=[x for x in d["posts"] if x.get("status")=="pending" and (not x.get("scheduled_time") or datetime.datetime.fromisoformat(x["scheduled_time"].replace("Z","+00:00"))<=now)]
    due.sort(key=lambda x:x.get("scheduled_time",""))
    if not due: print("due=0"); return
    uid=uid_(); done=0
    for i,it in enumerate(due):
        try:
            pid=post_item(uid,it); it["status"]="posted"; it["posted_id"]=pid; done+=1
            json.dump(d,open(QUEUE,"w",encoding="utf-8"),ensure_ascii=False,indent=2); print("posted",it["id"],pid)
        except Exception as e: print("error",it["id"],e)
        if i<len(due)-1: time.sleep(SPACING)
    print("done",done,"/",len(due))
if __name__=="__main__": main()
