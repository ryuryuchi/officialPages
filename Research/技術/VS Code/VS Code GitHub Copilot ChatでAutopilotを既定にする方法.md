---
作成日: 2026-08-25
更新日: 2026-08-31
タグ:
  - VS Code
  - GitHub Copilot
  - Autopilot
状態: 完了
---

# VS Code GitHub Copilot ChatでAutopilotを既定にする方法

## 概要

VS CodeのGitHub Copilot Chatで、新しいエージェントセッションの標準モードを
Autopilotにする設定方法を調査した。

## 結論

現行のAgent Hostを使う新しいエージェントセッションでは、ユーザー設定
`settings.json` に次を追加する。

```json
{
  "chat.defaultConfiguration": {
    "mode": "autopilot"
  }
}
```

設定画面を使う場合は、設定検索で `chat.defaultConfiguration` または
`Default Configuration` を検索し、`Mode` を `Autopilot` にする。

Localハーネスなど拡張機能ホスト上のChatではAutopilotが「モード」ではなく
「権限レベル」として扱われるため、次の設定を使う。

```json
{
  "chat.permissions.default": "autopilot"
}
```

## 詳細

### 現行のAgent Hostの場合

VS Code本体の設定定義では、`chat.defaultConfiguration` は新しいエージェント
セッションの初期構成を指定するオブジェクトである。`mode` には
`interactive`、`plan`、`autopilot` を指定できる。したがって、
`mode: "autopilot"` とすると、新規セッションがAutopilotで始まる。

この設定は新規セッションの開始値であり、既に開いているセッションのモードを
一括変更するものではない。既存セッションでは、チャット入力欄のモード選択から
Autopilotへ切り替える。

### 従来の拡張機能ホストの場合

公式ドキュメントでは、Agent Host上のAutopilotはエージェントモード、
拡張機能ホスト上のAutopilotは権限レベルとして区別されている。
拡張機能ホストの新規Chatで既定の権限レベルを指定する設定は
`chat.permissions.default` であり、値 `autopilot` を指定できる。

VS Code 1.124のリリースノートは、当時のAutopilotを権限レベルとして説明し、
新規Chatの既定値を `chat.permissions.default` で変更できると案内されている。
利用中のVS Codeで `chat.defaultConfiguration` が設定候補に出ない場合は、
この従来設定を使用する。

### 設定手順

1. `Ctrl+,` で設定画面を開く。
2. `chat.defaultConfiguration` を検索する。
3. `Mode` を `Autopilot` に変更する。
4. 新しいエージェントセッションを作成し、Autopilotで開始されることを確認する。
5. 設定が見つからない場合は、`chat.permissions.default` を検索して
   `Autopilot` を選ぶ。

`settings.json` を直接編集する場合は、コマンドパレットから
`Preferences: Open User Settings (JSON)` を実行する。全ワークスペースで
既定にしたい場合はユーザー設定へ追加し、特定ワークスペースだけに適用したい
場合はワークスペース設定へ追加する。

### 注意点

- Autopilotは、すべてのツール呼び出しを自動承認し、タスク完了まで自律的に
  反復する。エラーの自動再試行や、確認質問への自動回答も行う。ファイル編集、
  ターミナルコマンド、外部ツールも承認なしで実行される可能性がある。
- ワークスペース外のローカルファイルを `file:` URI で取得する場合、VS Codeの
  組み込み `fetch` ツールは原則として確認対象にする。ただし、ユーザーがチャットの
  プロンプトでその URI を明示した場合、現行実装では自動承認される。この挙動を
  Autopilotの既定化だけで無条件に許可する設定として扱わない。
- ワークスペース外の読み取りを運用上許可する場合は、対象をタスクに必要な
  最小限のファイルに限定し、読み取り専用とする。認証情報、秘密鍵、トークン、
  個人情報を含む可能性があるファイルは、不可欠でユーザーが明示指定した場合以外は
  読み取らない。外部ファイルの作成・更新・削除は、対象パスと操作を明示指定された
  場合だけにする。
- 初回選択時には警告ダイアログが表示される場合がある。
- 組織管理ポリシーはユーザー設定より優先される。組織で
  `chat.tools.global.autoApprove` が無効化されている場合、Autopilotを利用または
  表示できないことがある。管理対象の細粒度ルールはAutopilotより優先される。
- 既定化しても、各セッションの入力欄から別のモードへ随時変更できる。

## 参考資料

- [Manage approvals for agent tools in Visual Studio Code](https://code.visualstudio.com/docs/agents/run/approvals)
  - 参照日: 2026-08-31
- [Visual Studio Code 1.124 Release Notes](https://code.visualstudio.com/updates/v1_124)
  - 参照日: 2026-08-31
- [VS Code setting registration for chat.defaultConfiguration](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/browser/chat.shared.contribution.ts)
  - 参照日: 2026-08-31
- [Agent Host behavior in Visual Studio Code](https://code.visualstudio.com/docs/agents/concepts/agent-host)
  - 参照日: 2026-08-31
- [VS Code built-in fetch tool implementation](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/electron-browser/builtInTools/fetchPageTool.ts)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLと現行設定定義を再確認し、Agent HostとLocalハーネスの
  区別、Autopilotの自動再試行・質問応答、管理対象ルールの優先を反映
- 2026-08-25: ワークスペース外のファイル読み取りに関する確認挙動と安全な運用規定を追記
- 2026-08-25: 初版を作成
