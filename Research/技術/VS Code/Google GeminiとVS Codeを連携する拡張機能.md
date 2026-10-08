---
作成日: 2026-10-08
更新日: 2026-10-08
タグ:
  - Google Gemini
  - VS Code
  - Gemini Code Assist
  - Gemini CLI
状態: 完了
---

# Google GeminiとVS Codeを連携する拡張機能

## 概要

Google GeminiをVS Codeから利用する方法を調べ、Google公式拡張機能と、Gemini APIを接続できる代表的なサードパーティー拡張機能を比較する。

## 結論

Google公式の拡張機能は存在する。VS Code内でコード補完、チャット、デバッグ、テスト生成などを使いたい場合は **Gemini Code Assist** が第一候補である。ただし、2026-06-18以降は個人向けのGemini Code Assist、Google AI Pro、Google AI Ultraのアカウントではリクエストを処理しなくなっており、現在はGemini Code Assist StandardまたはEnterpriseの契約が必要になる。

Gemini CLIをターミナル中心で使い、VS Codeの選択範囲や差分表示と連携したい場合は **Gemini CLI Companion** が適している。この拡張機能はGemini CLIを別途インストールして使うため、Gemini Code Assistとは用途が異なる。

Google AI Studioなどで取得したGemini APIキーを使いたい場合は、**Continue** または **Cline** のような拡張機能にGeminiをプロバイダーとして設定する方法もある。APIキーの管理、利用料金、送信するコードの扱いは、選択したサービスの規約と設定を確認する必要がある。

## 詳細

### 1. Gemini Code Assist（Google公式）

拡張機能名は **Gemini Code Assist**、Marketplaceの識別子は `Google.geminicodeassist` である。自然言語チャット、コード補完、コード生成、デバッグ、ユニットテスト生成、ドキュメントやコード例の出典表示に対応する。Google Cloud、gcloud CLI、KRM、Terraformなど、Googleのクラウド開発に関係する作業にも対応している。

VS Codeの拡張機能ビューで `Gemini Code Assist` を検索するか、Marketplaceの公式ページからインストールできる。

ただし、公式の廃止告知では、2026-06-18以降、個人向けGemini Code Assist、Google AI Pro、Google AI UltraのアカウントはIDE拡張機能とGemini CLIでリクエストを処理できないと案内されている。Gemini Code Assist StandardまたはEnterpriseの契約は影響を受けない。したがって、個人のGoogleアカウントで無料のGeminiをVS Codeから使う目的だけなら、インストールできても利用できない可能性がある。

### 2. Gemini CLI Companion（Google公式）

拡張機能名は **Gemini CLI Companion**、Marketplaceの識別子は `Google.gemini-cli-vscode-ide-companion` である。Gemini CLIとVS Codeを接続し、次の機能を提供する。

- VS Codeで開いているファイルのコンテキストをGemini CLIへ渡す
- カーソル位置や選択テキストをGemini CLIから参照する
- Gemini CLIが提案した変更をVS Codeのネイティブ差分画面で確認、編集、適用する
- コマンドパレットの `Gemini CLI: Run` からGemini CLIを起動する

利用にはVS Code 1.99.0以上と、別途インストールしたGemini CLIが必要である。Gemini CLIをターミナルで使う人が、編集対象や差分をVS Codeで確認するための連携機能であり、単体のコード補完拡張機能ではない。

### 3. Gemini APIを使うサードパーティー拡張機能

#### Continue

ContinueはVS CodeのAI開発支援拡張機能で、設定のプロバイダーにGeminiを指定し、Gemini APIキーを登録できる。Google AI Studioで発行したAPIキーを自分で設定して、利用するモデルや構成を管理したい場合に向いている。

#### Cline

ClineはVS Code上で動作するエージェント型の拡張機能で、設定画面のAPIプロバイダーにGoogle Geminiを選択できる。複数ファイルの編集やターミナル操作を含むエージェント機能を使いたい場合の候補になる。

ContinueとClineはGoogle公式拡張機能ではない。Gemini APIの利用料、レート制限、APIキー漏えい対策、プロンプトやソースコードの送信先を確認してから利用する。

### 目的別の選び方

| 目的 | 候補 | 注意点 |
| --- | --- | --- |
| Google公式のコード補完・チャットを使う | Gemini Code Assist | StandardまたはEnterprise契約が必要。個人向けアカウントは2026-06-18以降利用不可 |
| Gemini CLIをターミナル中心に使い、VS Codeで差分を確認する | Gemini CLI Companion | Gemini CLIとVS Code 1.99.0以上が必要 |
| Gemini APIキーとモデル設定を自分で管理する | Continue | APIキーと設定ファイルを安全に管理する |
| 複数ファイル編集などのエージェント機能を使う | Cline | 実行前の確認、ワークスペース権限、API利用料を確認する |

### 最初に試す手順

Google CloudのStandardまたはEnterprise契約がある場合は、VS Codeの拡張機能ビューで `Gemini Code Assist` を検索し、発行元が **Google** であることを確認してインストールする。

Gemini CLIをすでに使っている場合は、Marketplaceで `Gemini CLI Companion` を検索するか、Gemini CLIのIDE連携機能からインストールする。拡張機能のインストール後、コマンドパレットから `Gemini CLI: Run` を実行して連携を確認する。

APIキー方式を選ぶ場合は、まずContinueまたはClineの公式ドキュメントに従ってプロバイダーを設定する。APIキーをソースコード、ワークスペース設定、共有ログへ直接記録しない。

## 参考資料

- [Gemini Code Assist - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=Google.geminicodeassist)
  - 参照日: 2026-10-08
- [Gemini Code Assist overview - Google for Developers](https://developers.google.com/gemini-code-assist/docs/overview)
  - 参照日: 2026-10-08
- [Gemini Code Assist consumer accounts - Google for Developers](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals)
  - 参照日: 2026-10-08
- [Gemini CLI Companion - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=Google.gemini-cli-vscode-ide-companion)
  - 参照日: 2026-10-08
- [IDE integration - Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/main/docs/ide-integration/index.md)
  - 参照日: 2026-10-08
- [How to Configure Gemini with Continue](https://docs.continue.dev/customize/model-providers/top-level/gemini)
  - 参照日: 2026-10-08
- [Google Gemini - Cline](https://docs.cline.bot/provider-config/google-gemini)
  - 参照日: 2026-10-08

## 更新履歴

- 2026-10-08: Google公式の2拡張機能、APIキー方式の候補、個人向けアカウントの提供停止を調査して初版を作成
