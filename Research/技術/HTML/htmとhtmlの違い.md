---
作成日: 2026-08-25
更新日: 2026-08-31
タグ:
  - HTML
  - 拡張子
  - MIMEタイプ
状態: 完了
---

# htmとhtmlの違い

## 概要

HTMLファイルの拡張子である`.htm`と`.html`の違い、および新規作成時の選択基準を整理する。

## 結論

`.htm`と`.html`は、いずれもHTML文書の拡張子として使える。文書のHTML構文や、対応する標準のMIMEタイプである`text/html`に違いはない。

新しく作るファイルには、現在より一般的で意味が分かりやすい`.html`を使う。既存サイトが`.htm`で統一されている場合は、URL互換性と命名規則の一貫性を保つため、そのまま`.htm`を維持する。

## 詳細

### 拡張子の由来

`.htm`は、拡張子を3文字までに制限した古いMS-DOS FATの8.3ファイル名に合わせて広まった短縮形である。現在のWindowsファイルシステムは長いファイル名を扱えるため、この制約を理由に`.htm`を選ぶ必要はない。

### ブラウザでの扱い

ブラウザが受け取るHTMLの解釈は、HTTPで配信する場合は主にレスポンスの`Content-Type: text/html`で決まる。IANAは`text/html`をHTML用の登録済みメディアタイプとして定義し、一般的なファイル拡張子として`html`と`htm`の両方を明記している。

したがって、拡張子を`.html`から`.htm`へ変えても、HTMLのタグ、CSS、JavaScript、ブラウザの互換性に本質的な差は生じない。ただし、Webサーバーや静的ホスティングの設定が特定の拡張子だけを`text/html`へ対応付けている場合は、両方を正しく配信できるよう設定を確認する。

### 実務上の注意

- URLの一部として公開済みの拡張子を変更すると、既存リンクや検索結果が切れる可能性がある。変更する場合は301リダイレクトを設定する。
- プロジェクト内では拡張子を混在させず、既存の命名規則に合わせる。
- 新規プロジェクトでは、可読性と一般的な慣行から`.html`を選ぶ。

## 参考資料

- [HTML Living Standard](https://html.spec.whatwg.org/multipage/)
  - 参照日: 2026-08-31
- [IANA Media Types - text/html](https://www.iana.org/assignments/media-types/text/html)
  - 参照日: 2026-08-31
- [Microsoft Learn: Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、IANAの拡張子登録とMS-DOS FATの8.3制約を一次資料で補強
- 2026-08-25: 初版を作成
