import os, base64, requests
from nacl import encoding, public
pat = os.environ["GH_PAT"]; repo = os.environ["GITHUB_REPOSITORY"]; new = os.environ["NEW_TOKEN"]
h = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}
pk = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=h).json()
pub = public.PublicKey(pk["key"].encode(), encoding.Base64Encoder())
sealed = public.SealedBox(pub).encrypt(new.encode())
enc = base64.b64encode(sealed).decode()
r = requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/THREADS_TOKEN", headers=h,
                  json={"encrypted_value": enc, "key_id": pk["key_id"]})
print("secret update status:", r.status_code)
r.raise_for_status()
