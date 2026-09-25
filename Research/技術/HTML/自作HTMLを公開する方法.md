---
作成日: 2026-08-25
更新日: 2026-08-31
タグ:
  - HTML
  - Web公開
  - GitHub Pages
  - ホスティング
状態: 完了
---

# 自作HTMLをインターネットに公開する方法

## 概要

自作した静的なHTMLファイルを、第三者がブラウザで閲覧できるように公開する方法を整理する。

## 結論

HTML、CSS、JavaScriptだけで動くサイトなら、初心者はGitHub Pagesを使うと公開しやすい。`index.html`をGitHubリポジトリの公開元に置き、リポジトリのSettingsからPagesを有効にする。単純な静的ファイルはブランチから、独自のビルド工程が必要ならGitHub Actionsから公開する。

PHP、データベース、ログイン処理などサーバー側の処理が必要な場合はGitHub Pagesでは動かないため、レンタルサーバーまたは対応するクラウドホスティングを選ぶ。

## 詳細

### 公開前に確認すること

- 自作HTMLを入口にするなら、公開元の最上位へ`index.html`を置く。GitHub Pages自体は`index.md`または`README.md`も入口ファイルとして検索する。
- HTMLから読み込むCSS、画像、JavaScriptのパスを確認する。ローカルPC固有のパス（例: `C:\...`）は公開後に使えない。
- APIキー、パスワード、個人情報をHTMLやJavaScript、公開リポジトリに含めない。ブラウザに配信したファイルは閲覧者が確認できる。
- 公開URLにアクセスして、スマートフォンでも表示とリンクを確認する。

### GitHub Pagesで公開する手順

1. GitHubのアカウントを作成し、`my-site`などの新しいリポジトリを作る。個人またはOrganizationのGitHub Freeでは、GitHub Pages用リポジトリをパブリックにする必要がある。プライベートリポジトリからの公開可否は契約プランによるが、利用できる場合も公開サイト自体はインターネットへ公開される。
2. リポジトリの最上位に`index.html`と、必要なCSS、画像、JavaScriptをアップロードする。
3. リポジトリで **Settings** → **Pages** を開く。
4. **Build and deployment** の **Source** で **Deploy from a branch** を選び、公開するブランチ（通常は`main`）とフォルダー（通常は`/(root)`）を選択して保存する。
5. デプロイ完了後、Pages画面に表示されるURLを開く。通常、URLは`https://<GitHubユーザー名>.github.io/<リポジトリ名>/`となる。
6. 更新時は、公開元にあるファイルを変更してGitHubへpushする。GitHub Pagesが再デプロイするため、少し待ってからURLを再読み込みする。

個人サイトをリポジトリ名なしの`https://<GitHubユーザー名>.github.io/`で公開したい場合、リポジトリ名を`<GitHubユーザー名>.github.io`にする。

ブランチ公開で選べる公開元フォルダーは`/(root)`または`/docs`である。Jekyll以外のビルド処理を使う場合や生成物専用ブランチを持ちたくない場合は、公式テンプレートを基にGitHub Actions公開を選ぶ。

### GitHub Pagesが向くケースと向かないケース

| 向くケース | 向かないケース |
| --- | --- |
| ポートフォリオ、紹介ページ、作品展示、静的な資料サイト | PHP、Python、Node.jsなどを常時実行するサイト |
| HTML/CSS/JavaScriptだけで完結するサイト | 独自のデータベースやサーバー側の秘密情報が必要なサイト |

### ほかの公開先

- **Netlify / Vercel**: GitHubリポジトリと連携して公開したい静的サイトやフロントエンドアプリに向く。フレームワーク用のビルド設定も扱いやすい。
- **レンタルサーバー**: PHPやWordPressを使う場合に向く。契約後、サーバーの公開用フォルダーへFTP/SFTPでファイルをアップロードする。
- **独自ドメイン**: `example.com`のようなURLを使いたい場合は、ドメインを取得して、公開サービス側の案内に従ってDNS設定を追加する。HTTPS設定が自動提供されるかも確認する。

## 参考資料

- [GitHub Docs: GitHub Pages サイトの作成](https://docs.github.com/ja/pages/getting-started-with-github-pages/creating-a-github-pages-site)
  - 参照日: 2026-08-31
- [GitHub Docs: GitHub Pages サイトの発行ソースの構成](https://docs.github.com/ja/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
  - 参照日: 2026-08-31
- [GitHub Docs: GitHub Pages について](https://docs.github.com/ja/pages/getting-started-with-github-pages/what-is-github-pages)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、入口ファイル、公開元、GitHub Actions、プライベートリポジトリの注意を現行仕様へ更新
- 2026-08-25: 初版を作成
