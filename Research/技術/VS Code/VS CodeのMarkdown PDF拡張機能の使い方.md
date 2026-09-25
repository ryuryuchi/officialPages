---
作成日: 2026-09-24
更新日: 2026-09-24
タグ:
  - VS Code
  - Markdown PDF
  - PDF
  - 拡張機能
状態: 完了
---

# VS CodeのMarkdown PDF拡張機能の使い方

## 概要

VS Code拡張「Markdown PDF」のインストールから、MarkdownファイルのPDF出力、出力先や用紙の設定、エラー時の確認方法までを整理する。

## 結論

Markdown PDFをインストールし、出力したいMarkdownファイルをエディターで開いてから、コマンドパレットまたはエディターの右クリックメニューで `markdown-pdf: Export (pdf)` を実行する。初回のPDF出力では、システムにあるChrome、Edge、Chromiumのいずれかが使われるか、管理対象のChromiumがダウンロードされる。

## 詳細

### インストール

1. VS Codeの拡張機能ビューを開く（`Ctrl+Shift+X`）。
2. `Markdown PDF` を検索する。
3. 発行元が `yzane` の拡張機能を選び、インストールする。

### PDFへの変換

変換対象の `.md` ファイルをVS Codeで開き、次のどちらかを実行する。

**コマンドパレット**

1. `F1` または `Ctrl+Shift+P` を押す。
2. `export` と入力する。
3. `markdown-pdf: Export (pdf)` を選ぶ。

**エディターの右クリックメニュー**

1. Markdownファイルのエディター上で右クリックする。
2. `markdown-pdf: Export (pdf)` を選ぶ。

HTML、PNG、JPEGで出力するときは、それぞれ `markdown-pdf: Export (html)`、`markdown-pdf: Export (png)`、`markdown-pdf: Export (jpeg)` を選ぶ。すべての形式を一度に作る場合は `markdown-pdf: Export (all: pdf, html, png, jpeg)` を選択する。

### 出力先とPDFの設定

ユーザー設定またはワークスペース設定の `settings.json` に、必要な設定を追加する。例えば、Markdownファイルと同じ場所にある `pdf` フォルダーへPDFを出力し、A4縦にする場合は次のように設定する。

```json
{
  "markdown-pdf.type": ["pdf"],
  "markdown-pdf.outputDirectory": "./pdf",
  "markdown-pdf.format": "A4",
  "markdown-pdf.orientation": "portrait"
}
```

設定画面（`Ctrl+,`）で `markdown-pdf` を検索すると、利用できる設定を確認できる。プロジェクト単位で設定する場合は、プロジェクトの `.vscode/settings.json` に記載する。`markdown-pdf.outputDirectory` を指定しない場合は、出力ファイルは元のMarkdownファイルと同じフォルダーに作成される。

### 保存時に自動変換する

Markdownファイルを保存するたびに自動で変換するには、設定に次を追加してVS Codeを再起動する。

```json
{
  "markdown-pdf.convertOnSave": true
}
```

保存のたびに変換が走るため、必要なファイルやワークスペースに限って有効にする。

### 初回のPDF出力とトラブルシューティング

PDF、PNG、JPEGの出力にはChromiumベースのブラウザーが使われる。拡張機能は、設定で指定した実行ファイル、インストール済みのGoogle Chrome・Microsoft Edge・Chromium、管理対象として自動ダウンロードするChromiumの順に利用を試みる。ブラウザーのダウンロードが必要な場合、ネットワークやプロキシ設定によって完了まで時間がかかることがある。

出力に失敗した場合は、拡張機能が表示するエラー通知を確認する。詳しい情報を不具合報告用に収集するには、コマンドパレットから `Markdown PDF: Output Diagnostics` を実行する。

Markdown内の生HTMLは既定でサニタイズされる。スクリプトや一部のHTML要素・属性は出力から除去されることがあるため、HTMLが必要な場合は拡張機能の `markdown-pdf.sanitize` 設定と公式説明を確認する。

## 参考資料

- [Markdown PDF（日本語README）](https://github.com/yzane/vscode-markdown-pdf/blob/master/README.ja.md)
  - インストール後の出力操作、保存時変換、Chromiumの選択、設定、診断コマンドを確認
  - 参照日: 2026-09-24
- [Markdown PDF - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)
  - 拡張機能の公開ページ、更新内容、サニタイズの既定動作を確認
  - 参照日: 2026-09-24

## 更新履歴

- 2026-09-24: Markdown PDF拡張機能の導入、出力、設定、トラブル対応をまとめて初版を作成
