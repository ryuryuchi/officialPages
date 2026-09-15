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

`index.md`を同じフォルダの`index.html`へ変換するジェネレーターを用意しています。
引数なしで実行すると、リポジトリ内にあるすべての`index.md`を対象にします。

```powershell
python .\generate_html.py
```

個別のページだけを生成する場合は、Markdownファイルまたはフォルダを指定します。

```powershell
python .\generate_html.py .\diary\2026-09-15\index.md
python .\generate_html.py .\diary\2026-09-15
```

既存ファイルを変更せず、生成結果に差分があるかだけを確認することもできます。

```powershell
python .\generate_html.py --check
```

## トップページのリンクを自動更新

トップ直下の各フォルダをカテゴリとして、配下の`index.html`へ飛ぶリンクを
トップページへ追記・更新できます。たとえば`diary`フォルダは
`<section name="diary">`へ自動的に反映されます。

```powershell
python .\update.py
```

sectionがまだないカテゴリも自動で追加されます。書き換え前の確認には`--check`を使えます。

```powershell
python .\update.py --check
```

## HTML生成とリンク更新をまとめて実行

次のBATを実行すると、すべての`index.md`をHTMLへ変換したあと、
トップページのリンクを更新します。

```powershell
.\generate_all.bat
```
