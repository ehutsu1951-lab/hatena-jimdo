# はてなブログ → Jimdo 自動記事リンク（無料）

はてなブログ `https://stoputsunomiyalrt.hatenablog.com/` の公開HTMLから最新10件を抽出して、GitHub Pages に掲載します。Jimdo の RSS ウィジェットは使用しません。

## 1. GitHubの新規リポジトリ
1. GitHubで新しい **Public** リポジトリ `hatena-jimdo` を作成。
2. このZIPの中身（`.github/workflows/update.yml`、`update.py`、`requirements.txt`、`docs/index.html`）をリポジトリの同じ場所にアップロード。**`.github` は隠しフォルダです。**
3. GitHub の **Settings → Actions → General → Workflow permissions** で **Read and write permissions** を選択（必要な場合のみ）。
4. **Actions → Update Hatena articles → Run workflow** を押す。自動生成された `docs/index.html` が更新されます。
5. **Settings → Pages → Build and deployment → Deploy from a branch → main /docs → Save**。しばらくして公開されます。

## 2. Jimdo へ貼り付け
Jimdo Creatorでページを編集 → 「コンテンツを追加」→「その他のコンテンツ＆アドオン」→「ウィジェット / HTML」 → 次を貼り付けます。`YOUR_GITHUB_USER` はご自分のGitHubユーザー名に変更します。

```html
<iframe
  src="https://YOUR_GITHUB_USER.github.io/hatena-jimdo/"
  title="はてなブログの最新記事"
  style="width:100%;height:1250px;border:0;background:#fff;"
  loading="lazy">
</iframe>
```

## 3. 自動更新
GitHub Actions が約2時間ごとに公開ブログを確認します。GitHub側の混雑などにより遅れる場合があります。ページを直接更新するためJimdoを触る必要はありません。

## 補足
- はてなブログのサイト構造変更によりプログラム更新が必要になることがあります。
- ブログに表示される記事が10件未満なら、その件数が表示されます。
- 画像はブログ記事内にある場合のみ表示します。
- Jimdoの無料ページに載せる外部iframeは表示条件によって高さが変わるため、HTMLの `height:1250px` を調整してください。
- Publicリポジトリ／標準的なGitHub Pages・Actionsの無料枠内で利用する想定です。GitHubの無料枠や規約は変更される場合があります。
