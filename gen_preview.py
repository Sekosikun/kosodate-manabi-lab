"""
投稿確認用の preview.html を生成する。
queue.json を読み、status が draft / pending の投稿を時刻順に並べ、
本文と画像つきで一覧表示する（ユーザーがブラウザで確認するため）。
実行: python3 automation/gen_preview.py
出力: automation/review/preview.html
"""
import os, json, html, datetime, base64

BASE = os.path.dirname(__file__)
QUEUE = os.path.join(BASE, "posts", "queue.json")
OUT = os.path.join(BASE, "review", "preview.html")


def jst(iso):
    try:
        t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (t + datetime.timedelta(hours=9)).strftime("%m/%d (%a) %H:%M")
    except Exception:
        return iso


def img_datauri(url):
    name = url.rsplit("/", 1)[-1]
    path = os.path.join(BASE, "images", name)
    if not os.path.exists(path):
        return ""
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return "data:image/png;base64," + b64


def main():
    with open(QUEUE, encoding="utf-8") as f:
        data = json.load(f)
    posts = [p for p in data.get("posts", []) if p.get("status") in ("draft", "pending")]
    posts.sort(key=lambda p: p.get("scheduled_time", ""))
    cards = []
    for p in posts:
        imgs = "".join(
            f'<img src="{img_datauri(u)}" alt="">' for u in p.get("images", []) if img_datauri(u))
        body = html.escape(p.get("text", "")).replace("\n", "<br>")
        badge = "予約済" if p.get("status") == "pending" else "下書き"
        cards.append(f'''<div class="card">
  <div class="meta"><span class="time">{jst(p.get("scheduled_time",""))}</span>
  <span class="badge {p.get('status')}">{badge}</span></div>
  <div class="text">{body}</div>
  <div class="imgs">{imgs}</div>
</div>''')
    doc = f'''<!doctype html><meta charset="utf-8">
<title>投稿プレビュー</title>
<style>
body{{font-family:-apple-system,sans-serif;background:#faf8f3;margin:0;padding:24px;color:#222}}
h1{{font-size:20px}}
.card{{background:#fff;border:1px solid #e6e0d3;border-radius:14px;padding:18px 20px;max-width:560px;margin:0 auto 18px}}
.meta{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}}
.time{{font-weight:700;color:#0F6E56}}
.badge{{font-size:12px;padding:3px 10px;border-radius:20px}}
.badge.draft{{background:#f1efe8;color:#888}}
.badge.pending{{background:#E1F5EE;color:#0F6E56}}
.text{{font-size:15px;line-height:1.7;white-space:normal}}
.imgs img{{width:100%;border-radius:10px;margin-top:12px}}
</style>
<h1>投稿プレビュー（{len(posts)}件）— 上から時刻順</h1>
{''.join(cards)}'''
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("生成:", OUT, "（", len(posts), "件 ）")


if __name__ == "__main__":
    main()
