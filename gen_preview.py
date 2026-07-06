import os, json, html, datetime, base64
BASE=os.path.dirname(__file__); QUEUE=os.path.join(BASE,"posts","queue.json"); OUT=os.path.join(BASE,"review","preview.html")
WD=["月","火","水","木","金","土","日"]

def to_jst(iso):
    t=datetime.datetime.fromisoformat(iso.replace("Z","+00:00"))
    return t+datetime.timedelta(hours=9)

def time_label(iso):
    if not iso: return "時刻指定なし"
    try: return to_jst(iso).strftime("%H:%M")
    except: return iso

def datauri(url):
    name=url.rsplit("/",1)[-1]; p=os.path.join(BASE,"images",name)
    if not os.path.exists(p): return ""
    return "data:image/png;base64,"+base64.b64encode(open(p,"rb").read()).decode()

def esc(t): return html.escape(t).replace("\n","<br>")

CSS="""<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Hiragino Sans',sans-serif;background:#faf8f3;margin:0;padding:28px 16px;color:#222}
h1{font-size:22px;margin:0 0 6px}
.summary{color:#666;font-size:14px;margin-bottom:24px}
details.group{max-width:640px;margin:0 auto 18px;background:#fff;border:1px solid #e6e0d3;border-radius:14px;overflow:hidden}
details.group[open]{padding-bottom:6px}
summary.gh{cursor:pointer;list-style:none;padding:16px 22px;font-size:17px;font-weight:700;color:#0F6E56;background:#eef5f1;display:flex;justify-content:space-between;align-items:center}
summary.gh::-webkit-details-marker{display:none}
summary.gh .cnt{font-size:13px;font-weight:600;color:#0F6E56;background:#fff;border-radius:20px;padding:3px 12px}
.card{border-top:1px solid #eee;padding:20px 22px;margin:0}
.meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.time{font-weight:700;color:#0F6E56;font-size:18px}
.badge{font-size:13px;padding:4px 12px;border-radius:20px;font-weight:600}
.draft{background:#f1efe8;color:#888}
.pending{background:#E1F5EE;color:#0F6E56}
.text{font-size:17px;line-height:1.85}
.reply{margin-top:12px;padding:12px 14px;background:#eef5f1;border-left:4px solid #1D9E75;border-radius:0 10px 10px 0;font-size:15px;line-height:1.8}
.rlabel{display:block;font-size:13px;color:#0F6E56;font-weight:700;margin-bottom:5px}
.imgs img{width:100%;border-radius:10px;margin-top:14px}
.id{font-size:12px;color:#aaa;margin-top:10px}
</style>"""

def card_html(p):
    imgs="".join('<img src="%s">'%datauri(u) for u in p.get("images",[]) if datauri(u))
    rlist = p.get("reply_texts") or ([p["reply_text"]] if p.get("reply_text") else [])
    reply="".join('<div class="reply"><span class="rlabel">↳ 返信%d（自動投稿）</span>%s</div>'%(i+1,esc(r)) for i,r in enumerate(rlist))
    badge="予約" if p.get("status")=="pending" else "下書き"
    return ('<div class="card"><div class="meta"><span class="time">%s</span><span class="badge %s">%s</span></div>'
            '<div class="text">%s</div>%s<div class="imgs">%s</div><div class="id">%s</div></div>'
            %(time_label(p.get("scheduled_time")),p.get("status"),badge,esc(p.get("text","")),reply,imgs,p.get("id","")))

d=json.load(open(QUEUE,encoding="utf-8"))
posts=[p for p in d.get("posts",[]) if p.get("status") in ("draft","pending")]

by_date={}   # "YYYY-MM-DD" -> list
reuse_sat=[]; reuse_any=[]; fixed_other=[]

for p in posts:
    iso=p.get("scheduled_time")
    if iso:
        try:
            key=to_jst(iso).strftime("%Y-%m-%d")
            by_date.setdefault(key,[]).append(p)
            continue
        except: pass
    if p.get("reuse_day")=="saturday": reuse_sat.append(p)
    elif p.get("reuse_day")=="any": reuse_any.append(p)
    else: fixed_other.append(p)

today=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=9)
today_key=today.strftime("%Y-%m-%d")

groups=[]  # (title, list, open_by_default)
for key in sorted(by_date.keys()):
    y,m,dd=key.split("-")
    wd=WD[datetime.date(int(y),int(m),int(dd)).weekday()]
    items=sorted(by_date[key], key=lambda p:p.get("scheduled_time",""))
    title="%s/%s（%s）"%(int(m),int(dd),wd)
    groups.append((title, items, key>=today_key))

if reuse_sat: groups.append(("🔁 土曜日限定・再利用プール", reuse_sat, False))
if reuse_any: groups.append(("🔁 曜日フリー・再利用プール", reuse_any, False))
if fixed_other: groups.append(("📌 固定投稿・その他（保留中）", fixed_other, False))

pending_n=sum(1 for p in posts if p["status"]=="pending")
draft_n=len(posts)-pending_n

sections=[]
for title, items, is_open in groups:
    body="".join(card_html(p) for p in items)
    sections.append('<details class="group"%s><summary class="gh"><span>%s</span><span class="cnt">%d件</span></summary>%s</details>'
                     %(" open" if is_open else "", html.escape(title), len(items), body))

doc=('<!doctype html><meta charset="utf-8"><title>投稿プレビュー</title>'+CSS+
     '<h1>投稿プレビュー</h1><div class="summary">全%d件（予約 %d件・下書き %d件）— 日付ごとにグループ化、タップで開閉</div>'
     %(len(posts),pending_n,draft_n)+"".join(sections))
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,"w",encoding="utf-8").write(doc)
print("preview:",len(posts),"件 /",len(groups),"グループ")
