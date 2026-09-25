---
作成日: 2026-08-27
更新日: 2026-08-31
タグ:
  - VS Code
  - ショートカット
  - 編集
  - Git
  - タスク
状態: 完了
---

# VS Codeの便利機能

## 概要

QiitaとZennで紹介されているVS Codeの便利機能を調べ、日常的な編集・プロジェクト操作で特に再利用しやすい標準機能を整理する。

## 結論

まず習得する価値が高いのは、コマンドパレット、Quick Open、複数カーソル、組み込みGit、タスク、プロファイルである。いずれも拡張機能なしで利用できる。特に、キーボードで操作名やファイル名を検索する習慣と、繰り返し編集で複数カーソルを使う習慣を付けると、VS Code全体の操作を効率化しやすい。

## 詳細

### まず覚える操作

| 機能 | Windows の既定ショートカット | 主な用途 |
| --- | --- | --- |
| コマンドパレット | `Ctrl+Shift+P` または `F1` | 実行したい機能名を検索する。設定、表示切替、Git、タスクなどの入口になる。 |
| Quick Open | `Ctrl+P` | ファイル名を入力してすばやく開く。 |
| 次の一致を選択 | `Ctrl+D` | 選択中の文字列と同じ次の箇所を追加選択する。繰り返し編集向け。 |
| すべての一致を選択 | `Ctrl+Shift+L` | 選択中の文字列の全出現箇所にカーソルを置く。 |
| 縦方向の複数カーソル | `Ctrl+Alt+Up` / `Ctrl+Alt+Down` | 同じ列の複数行を同時に編集する。Linuxの既定値は`Shift+Alt+Up` / `Shift+Alt+Down`。グラフィックスドライバーなどと競合する場合がある。 |
| 任意位置へのカーソル追加 | `Alt+Click` | 離れた箇所を同時に編集する。 |

Qiita・Zennの記事では、複数カーソルは同じ語句の置換、複数行への接頭辞・接尾辞の追加、設定値の一括編集で有用と紹介されている。ただし、識別子の名称変更では、言語機能が利用できる場合は `F2` の「Rename Symbol」を優先する。複数カーソルでは文字列として一致した別の意味の箇所まで変更するおそれがあるためである。

### 組み込みGitとタイムライン

ソース管理ビューでは、変更の確認、ステージング、コミット、ブランチの切替などをGUIから行える。差分を確認してからステージングする流れにすると、意図しないファイルをコミットに含めにくい。

エクスプローラーのタイムラインは、選択したファイルに関係する履歴を時系列で確認するためのビューである。Git履歴を利用するにはリポジトリが必要だが、ローカル履歴を利用できる場合もある。過去の内容を確認・比較する用途には便利だが、バックアップの代わりにはしない。重要な変更はGitへコミットし、リモートへpushする。

### タスクで定型操作を再利用する

`Tasks: Run Task` から、ワークスペースで定義したビルド、テスト、整形などの定型コマンドを実行できる。プロジェクト固有の操作は `.vscode/tasks.json` に定義しておくと、チーム内で同じ手順を共有しやすい。タスク定義に秘密情報を直接書かず、必要なら環境変数や安全な資格情報管理を使う。

### プロファイルで用途を分離する

プロファイルは、設定、拡張機能、テーマ、キーボードショートカット、スニペット、
タスク、MCPサーバーなどを用途別に切り替える機能である。例えば「普段の開発」
「Python作業」「発表・デモ」で分けると、不要な拡張機能や設定の干渉を減らせる。
現在はProfiles editorから作成、切替、エクスポート、インポートを管理できる。

### おすすめの導入順

1. `Ctrl+P` と `Ctrl+Shift+P` を使い、ファイルとコマンドを検索して開く。
2. 繰り返し編集では `Ctrl+D`、全件なら `Ctrl+Shift+L` を試す。
3. ソース管理ビューで差分を確認し、必要な変更だけをステージングする。
4. よく実行するテストやビルドをタスクにする。
5. 拡張機能や設定が増えたら、用途別プロファイルへ分ける。

## 参考資料

- [Visual Studio Code 入門: 1回: コマンドパレット](https://qiita.com/wraith13/items/f7c9f60a7fe3b0d1e4aa)
  - 参照日: 2026-08-31
- [VSCode マルチカーソルの活用方法を基礎から徹底解説](https://qiita.com/htcd/items/a77b3a8a314db3d56700)
  - 参照日: 2026-08-31
- [VSCode 個人的に便利機能まとめ](https://zenn.dev/0bucoujevh/articles/eac554c2b8ae0e)
  - 参照日: 2026-08-31
- [VSCode マルチカーソル、使ってますか？](https://zenn.dev/hacobell_dev/articles/vscode-multi-cursor)
  - 参照日: 2026-08-31
- [User interface - Command Palette](https://code.visualstudio.com/docs/editing/userinterface#_command-palette)
  - 参照日: 2026-08-31
- [Basic editing](https://code.visualstudio.com/docs/editing/codebasics#_multiple-selections-multicursor)
  - 参照日: 2026-08-31
- [Tasks in Visual Studio Code](https://code.visualstudio.com/docs/debugtest/tasks)
  - 参照日: 2026-08-31
- [Profiles](https://code.visualstudio.com/docs/configure/profiles)
  - 参照日: 2026-08-31
- [User interface - Timeline view](https://code.visualstudio.com/docs/editing/userinterface#_timeline-view)
  - 参照日: 2026-08-31
- [Using Git source control in VS Code](https://code.visualstudio.com/docs/sourcecontrol/overview)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、移転した公式URL、Linuxの複数カーソル、
  Profiles editorの現行仕様、Git公式資料を反映
- 2026-08-27: Qiita・Zennの記事と公式資料を基に初版を作成
