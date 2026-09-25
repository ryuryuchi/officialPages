---
作成日: 2026-09-15
更新日: 2026-09-15
タグ:
  - GitHub Pages
  - GitHub Actions
  - 静的サイト
状態: 完了
---

# GitHub Pagesの基本と公開方法

## 概要

GitHub Pagesについて、サービスの仕組み、サイトの種類、公開方法、独自ドメイン、
制約、用途上の注意点をGitHub公式資料に基づいて整理する。

## 結論

GitHub Pagesは、GitHubリポジトリに置いたHTML・CSS・JavaScriptなどを公開する
静的サイトホスティングサービスである。個人・組織のサイト、プロジェクトの紹介、
ドキュメント、ブログ、ポートフォリオなど、サーバー側の処理を必要としないサイトに
向いている。

公開方法は、少量の静的ファイルをそのまま公開するならブランチの指定、ビルド処理や
Jekyll以外の静的サイトジェネレーターを使うならGitHub Actionsが扱いやすい。
データベース、サーバーサイドプログラム、ログイン処理などをGitHub Pagesだけで
実行することはできないため、その部分は別のAPIやホスティングサービスに分ける。

個人・組織サイトは `<owner>.github.io` リポジトリから公開し、プロジェクトサイトは
通常のリポジトリから `<owner>.github.io/<repository>` の形式で公開する。独自ドメイン、
HTTPS、Jekyll、カスタムGitHub Actionsワークフローにも対応するが、サイト容量1 GB、
デプロイ10分、帯域のソフト上限100 GB/月などの制約がある。

## 詳細

### 仕組みとサイトの種類

GitHub Pagesは、リポジトリ内の静的ファイルを配信し、設定によっては公開前にビルドを
実行する。訪問者からのリクエストごとにアプリケーションサーバーで処理するサービス
ではない。

| 種類 | リポジトリ | 標準URL | 用途 |
| --- | --- | --- | --- |
| ユーザーサイト | `<owner>.github.io` | `https://<owner>.github.io` | 個人のホームページ、ポートフォリオ |
| 組織サイト | `<owner>.github.io` | `https://<owner>.github.io` | 組織のホームページ、公式ドキュメント |
| プロジェクトサイト | 任意のプロジェクトリポジトリ | `https://<owner>.github.io/<repository>` | プロジェクト紹介、製品ドキュメント、デモ |

ユーザーサイトと組織サイトはアカウントごとに1サイト、プロジェクトサイトはリポジトリ
ごとに1サイトである。プロジェクトサイトのURLにはリポジトリ名が含まれるため、Reactや
Vueなどのアプリを公開する場合は、ビルドツールのベースパスも確認する必要がある。

### 公開方法の比較

#### ブランチから公開する方法

リポジトリのSettingsで **Pages** を開き、**Build and deployment** の **Source** を
**Deploy from a branch** に設定する。公開対象のブランチとフォルダー（ルートまたは
`/docs`）を選ぶと、対象ブランチへのpushを契機に公開される。

次のようなサイトに向いている。

- `index.html`、CSS、画像などをそのまま公開する小規模サイト
- ビルド済み成果物をリポジトリで管理したいサイト
- GitHub Actionsを追加せず、設定を簡単にしたいサイト

#### GitHub Actionsでビルドして公開する方法

GitHub Actionsのワークフローで、チェックアウト、依存関係のインストール、静的サイトの
ビルド、Pages用アーティファクトのアップロード、デプロイを行う。GitHub公式の
`actions/configure-pages`、`actions/upload-pages-artifact`、`actions/deploy-pages`を
利用できる。

Jekyll以外の静的サイトジェネレーターや、npmなどを使うビルド処理を組み込みたい場合は
この方法が適している。デプロイジョブには通常、`pages: write` と `id-token: write`
を含む権限設定、`github-pages`環境、ビルドジョブとの `needs` 関係が必要になる。
実際のアクションのバージョンや権限は、公式のスターターワークフローを基準に確認する。

### Jekyllとの関係

JekyllはMarkdownなどから静的HTMLを生成する静的サイトジェネレーターで、GitHub Pagesに
組み込みサポートがある。テーマ、レイアウト、Front Matterを使うサイトには便利である。

ただし、GitHub公式資料では、Jekyllを使う場合もGitHub Actionsによるデプロイと自動化が
推奨されている。Jekyllを使わない場合も、Actionsのカスタムワークフローを使えば任意の
静的サイトジェネレーターで生成した成果物を公開できる。

### 最小構成の公開手順

1. 新規または既存のGitHubリポジトリに `index.html` を用意する。
2. ユーザーサイトならリポジトリ名を `<username>.github.io` にする。プロジェクトサイト
   なら任意のリポジトリを使う。
3. リポジトリの **Settings** → **Pages** を開く。
4. 単純な静的ファイルなら **Deploy from a branch** を選び、ブランチとフォルダーを指定
   する。ビルドが必要ならGitHub ActionsのPages用ワークフローを選ぶ。
5. 保存後、表示されたURLを開く。変更の反映には最大10分かかる場合がある。

公開前に、リンク先や画像パスがプロジェクトサイトのサブパスに対応していること、
公開対象に秘密情報や不要な設定ファイルが含まれていないことを確認する。

### 独自ドメインとHTTPS

GitHub Pagesでは、`www.example.com` や `blog.example.com` のサブドメインと、
`example.com` のようなアペックスドメインを使える。

- サブドメインはDNSプロバイダーに `CNAME` レコードを設定する。
- アペックスドメインは `A`、`ALIAS`、`ANAME` のいずれかをDNSプロバイダーで設定する。
- 独自ドメインをリポジトリに設定する前に、GitHubでドメインを検証することが推奨される。
  検証しないままPagesを無効化すると、ドメインテイクオーバーのリスクがある。
- HTTPSを有効にするとHTTPアクセスをHTTPSへリダイレクトできる。公開サイトではHTTPSを
  強制する。

DNSの変更には反映時間がある。GitHub Pagesを停止した後もDNSレコードを残す場合は、
独自ドメインの設定状態と所有権検証を定期的に確認する。

### 主な制約とセキュリティ上の注意

GitHub公式資料に記載されている主な制約は次のとおりである。

| 項目 | 制約 |
| --- | --- |
| ユーザー・組織サイト | アカウントごとに1サイト |
| Pagesソースリポジトリ | 推奨上限1 GB |
| 公開済みサイト | 1 GB以下 |
| デプロイ時間 | 10分を超えるとタイムアウト |
| 帯域 | 100 GB/月のソフト上限 |
| ビルド回数 | 10回/時のソフト上限。カスタムGitHub Actionsワークフローでのビルドにはこの制限が適用されない |

上限超過時は、レート制限、配信停止、GitHub Supportからの代替策の案内などが行われる
可能性がある。大容量ファイルや大量配信には、リリース、CDN、別のホスティングサービス
を検討する。

GitHub Pagesはオンラインビジネス、電子商取引、商用SaaSを運用するための無料Web
ホスティングとしては想定されていない。また、パスワードやクレジットカード番号などの
機密性の高い取引を扱わない。静的ファイルは公開対象になり得るため、APIキー、秘密鍵、
個人情報をリポジトリやビルド成果物に含めない。

### 向いている用途・向いていない用途

**向いている用途**

- READMEやMarkdownから作るドキュメントサイト
- 技術ブログ、ポートフォリオ、履歴書
- オープンソースプロジェクトの紹介ページ
- JavaScriptで完結する静的なデモ

**単独では向いていない用途**

- ユーザー情報を保存する会員サイト
- データベースを使う業務システム
- サーバー側で認証・決済・ファイル処理を行うサービス
- 大容量ファイルや大量トラフィックを継続的に配信するサービス

後者では、フロントエンドをGitHub Pagesに置き、API・認証・データベース・ファイル配信を
別サービスに分離する構成を検討する。

## 参考資料

- [What is GitHub Pages? - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
  - GitHub Pagesの定義、サイトの種類、標準URL、データ収集の説明
  - 参照日: 2026-09-15
- [Quickstart for GitHub Pages - GitHub Docs](https://docs.github.com/en/pages/quickstart)
  - ユーザーサイトの作成、Pages設定、公開確認の手順
  - 参照日: 2026-09-15
- [Creating a GitHub Pages site - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
  - 新規・既存リポジトリからのサイト作成と公開手順
  - 参照日: 2026-09-15
- [Configuring a publishing source for your GitHub Pages site - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
  - ブランチ公開とGitHub Actions公開の設定
  - 参照日: 2026-09-15
- [Using custom workflows with GitHub Pages - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
  - Pages用GitHub Actions、アーティファクト、権限、デプロイ設定
  - 参照日: 2026-09-15
- [About GitHub Pages and Jekyll - GitHub Docs](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll)
  - Jekyllの役割とGitHub Actionsを使ったデプロイの推奨
  - 参照日: 2026-09-15
- [GitHub Pages limits - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
  - 容量、帯域、ビルド回数、タイムアウト、商用利用に関する制約
  - 参照日: 2026-09-15
- [About custom domains and GitHub Pages - GitHub Docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)
  - サブドメイン、アペックスドメイン、DNS、ドメインテイクオーバー対策
  - 参照日: 2026-09-15
- [Securing your GitHub Pages site with HTTPS - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
  - HTTPSの強制とHTTPからHTTPSへのリダイレクト
  - 参照日: 2026-09-15

## 更新履歴

- 2026-09-15: GitHub Pagesの仕組み、公開方法、独自ドメイン、制約、用途を公式資料に基づいて初版作成
