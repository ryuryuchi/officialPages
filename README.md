# Official Pages

GitHub Pages 用のリポジトリです。

## 公開URL
- https://ryuryuchi.github.io/officialPages/

## 構成
- `index.html`: Webサイトのトップページ
- `.nojekyll`: Jekyll処理を無効化する設定ファイル

## 当日の日記フォルダとindex.mdを生成

当日日付のフォルダ（`diary/YYYY-MM-DD/`）と空の `index.md` を作成するスクリプトを用意しています。
すでにファイルが存在する場合は上書きされません。

```powershell
python .\create_diary.py
```

バッチファイルからも実行できます（Windows のスタートアップ等に登録して起動時に自動作成することも可能です）。

```powershell
.\create_diary.bat
```

## MarkdownからHTMLを生成

Markdownを同じフォルダのHTMLへ変換するジェネレーターを用意しています。
引数なしでは従来どおり、リポジトリ内にあるすべての`index.md`を
`index.html`へ変換します。

```powershell
python .\generate_html.py
```

Researchのように`index.md`以外のMarkdownもHTML化する場合は、
`--all-markdown`を指定します。Markdownの相対リンクも生成先のHTMLへ接続します。

```powershell
python .\generate_html.py --all-markdown .\Research
```

個別のページだけを生成する場合は、Markdownファイルまたはフォルダを指定します。
出力名はMarkdownと同名のHTMLです（`index.md`なら`index.html`）。

```powershell
python .\generate_html.py .\diary\2026-09-15\index.md
python .\generate_html.py .\diary\2026-09-15
```

既存ファイルを変更せず、生成結果に差分があるかだけを確認することもできます。

```powershell
python .\generate_html.py --check
```

## トップページのリンクを自動更新

トップ直下の各フォルダをカテゴリとして、トップページへリンクを追記・更新できます。
カテゴリ直下に`index.html`または`README.html`があればそのページへ、
なければ配下の`index.html`へリンクします。たとえば`Research`は目次ページへ、
`diary`は各日記ページへ自動的に接続されます。

```powershell
python .\update.py
```

sectionがまだないカテゴリも自動で追加されます。書き換え前の確認には`--check`を使えます。

```powershell
python .\update.py --check
```

## HTML生成とリンク更新をまとめて実行

次のBATを実行すると、すべての`index.md`と`Research`配下のMarkdownを
HTMLへ変換したあと、トップページのリンクを更新します。

```powershell
.\generate_all.bat
```

このBATは、生成・リンク更新に成功して変更がある場合、実行日を使った
`update YYYY-MM-DD` というコメントでコミットし、そのままリモートへプッシュします。
変更がない場合は空のコミットを作成せず、未プッシュのコミットだけをプッシュします。
プッシュにはGitの認証設定と、
現在のブランチに設定されたリモート追跡先が必要です。
