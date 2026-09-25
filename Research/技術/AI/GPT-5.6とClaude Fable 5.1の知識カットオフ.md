---
作成日: 2026-08-26
更新日: 2026-09-07
タグ:
  - GPT-5.6
  - Fable5.1
  - OpenAI
  - Anthropic
  - 知識カットオフ
状態: 完了
---

# GPT-5.6とClaude Fable 5.1の知識カットオフ

## 概要

GPT-5.6シリーズとClaude Fable 5.1について、学習済み知識のカットオフ時期を
OpenAIおよびAnthropicの公式モデル資料で確認した。

## 結論

- **GPT-5.6シリーズ: 2026年2月16日**
  - GPT-5.6 Sol、Terra、Lunaの3モデルすべてで共通。
- **Claude Fable 5.1: 2026年6月**
  - Anthropicは日付までは公表していない。

したがって、公表値上はFable 5.1のほうがGPT-5.6シリーズより新しい時点までの
知識を持つ。ただし、カットオフは学習済み知識の境界を示すものであり、
その日以前の全情報を必ず知っていることを保証するものではない。

## 詳細

### GPT-5.6シリーズ

| モデル | 公式の知識カットオフ |
| --- | --- |
| GPT-5.6 Sol (`gpt-5.6-sol`) | 2026年2月16日 |
| GPT-5.6 Terra (`gpt-5.6-terra`) | 2026年2月16日 |
| GPT-5.6 Luna (`gpt-5.6-luna`) | 2026年2月16日 |

OpenAIの各モデルページはいずれも「Feb 16, 2026 knowledge cutoff」と
明記している。`gpt-5.6`エイリアスはGPT-5.6 Solへルーティングされるため、
接尾辞なしのGPT-5.6についても同じ日付になる。

### Claude Fable 5.1

Anthropicの公式モデル一覧では、Claude Fable 5.1の
「Reliable knowledge cutoff」と「Training data cutoff」がともに
「Jun 2026」とされている。月単位の公表であり、月内の具体的な日付は
公式資料からは確認できない。

### 比較上の注意

- OpenAIは日単位、Anthropicは月単位で公表しているため、厳密な日数差は
  算出できない。
- Anthropicは「Reliable knowledge cutoff」と「Training data cutoff」を
  区別しているが、Fable 5.1では両方とも2026年6月である。
- Web検索や外部ツールで取得する最新情報は、モデル本体の学習済み知識とは
  別に扱う必要がある。

### 現行性

2026年9月7日に各モデルページを再確認した。GPT-5.6 Sol、Terra、Lunaはいずれも
現行ページに同じカットオフを掲載し、廃止または後継への移行告知はない。Fable 5.1も
現行モデル一覧に掲載され、2027年9月1日より前に廃止しないと案内されている。
したがって、GPT-5.6の初版値は維持し、Fableは現行の5.1情報へ更新した。

## 参考資料

- [GPT-5.6 Sol（OpenAI公式モデル資料）](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
  - 参照日: 2026-09-07
- [GPT-5.6 Terra（OpenAI公式モデル資料）](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
  - 参照日: 2026-09-07
- [GPT-5.6 Luna（OpenAI公式モデル資料）](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
  - 参照日: 2026-09-07
- [Models overview（Anthropic公式モデル一覧）](https://platform.claude.com/docs/en/models/overview)
  - 参照日: 2026-09-07

## 更新履歴

- 2026-09-07: Fable 5.1の現行名称、知識カットオフ、提供状態を公式一覧で再確認
- 2026-08-31: 全URL、知識カットオフ、提供状態、廃止予定を再確認
- 2026-08-26: 初版を作成
