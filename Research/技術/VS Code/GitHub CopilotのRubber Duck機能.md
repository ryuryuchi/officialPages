---
作成日: 2026-08-27
更新日: 2026-08-31
タグ:
  - VS Code
  - GitHub Copilot
  - Rubber Duck
  - AIエージェント
状態: 完了
---

# GitHub CopilotのRubber Duck機能

## 概要

VS Code 1.135で追加されたRubber Duckについて、機能の目的、仕組み、
使い方、利用条件、注意点を公式資料から整理する。

## 結論

Rubber Duckは、Copilotの計画、実装、テストを別系統のAIモデルに批評させる、
読み取り専用の組み込みレビューエージェントである。一般的な
「ラバーダック・デバッグ」のように考えを言語化するだけでなく、別モデルが
問題点と修正案を返す点が特徴である。

VS Codeでは、2026年8月26日公開の1.135でCopilot Agent Hostセッションから
利用できる実験的機能として追加された。チャット入力欄で
`/rubber-duck <質問>`を実行する。複雑な作業ではCopilotが自動的に呼び出すこともある。
VS Code 1.135のリリースノートではVS Code統合を実験的機能としている一方、
Copilot CLI版は2026年6月2日に一般提供された。

Rubber Duck自身はファイルを編集せず、環境を変更するコマンドも実行しない。
ただし、別モデルによる追加の推論処理が発生するため、待ち時間とモデル使用量は
増える。

## 詳細

### 追加時期と位置付け

- GitHub Copilot CLIでは、2026年6月2日にRubber Duckの一般提供が告知された。
- VS Codeでは、2026年8月26日公開のバージョン1.135で、Copilot Agent Host
  のCopilotハーネス向け実験的機能として追加された。
- VS CodeのCopilot Agent HostはCopilot SDKを使用しており、Copilot CLIや
  GitHub Copilotアプリなどと動作や機能をそろえる仕組みである。このため、
  CLIで先に提供されたRubber DuckをVS Code内でも利用できるようになったと
  理解できる。

CLIでは一般提供、VS Code統合では実験的機能という位置付けの違いに注意する。

### 何をする機能か

メインのCopilotエージェントが現在の計画、設計、実装、テストをRubber Duckへ
渡すと、Rubber Duckは次のような実質的な問題を探す。

- バグやロジックエラー
- セキュリティ上の脆弱性
- 設計上の欠陥やアンチパターン
- 性能上のボトルネック
- テスト範囲の不足
- 見落とされた前提やエッジケース

指摘は、作業を成功させるために修正必須の「Blocking issues」、品質向上のため
修正すべき「Non-blocking issues」、優先度の低い改善案である「Suggestions」に
分類される。スタイル、書式、命名、軽微なリファクタリングなど、成否に影響しない
指摘は原則として対象外である。

Rubber Duckは指摘内容、影響、具体的な修正案を返す。メインエージェントが
その批評を要約し、採用するかを判断して作業を続ける。Rubber Duck自身には
コードベースを調査する読み取り専用ツールへのアクセスがあるが、ファイル編集や
環境を変更するコマンドの実行はできない。

### 別モデルを使う理由

Rubber Duckは、メインセッションとは異なる系統のモデルを批評役として自動選択
する。たとえばメインがClaude系なら、GPT系が選ばれる場合がある。同じモデルに
自己評価させるよりも、学習傾向、バイアス、失敗パターンが異なる視点を得ることが
目的である。

公式ドキュメント上、メインセッションがClaudeまたはGPTの大規模言語モデルを
使用し、適切な補完モデルを利用できる場合に限って動作する。セッション途中で
メインモデルを変更した場合、次回の呼び出し時に新しい組み合わせが自動選択される。

### VS Codeでの使い方

1. VS Code 1.135以降で新しいエージェントセッションを開く。
2. Session Targetで`Copilot`ハーネスを選ぶ。`Local`ハーネスでは利用しない。
3. メインモデルとしてClaude系またはGPT系を選ぶ。
4. チャット入力欄で、たとえば次のように入力する。

```text
/rubber-duck What edge cases are missing?
```

自然言語で「ここまでの変更について別の視点でレビューして」のように依頼する
こともできる。コマンドが候補に表示されない場合は、次を確認する。

- VS Codeが1.135以降か
- Local、Claude、CodexではなくCopilot Agent Hostセッションを使っているか
- メインモデルがClaude系またはGPT系か
- 組み合わせ可能な補完モデルへのアクセスがあるか
- 実験的機能の段階的提供対象になっているか

最後の項目は、VS Code 1.135のリリースノートが全ユーザーへの段階的展開を
案内しており、Rubber Duckも実験的機能とされていることからの実務上の確認事項
である。公式資料はRubber Duck専用の有効化設定名を案内していない。

### 自動的に呼び出される場面

複雑な作業では、Copilotが効果の高いタイミングを選んでRubber Duckを自動的に
呼び出す場合がある。

- 複雑な変更の計画後、実装を始める前
- 複雑な実装の途中または直後
- テスト作成後
- 失敗の繰り返しや予期しない結果が発生したとき

小規模で明確な変更では通常スキップされる。常にレビューしてほしい場合は
`/rubber-duck`または自然言語で明示的に依頼する。

### 従来機能との違い

| 対象 | 主な役割 | ファイル変更 | 特徴 |
|---|---|---:|---|
| メインのCopilotエージェント | 計画、実装、テスト、修正 | する | タスクを最後まで進める実行役 |
| Rubber Duck | メインエージェントの成果を批評 | しない | 別系統モデルによる第二の意見 |
| 一般的なラバーダック・デバッグ | 人が説明して自分で気付く | 人が行う | 原則として相手から回答はない |
| コードレビュー | 変更済みコードを検査 | 通常しない | Rubber Duckは計画やテストも途中段階で検査できる |

Autopilotは承認待ちを減らしてメインエージェントが自律的に作業を続けるための
モードであり、批評役を追加するRubber Duckとは目的が異なる。

### 効果に関する公式評価

GitHubがSWE-Bench Proで行った評価では、Claude Sonnet 4.6とGPT-5.4の
Rubber Duckを組み合わせると、Sonnet単体とClaude Opus 4.6単体の性能差の
74.7%を埋めたとしている。3ファイル以上かつ70ステップ以上を要する難しい問題
では、Sonnet単体より3.8%高く、3回の試行で特定した最難関問題では4.8%高かった。

これはGitHub自身による特定モデル、特定ベンチマークでの評価である。すべての
モデル構成や実務タスクで同じ改善率になることを保証する結果ではない。

### 向いている用途

- 複数ファイルにまたがる変更や大規模リファクタリング
- アーキテクチャや設計方針を確定する前のレビュー
- 見落としの影響が大きい重要な変更
- テストケースやエッジケースの不足確認
- エージェントが同じ失敗を繰り返しているときの打開

### 注意点

- 追加のモデル呼び出しにより、応答時間とモデル使用量が増える。
- 適切な補完モデルが利用できなければ動作しない。
- 指摘は助言であり、正しさは保証されない。重要な変更ではテストや人による
  レビューも必要である。
- 読み取り専用なのはRubber Duckであり、批評を受け取ったメインエージェントは
  権限設定に応じてファイル変更やコマンド実行を行える。
- VS Codeでは実験的機能のため、仕様、提供条件、UIが変更される可能性がある。

## 参考資料

- [Visual Studio Code 1.135](https://code.visualstudio.com/updates/v1_135)
  - 参照日: 2026-08-31
- [Choose and use an agent harness](https://code.visualstudio.com/docs/agents/run/agent-harnesses)
  - 参照日: 2026-08-31
- [About the rubber duck agent](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck)
  - 参照日: 2026-08-31
- [Copilot CLI: Improved UI, rubber duck, prompt scheduling, and voice input](https://github.blog/changelog/2026-06-02-copilot-cli-improved-ui-rubber-duck-prompt-scheduling-and-voice-input/)
  - 参照日: 2026-08-31
- [GitHub Copilot CLI combines model families for a second opinion](https://github.blog/ai-and-ml/github-copilot/github-copilot-cli-combines-model-families-for-a-second-opinion/)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、VS Code統合とCLI版の提供状態の違い、
  Copilotハーネス限定、対応モデルとベンチマークの適用範囲を明確化
- 2026-08-27: 初版を作成
