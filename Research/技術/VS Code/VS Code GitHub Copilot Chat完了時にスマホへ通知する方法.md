---
作成日: 2026-09-04
更新日: 2026-09-10
タグ:
  - VS Code
  - GitHub Copilot
  - スマホ通知
  - ntfy
状態: 完了
---

# VS Code GitHub Copilot Chat完了時にスマホへ通知する方法

## 概要

VS CodeでGitHub Copilot Chatの作業が終わったとき、PCの前を離れていても
スマートフォンで気付ける方法を調べた。ローカルのVS Code Chat、Copilot CLI、
GitHubのCloud Agentを分け、実現性、設定量、セキュリティ上の注意点を比較する。

## 結論

PC上で右下の通知を見逃しやすい場合、まずVS Code標準の
`chat.notifyWindowOnResponseReceived`を`always`にする。これはChatの応答を受信した
ときにOS通知を出す設定で、通知を選ぶと該当Chatへ戻れる。エージェントが入力や確認を
待っていることも見逃したくない場合は、`chat.notifyWindowOnConfirmation`も`always`にする。
ただし、標準機能の通知先を別の場所へ移す設定や、Copilot応答専用の通知音設定は確認
できなかった。音で知らせたい場合は、第三者拡張を導入する方法が候補になる。

用途別の推奨は次のとおりである。

| 用途 | 推奨方法 | 評価 |
| --- | --- | --- |
| ローカルのVS Code Chatをそのまま監視 | **Productive Vibe Coder**などの拡張機能でOS通知を出す | 導入が最短。ただし第三者拡張の動作確認と権限確認が必要 |
| ローカル通知をスマホにも転送 | 上記拡張のGitHub通知機能、または対応拡張からntfy等へ送信 | スマホへ届くが、PATや通知トークンを扱う場合がある |
| Copilot CLIやリモートセッションを使える | **GitHub Mobileのライブ通知** | 公式機能。対象はリモートCopilot CLI/Cloud Agent系で、ローカルChatの全完了を直接通知する機能とは区別が必要 |
| 自分で確実に通知処理を組む | Copilot CLI/Cloud Agentの`sessionEnd`または`agentStop` Hookからntfy、Pushover、Telegram等のHTTPS APIを呼ぶ | 柔軟だが、Hook対象とトークン管理を自分で設計する必要がある |

したがって、**今のローカルVS Code Chatを変えずに試すなら、まずOS通知対応の
拡張機能を試し、スマホ通知が必要ならGitHub通知連携またはntfy連携を検討する**
のが現実的である。公式機能だけを優先するなら、ローカルChatではなく
GitHub Mobileが対応するリモートCopilot CLI/Cloud Agentのセッションへ作業を
寄せる方法が安全である。

## 詳細

### 0. VS Code標準設定（まず試す方法）

VS Code公式ドキュメントでは、次の2設定が案内されている。設定画面で名前を検索するか、
`settings.json`へ記載する。

```json
{
  "chat.notifyWindowOnResponseReceived": "always",
  "chat.notifyWindowOnConfirmation": "always"
}
```

- `chat.notifyWindowOnResponseReceived`: Chatの応答を受信したときのOS通知。
- `chat.notifyWindowOnConfirmation`: エージェントが入力または確認を必要として停止した
  ときのOS通知。
- 値は`off`、`windowNotFocused`（既定値）、`always`。`always`はVS Codeウィンドウが
  前面にある場合も通知する。

これは「右下以外に表示する」設定ではなく、WindowsのOS通知を確実に出す設定である。
Windows側の通知バナー、通知音、通知の表示時間は、Windowsの
**設定 > システム > 通知 > Visual Studio Code**で調整する。通知音だけで知らせたい
場合や、より目立つ通知が必要な場合は、拡張機能の検討が必要である。

### 0.1 音で知らせる第三者拡張

Marketplaceの**Copilot Chime**は、Copilotのタスク完了、入力要求、注意喚起などで音を
鳴らせる。音量、イベント別の有効・無効、音の種類を設定できる。一方、第三者拡張で
あり、Copilot Chatの内部仕様変更で動作しなくなる可能性がある。Marketplaceの説明では、
通常の応答終了を自動検知するだけでなく、プロンプトに`#chime`を含めて完了通知を
依頼する使い方も案内されているため、導入後に自分のAgentモードで期待どおり鳴るか
確認する。

### 1. ローカルのVS Code Chat

VS CodeのGitHub Copilot Chatには、2026-09-04時点で、Chatの応答終了を任意の
HTTPエンドポイントへ送る設定が公式ドキュメントで確認できない。VS Codeの機能要望
には「応答終了、コード生成終了、承認待ちなどでHTTPリクエストを送りたい」という
提案があるが、確認したIssueは重複としてクローズされている。

Marketplaceの**Productive Vibe Coder**は、Copilot Chatの終了または応答待ちを
検出し、Windows/macOS/LinuxのOS通知やサウンドを出す拡張として掲載されている。
任意のプライベートGitHubリポジトリへIssueを作成し、GitHubの通知ベル、GitHub
Mobile、メールへ知らせる機能も説明されている。

ただし、これはMicrosoftまたはGitHub公式のVS Code拡張ではない。GitHub通知機能を
使う場合はPATを設定する手順が掲載されているため、次を確認してから使う。

- 拡張の公開元、ソースコード、更新状況、要求権限を確認する。
- PATをソースコード、設定ファイル、同期設定へ平文で保存しない。
- PATは必要最小限の権限にし、用途を終えたら失効させる。
- Copilotの回答やソースコードを外部通知サービスへ送らず、完了時刻や短い状態だけを送る。

拡張機能が将来のCopilot Chat内部仕様変更で検出できなくなる可能性もあるため、
導入後に「完了」「入力待ち」「エラー」の3状態でテストする。

### 2. GitHub Mobileのライブ通知

GitHubの公式発表では、GitHub Mobileはリモートで動くCopilot CLIセッションの
進行中、入力待ち、アイドル、終了をライブ通知できる。VS Codeなどから開始した
対応するリモートセッションも対象に含まれる。iOSは17.2以上でLive Activities、
Androidは16以上でLive Update通知に対応し、それより古いAndroidでも進捗通知は
受け取れると説明されている。

これは「GitHub Mobile対応のリモートCopilot CLI/Cloud Agentセッション」を
スマホで追跡する方法であり、PC上のローカルChat応答すべてに対する汎用通知設定と
同じではない。現在の作業がローカルAgent Chatか、リモートCLI/Cloud Agentかを
最初に確認する必要がある。

### 3. Hooksからpush通知サービスを呼ぶ

GitHubのHooks公式資料では、Copilot Cloud AgentとGitHub Copilot CLIで、
`sessionEnd`、`agentStop`、`errorOccurred`などのイベントにコマンドを実行できる。
WindowsではHook設定に`powershell`コマンドを指定できるため、PowerShellから
通知サービスのHTTPS APIを呼べる。

例として、ntfyはHTTPのPOST/PUTでトピックへ通知でき、Androidアプリで受信できる。
トピック名は認証なしの場合に実質的なパスワードとなるため、推測困難な名前を使い、
公開リポジトリやログへURLを残さない。Pushoverはアプリトークンとユーザーキーを
HTTPS POSTで送る方式、TelegramはBot APIの`sendMessage`を使う方式である。

ただし、Hooksの公式適用先はCloud AgentとCopilot CLIであり、ローカルのVS Code
Chatへそのまま適用できるとは書かれていない。Hookは同期実行されてAgentの処理を
ブロックするため、通知処理は短時間で終えるか、別プロセスへ安全に引き渡す。
入力JSONに含まれるプロンプトやファイル情報を通知本文へ無制限に入れない。

### 4. 現実的な選び方

1. **まずPCだけでよい**: Productive Vibe Coder等のOS通知を有効にする。
2. **スマホで完了だけ知りたい**: 拡張のGitHub通知連携を、最小権限のPATと
   専用プライベートリポジトリで試す。
3. **外部サービスへコード情報を出したくない**: ntfy等へ送る本文を
   「Copilot完了」「入力待ち」などの固定文にし、トークンを環境変数や安全な
   秘密情報ストアから読む。
4. **公式サポートを優先**: GitHub Mobileが対象とするリモートCopilot CLI/Cloud
   Agentへ作業方式を変更する。

## 参考資料

- [Use chat in VS Code - Get notified about chat responses](https://code.visualstudio.com/docs/chat/chat-overview#_get-notified-about-chat-responses)
  - `chat.notifyWindowOnResponseReceived`、`chat.notifyWindowOnConfirmation`の用途と、`off`、`windowNotFocused`、`always`の値を確認。
  - 参照日: 2026-09-10
- [Copilot Chime - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=hatchetsoftwarellc.copilot-chime)
  - Copilotの完了・入力要求などを音で通知する機能と設定項目を確認。
  - 参照日: 2026-09-10
- [About hooks for GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/hooks)
  - 参照日: 2026-09-04
- [Live coding agent notifications on GitHub Mobile now support remote Copilot CLI sessions](https://github.blog/changelog/2026-07-08-github-mobile-live-notifications-for-copilot-cli-sessions/)
  - 参照日: 2026-09-04
- [Productive Vibe Coder - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=Momskid.productive-vibe-coder)
  - 参照日: 2026-09-04
- [Notification when Copilot is Done #260699](https://github.com/microsoft/vscode/issues/260699)
  - 参照日: 2026-09-04
- [ntfy: Publishing](https://docs.ntfy.sh/publish/)
  - 参照日: 2026-09-04
- [Pushover Message API](https://pushover.net/api)
  - 参照日: 2026-09-04
- [Telegram Bot API: sendMessage](https://core.telegram.org/bots/api#sendmessage)
  - 参照日: 2026-09-04

## 更新履歴

- 2026-09-10: VS Code標準の応答受信・確認待ち通知設定と、音で知らせる第三者拡張の候補を追加
- 2026-09-04: VS CodeローカルChat、GitHub Mobile、Hooks、通知サービス、第三者拡張を比較し、スマホ通知の選択基準とセキュリティ注意点を整理
