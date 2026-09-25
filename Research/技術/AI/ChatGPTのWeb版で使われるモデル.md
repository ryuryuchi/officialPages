---
作成日: 2026-09-09
更新日: 2026-09-09
タグ:
  - ChatGPT
  - OpenAI
  - GPT-5.6
  - AIモデル
状態: 完了
---

# ChatGPTのWeb版で使われるモデル

## 概要

一般ユーザーがWeb版ChatGPTを使うとき、標準で割り当てられるモデルを、無料プランと有料プランの違いを含めてOpenAI公式情報で確認した。参照日は2026-09-09。

## 結論

- 無料プラン（Free）またはGoの通常のテキストチャットでは、標準モデルは **GPT-5.6 Luna** である。
- PlusやProなどの有料プランでは、GPT-5.6 Solなど、プランとモデル選択欄に表示される別モデルを使える。したがって「普通のChatGPT」が無料版を指すなら、答えはGPT-5.6 Lunaである。
- ChatGPTのモデルは、契約プラン、モデル選択、推論モード、利用上限到達時の自動切り替えで変わる。画面上部のモデル選択欄に表示される名称が、その会話で選択されているモデルを確認する最も確実な方法である。
- GPT-6 Astraは2026-09-03時点で限定的な組織向けの段階展開であり、無料版の通常チャットの標準モデルではない。

## 詳細

### 無料版の通常利用

OpenAIは、FreeとGoのユーザーについて、日常的なテキストチャットにGPT-5.6を提供している。OpenAIの案内では、無料ユーザーへGPT-5.6 Lunaの利用を拡大しており、通常の無料Web利用についてはGPT-5.6 Lunaが標準となる。

「Think」などの深い推論を使う操作では、同じLuna系でも処理方法や利用上限が通常チャットと異なる場合がある。無料版でも、ファイル、画像生成、音声、データ分析などはテキストチャットとは別の上限がある。

### 有料版・自動切り替え

Plus、Pro、Business、Enterpriseでは、契約プランとワークスペース設定に応じてGPT-5.6 Sol、Sol Pro、GPT-6 Astraなどの選択肢が表示される場合がある。表示されるモデルと上限は全ユーザー共通ではなく、段階展開やプランによって変わる。

また、Proモデルの利用上限に達した場合などには、ChatGPTが利用可能な別モデルへ自動的に切り替えることがある。このため、単に「ChatGPTは常に1つのモデル」とは言えない。

### 確認方法

1. Web版ChatGPTで対象の会話を開く。
2. 画面上部のモデル名またはモデル選択欄を見る。
3. 推論モードや自動選択が表示されている場合は、その設定も確認する。

モデル名が表示されない、または自動選択になっている場合は、プランの既定値とサービス側の自動ルーティングが適用されるため、回答ごとに内部処理が変わる可能性がある。

## 参考資料

- [Improving GPT-5.6 Sol in ChatGPT—and expanding access to GPT-5.6 Luna for free users](https://openai.com/index/improving-gpt-5-6-sol-in-chatgpt/)
  - 参照日: 2026-09-09
- [GPT-5.6 and GPT-6 Pro in ChatGPT](https://help.openai.com/en/articles/20001354-gpt-56-in-chatgpt)
  - 参照日: 2026-09-09
- [ChatGPT — Release Notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)
  - 参照日: 2026-09-09
- [GPT-5.6: Frontier intelligence that scales with your ambition](https://openai.com/index/gpt-5-6/)
  - 参照日: 2026-09-09

## 更新履歴

- 2026-09-09: OpenAI公式情報を確認し、無料版の標準モデル、有料版・自動切り替え、確認方法を整理して初版を作成
