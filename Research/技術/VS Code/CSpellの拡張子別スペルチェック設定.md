---
作成日: 2026-09-10
更新日: 2026-09-10
タグ:
  - CSpell
  - VS Code
  - スペルチェック
  - 設定
状態: 完了
---

# CSpellの拡張子別スペルチェック設定

## 概要

VS Code拡張のCSpellで、ファイル種別（VS Codeのlanguage ID）ごとにスペルチェックの対象・対象外を設定できるかを確認した。

## 結論

設定できる。VS Codeのユーザー設定またはワークスペース設定で、`cSpell.enabledFileTypes` を使う。

特定の種類だけ除外する場合は、次のように設定する。

```json
{
  "cSpell.enabledFileTypes": {
    "markdown": false,
    "json": false
  }
}
```

逆に、Markdownだけを対象にするなど、対象を限定する場合はワイルドカードを使う。

```json
{
  "cSpell.enabledFileTypes": {
    "*": false,
    "markdown": true
  }
}
```

## 詳細

### 設定場所

プロジェクト単位なら、プロジェクト直下の `.vscode/settings.json` に記載する。全プロジェクトに適用するなら、VS Codeのユーザー設定に記載する。設定画面で `cSpell.enabledFileTypes` を検索して変更することもできる。

### 拡張子ではなくlanguage IDを指定する

設定のキーは拡張子そのものではなく、VS Codeのlanguage IDである。例えば、代表的な指定は次のとおり。

| 対象 | language ID |
| --- | --- |
| Markdown | `markdown` |
| JSON | `json` |
| JSON with Comments | `jsonc` |
| JavaScript | `javascript` |
| TypeScript | `typescript` |
| Python | `python` |

対象ファイルを開いたとき、ステータスバーに表示される言語モードからlanguage IDを確認できる。拡張子とlanguage IDの対応はCSpellの公式一覧で確認する。

### 設定例

すべてのファイル種別を対象外にして、Markdownとプレーンテキストだけを対象にする例。

```json
{
  "cSpell.enabledFileTypes": {
    "*": false,
    "markdown": true,
    "plaintext": true
  }
}
```

特定の種類だけを対象外にする例。

```json
{
  "cSpell.enabledFileTypes": {
    "*": true,
    "json": false,
    "jsonc": false
  }
}
```

なお、設定対象はファイル種別全体である。特定のファイル名やフォルダーだけを除外したい場合は、CSpellの`ignorePaths`など、パスを対象にする設定を使い分ける。

### 古い設定名について

`cSpell.enabledLanguageIds` や `cSpell.enableFiletypes` は以前使われていた設定名で、現在は `cSpell.enabledFileTypes` が推奨される。既存設定を移行するときは、拡張機能のバージョンと設定スキーマを確認する。

## 参考資料

- [Files, Folders, and Workspaces | VS Code Spell Checker](https://streetsidesoftware.com/vscode-spell-checker/docs/configuration/files-folders-and-workspaces)
  - `cSpell.enabledFileTypes` の用途、ワイルドカード、ファイル種別の有効・無効設定を確認
  - 参照日: 2026-09-10
- [File Types and Extensions | CSpell](https://cspell.org/docs/Configuration/file-types)
  - CSpellが扱う拡張子とファイル種別の一覧を確認
  - 参照日: 2026-09-10
- [User and workspace settings | Visual Studio Code](https://code.visualstudio.com/docs/configure/settings)
  - ユーザー設定とワークスペース設定の保存場所・適用範囲を確認
  - 参照日: 2026-09-10

## 更新履歴

- 2026-09-10: CSpellのファイル種別ごとのスペルチェック設定を調査して初版を作成
