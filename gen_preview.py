import os, json, html, datetime, base64
BASE=os.path.dirname(__file__); QUEUE=os.path.join(BASE,"posts","queue.json"); OUT=os.path.join(BASE,"review","preview.html")
def jst(iso):
    try:
        t=datetime.datetime.fromisoformat(iso.replace("Z","+00:00")); return (t+datetime.timedelta(hours=9)).strftime("%m/%d %H:%M")
    except: return iso
def datauri(url):
    name=url.rsplit("/",1)[-1]; p=os.path.join(BASE,"images",name)
    if not os.path.exists(p): return ""
    return "data:image/png;base64,"+base64.b64encode(open(p,"rb").read()).decode()
def esc(t): return html.escape(t).replace("\n","<br>")
CSS="<style>body{font-family:-apple-system,sans-serif;background:#faf8f3;margin:0;padding:24px;color:#222}h1{font-size:20px}.card{background:#fff;border:1px solid #e6e0d3;border-radius:14px;padding:18px 20px;max-width:560px;margin:0 auto 18px}.meta{display:flex;justify-content:space-between;margin-bottom:10px}.time{font-weight:700;color:#0F6E56}.badge{font-size:12px;padding:3px 10px;border-radius:20px}.draft{background:#f1efe8;color:#888}.pending{background:#E1F5EE;color:#0F6E56}.text{font-size:15px;line-height:1.7}.reply{margin-top:10px;padding:10px 12px;background:#eef5f1;border-left:3px solid #1D9E75;border-radius:0 8px 8px 0;font-size:14px;line-height:1.7}.rlabel{display:block;font-size:12px;color:#0F6E56;font-weight:700;margin-bottom:4px}.imgs img{width:100%;border-radius:10px;margin-top:12px}</style>"
d=json.load(open(QUEUE,encoding="utf-8"))
posts=[p for p in d.get("posts",[]) if p.get("status") in ("draft","pending")]
posts.sort(key=lambda p:p.get("scheduled_time",""))
cards=[]
for p in posts:
    imgs="".join('<img src="%s">'%datauri(u) for u in p.get("images",[]) if datauri(u))
    reply='<div class="reply"><span class="rlabel">↳ 返信（自動投稿）</span>%s</div>'%esc(p["reply_text"]) if p.get("reply_text") else ""
    badge="予約" if p.get("status")=="pending" else "下書き"
    cards.append('<div class="card"><div class="meta"><span class="time">%s</span><span class="badge %s">%s</span></div><div class="text">%s</div>%s<div class="imgs">%s</div></div>'%(jst(p.get("scheduled_time","")),p.get("status"),badge,esc(p.get("text","")),reply,imgs))
doc='<!doctype html><meta charset="utf-8"><title>投稿プレビュー</title>'+CSS+('<h1>投稿プレビュー（%d件）— 時刻順・返信つき</h1>'%len(posts))+"".join(cards)
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,"w",encoding="utf-8").write(doc)
print("preview:",len(posts),"件")
