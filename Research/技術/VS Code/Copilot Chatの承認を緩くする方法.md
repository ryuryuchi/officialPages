---
作成日: 2026-08-25
更新日: 2026-08-31
タグ:
  - VS Code
  - GitHub Copilot
  - Copilot Chat
  - 承認
状態: 完了
---

# VS Code GitHub Copilot Chatの承認を緩くする方法

## 概要

VS Code の GitHub Copilot Chat で、エージェントがファイル編集、ターミナル実行、外部アクセスを行うたびに表示される承認を減らす方法を調査した。

## 結論

最初に試す方法は、チャット入力欄の権限ドロップダウンで **Assisted permissions** を選ぶことである。リスクが低いとモデルが判定したツール呼び出しを自動承認し、リスクがある操作だけ確認できるため、承認回数と安全性のバランスがよい。

特定の操作だけ毎回承認される場合は、確認ダイアログで「現在のワークスペース」または「今後すべて」を選ぶか、`Chat: Manage Tool Approval` コマンドで対象ツールを恒久承認する。ターミナルは `chat.tools.terminal.autoApprove` で、開発に必要なコマンドだけを許可リストへ追加する。

**Bypass Approvals** と **Autopilot** は全ツールを自動承認する。信頼できるローカルのリポジトリだけで使い、通常は Agent Sandbox を有効にしてから選ぶ。外部サイトの取得結果、MCP サーバー、秘密情報を含むファイル、破壊的なコマンドまで自動承認され得るため、常用は推奨しない。

## 詳細

### すぐに承認回数を減らす手順

1. VS Code の Chat ビューでエージェントのチャットを開く。
2. チャット入力欄にある権限（Permissions）ドロップダウンを開く。
3. **Assisted permissions** を選ぶ。
   - 初回は警告を確認する。
   - この選択は現在のチャットセッションに適用される。
4. 新しいセッションでも既定にしたい場合は、設定で `chat.permissions.default` を希望する権限レベルに変更する。

`Assisted permissions` が表示されない場合は、設定 `chat.assistedPermissions.enabled` を有効化する。この権限レベルは Agent Host 上で動作するエージェントで利用できる。

### 操作別に恒久承認する方法

確認ダイアログでは、1回だけでなく、現在のセッション、現在のワークスペース、以後すべての呼び出しという範囲を選択できる。よく使う安全な操作には「現在のワークスペース」を選ぶと、別プロジェクトには影響を広げずに済む。

まとめて管理するには、コマンドパレット（Windows: `Ctrl+Shift+P`）で **Chat: Manage Tool Approval** を実行する。MCP サーバーや拡張機能ごと、または個別ツールごとに、次の承認を設定できる。

- **Pre-approval**: 実行前の確認を省略する。
- **Post-approval**: 外部データの実行結果をチャットへ渡す前の確認を省略する。

不要になった恒久承認は **Chat: Reset Tool Confirmations** で全消去できる。個別に見直す場合は `Chat: Manage Tool Approval` を使う。

### ターミナル承認を減らす方法

ターミナルは単一ツールで任意のコマンドを実行できるため、ツール全体ではなくコマンドごとに承認される。VS Code は既定で一部の安全なコマンドを自動承認し、`rm` や `del` のような危険なコマンドは手動承認を要求する。

設定 JSON の `chat.tools.terminal.autoApprove` に、日常的に使う読み取り専用または開発用コマンドを追加する。例:

```jsonc
{
  "chat.tools.terminal.autoApprove": {
    "mkdir": true,
    "/^git (status|show\\b.*)$/": true,
    "del": false
  }
}
```

- 値 `true` は自動承認、`false` は常に手動承認である。
- `/.../` で正規表現を指定できる。
- 複合コマンドでは、すべてのサブコマンドが許可ルールに一致し、拒否ルールに一致しない場合だけ自動承認される。
- `chat.tools.terminal.enableAutoApprove` を `false` にすると、ターミナルの自動承認を完全に無効にできる。

最初から `npm` や `git` 全体を許可するより、`git status`、テスト実行、ビルド実行など実際に必要なコマンドに絞った正規表現ルールから始めるのが安全である。

### 全承認を省略する選択肢

| 選択肢 | 動作 | 推奨用途 |
| --- | --- | --- |
| Default Approvals | 設定済みの個別承認ルールに従う | 通常の利用 |
| Assisted permissions | モデルが低リスクと判断した操作を自動承認 | 承認を減らす第一候補 |
| Bypass Approvals | すべてのツール呼び出しを自動承認 | 信頼済みのローカル作業 |
| Autopilot | 全自動承認に加え、完了まで自律反復する | 小さく隔離した、明確な作業 |

**Bypass Approvals** は権限ドロップダウン、**Autopilot** はエージェントモードのドロップダウンから選択する。いずれも初回は警告の確認が必要であり、組織の管理ポリシーがある場合は、そのポリシーによる承認・拒否が優先される。

Autopilotはエラーの自動再試行と確認質問への自動回答も行う。
`chat.autopilot.advanced.enabled`を有効にするAdvanced Autopilot（Preview）では、
別の小型モデルが各ターン後に完了判定を行い、未完了なら次のターンへ指針を渡す。

### 安全に緩くするための推奨構成

1. 信頼できるフォルダーだけをワークスペースとして開く。
2. **Assisted permissions** を使う。
3. 頻繁に使う安全なツールはワークスペース単位で Pre-approval を設定する。
4. ターミナルは必要なコマンドだけ `chat.tools.terminal.autoApprove` に追加し、`del` などは明示的に `false` のままにする。
5. macOS、Linux、WSL2で利用できる場合は Agent Sandbox（Preview）を有効化する。
   サンドボックス内で実行するターミナルコマンドは、ファイルシステムとネットワークの
   境界で制限され、VS Code は確認なしで実行できる。Windowsネイティブは対象外である。
6. Web 取得の応答内容、MCP ツール、`.env` などの秘密情報を含み得るファイルの編集は、恒久承認の対象にしない。

URL 取得はリクエスト先の承認と、取得結果をチャットへ渡す前の承認の2段階である。`chat.tools.urls.autoApprove` で URL やドメインの自動承認を設定できるが、ユーザー生成コンテンツを含むサイトでは、結果の確認を残すべきである。

## 参考資料

- [Manage approvals and permissions - Visual Studio Code](https://code.visualstudio.com/docs/agents/run/approvals)
  - 参照日: 2026-08-31
- [Trust and safety - Visual Studio Code](https://code.visualstudio.com/docs/agents/concepts/trust-and-safety)
  - 参照日: 2026-08-31
- [Build with agents in VS Code - Visual Studio Code](https://code.visualstudio.com/docs/agents/overview)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLと承認仕様を再確認し、最小権限のコマンド例、
  管理対象ルールの優先、Advanced Autopilot、Sandboxの対応OSとPreview状態を反映
- 2026-08-25: 初版を作成
