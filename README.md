# 子育てまなびラボ 自動投稿システム

PCを落としても投稿される、**GitHubクラウド完結**の自動投稿の仕組みです。

## 仕組み（PC非依存）
1. **Claude（私）** が週1などで投稿文と画像をまとめて作り、ここ（GitHub）に保存。
2. **GitHub Actions（クラウド）** が毎日決まった時間に自動実行し、`posts/queue.json` から「予約時刻が来た未投稿」を1件投稿。
3. あなたのPC・操作は不要。投稿後、キューは自動で「投稿済み」に更新される。

```
Claude（中身を作る・時々） → GitHubに保存 → GitHub Actions（毎日自動）→ Threadsへ投稿
```

## ファイル
- `post_to_threads.py` … 投稿本体（テキスト／画像／カルーセル／コメント返信リンク対応）
- `posts/queue.json` … 投稿キュー（予約時刻・本文・画像URL・状態）
- `images/` … 投稿画像（PNG）。GitHubの公開URLがそのまま画像として使われる
- `.github/workflows/post.yml` … 毎日の自動実行スケジュール（cron）
- `token_refresh.py` … APIトークンを60日長期に変換／更新する補助

## あなたがやること（ブラウザのみ・一度だけ）
1. このフォルダを入れる **GitHubリポジトリ** を用意（私が作成を補助）。画像を公開URLにするため **public** 推奨。
2. Threads API の **短期アクセストークン** を取得し、私に渡す（→私が60日トークンに変換）。
3. GitHubの **Settings > Secrets > Actions** に `THREADS_TOKEN` として登録（私が手順を案内／代行）。
   - トークンは暗号化保存。コードには書きません。publicリポジトリでも安全。

## スケジュール変更
`.github/workflows/post.yml` の `cron`（UTC表記）を編集。日本時間は +9時間。
- 例：`"0 0 * * *"` = 毎日 朝9時(JST)。本数を増やす時は行を追加。
- 初期はウォームアップのため少なめ（1日数本）→ 慣れたら増やす。

## 安全・運用メモ
- 本文にアフィリンクは貼らず、`reply_text` でコメント返信に入れる運用（リーチ維持）。
- 1回の実行で1件だけ投稿（安全・ウォームアップ）。
- 画像URLは `images/` 内ファイルの公開URL（`https://raw.githubusercontent.com/ユーザー名/リポジトリ名/main/images/ファイル名`）。
