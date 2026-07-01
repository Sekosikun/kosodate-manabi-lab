import os, json, sys, urllib.parse, urllib.request
BASE="https://graph.threads.net"
def get(path, params):
    url=f"{BASE}/{path}?"+urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r: return json.load(r)
def main():
    tok=os.environ.get("THREADS_TOKEN")
    if not tok: sys.exit("THREADS_TOKEN未設定")
    res=get("refresh_access_token", {"grant_type":"th_refresh_token","access_token":tok})
    new=res.get("access_token")
    if not new: sys.exit("refresh失敗: "+json.dumps(res))
    print("::add-mask::"+new)
    gh_out=os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out,"a") as f: f.write(f"new_token={new}\n")
    print("refreshed ok, len=",len(new))
if __name__=="__main__": main()
