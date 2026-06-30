"""
子育てまなびラボ 自動投稿スクリプト（Threads）
- GitHub Actions（クラウド）から定期実行される。PCは不要。
- posts/queue.json から「予約時刻が来た未投稿」を1件取り出して投稿する。
- 画像なし=テキスト投稿 / 画像1枚=画像投稿 / 複数=カルーセル。
- reply_text があれば、投稿後にコメント返信としてリンク等を追加（本文にリンクを貼らない運用）。
依存ライブラリなし（標準ライブラリのみ）。
"""
import os, json, time, sys, datetime, urllib.parse, urllib.request

API = "https://graph.threads.net/v1.0"
TOKEN = os.environ.get("THREADS_TOKEN")
QUEUE = os.path.join(os.path.dirname(__file__), "posts", "queue.json")


def _call(method, path, params):
    params = dict(params)
    params["access_token"] = TOKEN
    if method == "GET":
        url = f"{API}/{path}?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url)
    else:
        url = f"{API}/{path}"
        req = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode())
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def get_user_id():
    return _call("GET", "me", {"fields": "id"})["id"]


def create_container(uid, params):
    return _call("POST", f"{uid}/threads", params)["id"]


def publish(uid, creation_id):
    # メディア処理待ち。失敗したら少し待って再試行。
    last = None
    for _ in range(12):
        try:
            return _call("POST", f"{uid}/threads_publish", {"creation_id": creation_id})["id"]
        except Exception as e:
            last = e
            time.sleep(15)
    raise RuntimeError(f"publish failed: {last}")


def post_item(uid, item):
    text = item.get("text", "")
    images = item.get("images", [])
    if not images:
        cid = create_container(uid, {"media_type": "TEXT", "text": text})
    elif len(images) == 1:
        cid = create_container(uid, {"media_type": "IMAGE", "image_url": images[0], "text": text})
    else:
        children = []
        for url in images:
            children.append(create_container(uid, {"media_type": "IMAGE", "image_url": url, "is_carousel_item": "true"}))
            time.sleep(3)
        time.sleep(20)
        cid = create_container(uid, {"media_type": "CAROUSEL", "children": ",".join(children), "text": text})
    time.sleep(20)
    pid = publish(uid, cid)
    reply = item.get("reply_text")
    if reply:
        time.sleep(5)
        rcid = create_container(uid, {"media_type": "TEXT", "text": reply, "reply_to_id": pid})
        time.sleep(5)
        publish(uid, rcid)
    return pid


def main():
    if not TOKEN:
        sys.exit("THREADS_TOKEN が設定されていません（GitHub Secrets に登録してください）")
    now = datetime.datetime.now(datetime.timezone.utc)
    with open(QUEUE, encoding="utf-8") as f:
        data = json.load(f)
    uid = get_user_id()
    changed = False
    for item in data.get("posts", []):
        if item.get("status") != "pending":
            continue
        st = item.get("scheduled_time")
        if st:
            t = datetime.datetime.fromisoformat(st.replace("Z", "+00:00"))
            if t > now:
                continue
        try:
            pid = post_item(uid, item)
            item["status"] = "posted"
            item["posted_id"] = pid
            changed = True
            print("posted:", item.get("id"), pid)
        except Exception as e:
            print("error:", item.get("id"), e)
        break  # 1回の実行で1件だけ（ウォームアップ＆安全のため）
    if changed:
        with open(QUEUE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
