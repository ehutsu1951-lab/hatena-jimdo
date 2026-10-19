# 立体カード型：はてなブログ → Jimdo

## 仕組み
- 公開ブログの各ページから記事を取得し、`articles.json` に過去記事を蓄積します。初回に取得できる過去記事は公開ページで遡れる範囲です。
- 新しい記事は GitHub Actions で約2時間ごとに確認します。GitHub Actions のスケジュールは遅延または停止する場合があります。
- `index.html` を GitHub Pages の `main` と `/(root)` で公開します。
- カード型のデザイン、検索、年月選択、さらに表示、記事リンクを備えています。

## 更新手順
1. GitHub リポジトリ直下の `update.py` と `requirements.txt` を、このZIPの内容に差し替えます。
2. `.github/workflows/update.yml` を同じパスで登録します（重要：ルート直下の `update.yml` は無効）。GitHub 上で Add file > Create new file から `.github/workflows/update.yml` を指定して中身を貼り付けても構いません。
3. Repository Settings > Actions > General > Workflow permissions を Read and write permissions に変更する必要がある場合があります。
4. Actions > Update Hatena articles > Run workflow で初回実行。完了後、`index.html` と `articles.json` が生成されます。
5. GitHub Pages は `main` / `/(root)` を維持します。既に Jimdo に iframe を貼っている場合、URLを変える必要はありません。

Jimdo に貼るコード：

```html
<iframe src="https://ehutsu1951-lab.github.io/hatena-jimdo/" title="公共交通を考える会の記事一覧" style="width:100%;height:1250px;border:0" loading="lazy"></iframe>
```

はてなブログ側の構造変更、閲覧制限、記事の公開範囲によっては取得できないことがあります。
