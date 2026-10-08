---
作成日: 2026-09-25
更新日: 2026-09-25
タグ:
  - Jev
  - TypeSafe
  - AIモデル
  - VS Code
状態: 完了
---

# Jevとは何かとVS Codeでの利用

## 概要

「すごいAI」として紹介されるJevが何をするモデルなのか、一般的なチャットAIやコーディングAIと何が違うのか、VS Codeで利用できるのかを、TypeSafeとVS Codeの公式資料を中心に調べる。

## 結論

JevはTypeSafeの「System One」モデルで、自由な文章やコードを生成するのではなく、文章やJSONなどの入力について、選択・採点・真偽判定といった**範囲を定めた判断**を返す。結果が型付きデータと確率で返るため、分類、振り分け、評価などをアプリケーションの処理に組み込みやすい。

「何でも答える非常に賢いチャットAI」や、Copilotの代わりにコードを書くモデルではない。特定の判断タスクで役に立つ専用部品であり、汎用LLMやコーディングエージェントを置き換えるものではない。Jevがあらゆる用途で他のAIより優れているという独立した比較結果は、この調査では確認できていない。

VS Codeでは、GitHub Copilotが対応するAgent SkillsとしてTypeSafeの公式スキルを読み込ませ、TypeSafeを使うコードの作成を支援させられる。また、自分のアプリや拡張機能からTypeSafe APIを呼ぶこともできる。いずれもCopilotの基盤モデルをJevに切り替える機能ではない。

## 詳細

### Jevが返すもの

TypeSafeは、Jevを「System One」モデルと呼んでいる。入力（state）と質問を渡し、主に次の3種類の回答を得る。

| 型 | できること | 例 |
| --- | --- | --- |
| Choice | あらかじめ定めた選択肢から選ぶ | 問い合わせを担当部署へ振り分ける |
| Score | 定義した基準に沿って点数を付ける | 文面の緊急度や品質を採点する |
| Noul | 真偽を判定し、0〜1の値を返す | 返金を求めているか判定する |

たとえば問い合わせ文を一度渡して、「緊急か」「どの部署が担当か」「どれくらい不満か」を同時に質問し、返ってきた値に応じて通常のプログラムで処理を分けられる。APIとSDKが結果を型付きデータとして返すため、LLMに「JSONだけで返して」と頼む方法より、出力の形式をソフトウェア側で扱いやすくする設計である。

### 「すごい」の意味と限界

- TypeSafeは、確率の校正、速さ、ソフトウェアで直接扱える構造化出力をJevの設計目標として説明している。これは提供元の説明であり、どの業務でも一定の正解率や速度を保証する意味ではない。
- 確率の校正は、多数の予測を集めたときに確率が実際の正解頻度に近づく性質であり、個々の回答が必ず正しいという保証ではない。閾値を決めて、人に確認を回す処理も検討する。
- 自由な説明、文章やコードの生成、会話、画像・音声・動画の直接入力には向かない。公式資料ではテキスト入力のみ対応としている。
- 英語が主な学習言語で、日本語を含む他言語も扱うが、精度は同等とは限らない。日本語で実運用する前に、対象データでテストする必要がある。
- 2026-09-25に確認したモデル資料ではJev 1.13.0が掲載され、入力は100万トークンあたり0.042米ドル、出力トークンは無料。料金や提供モデルは変わる可能性があるため、利用時に公式ページを再確認する。
- 同じモデル資料では、1リクエストの上限を64kトークン（入力全体と質問の合計）、入力と最長質問の組み合わせは32kトークンとしている。上限値やレート制限は変更される可能性がある。

### VS Codeでの利用方法

#### GitHub CopilotにTypeSafeの使い方を教える

VS CodeのGitHub CopilotはAgent Skillsに対応しており、プロジェクト内では`.github/skills/`などに置いたスキルを必要に応じて読み込める。TypeSafeの公式`typesafe-ai`スキルは、API、質問型、設計パターンをコーディングエージェントに説明し、TypeSafeを使うコードを書くのを支援する。

この方法でJevがCopilot Chatのモデルになるわけではない。Copilotのエージェントがコード作成を担い、生成したアプリケーションが必要に応じてTypeSafe APIを呼ぶという役割分担である。インストール方法はTypeSafe公式のAgent Skill資料とVS CodeのAgent Skills資料を参照する。

#### 自作アプリからJevを呼ぶ

アプリケーションからTypeSafe API（`POST /v1/systemone`）またはPython・JavaScript SDKを使って呼び出す。TypeSafeのAPIキーが必要であり、キーは環境変数や秘密情報管理機能に保管し、ソースコードやGitへ書き込まない。

APIへ渡す文章やデータはTypeSafeのサービスに送信される。提供元は入力をモデル学習に使わないと説明しているが、それだけでデータ保持やその他のプライバシー条件がすべて保証されるわけではない。機密情報を送る場合は、組織の規則と最新の利用規約・プライバシー資料を確認する。TypeSafeはEnterprise向けにゼロデータ保持（ZDR）を案内している。

#### Jevを使う編集用Agent Skillの例

GitHubの`RefoundAI/jev-editor-skill`は、記事やブログ原稿の文体、編集構成、SEOなどをJevで評価するコミュニティ製スキルである。これはTypeSafe公式の汎用`typesafe-ai`スキルとは別のプロジェクトで、Agent Skills対応エージェントから使う例の一つ。リポジトリはPython 3.10以上とTypeSafe APIキーを要件としている。

## 参考資料

- [Jev with coding agents - TypeSafe AI](https://docs.typesafe.ai/introduction/coding-agents)
  - 参照日: 2026-09-25
- [System One - TypeSafe AI](https://docs.typesafe.ai/concepts/system-one)
  - 参照日: 2026-09-25
- [Models - TypeSafe AI](https://docs.typesafe.ai/models)
  - 参照日: 2026-09-25
- [Quick start - TypeSafe AI](https://docs.typesafe.ai/introduction/quickstart)
  - 参照日: 2026-09-25
- [Agent skill - TypeSafe AI](https://docs.typesafe.ai/agent-skill)
  - 参照日: 2026-09-25
- [Use Agent Skills in VS Code - Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
  - 参照日: 2026-09-25
- [Privacy policy - TypeSafe AI](https://typesafe.ai/legal/privacy-policy)
  - 参照日: 2026-09-25
- [RefoundAI/jev-editor-skill - GitHub](https://github.com/RefoundAI/jev-editor-skill)
  - 参照日: 2026-09-25

## 更新履歴

- 2026-09-25: 初版を作成。Jevの特性、用途と制約、VS CodeでのAgent Skills/API利用を公式資料から整理
