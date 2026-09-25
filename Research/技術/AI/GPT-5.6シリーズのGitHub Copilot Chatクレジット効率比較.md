---
作成日: 2026-09-09
更新日: 2026-09-09
タグ:
  - GitHub Copilot
  - Copilot Chat
  - GPT-5.6
  - AIクレジット
状態: 完了
---

# GPT-5.6シリーズのGitHub Copilot Chatクレジット効率比較

## 概要

GitHub Copilot Chatで利用できるGPT-5.6 Luna、Terra、Solについて、Usage Based BillingにおけるAIクレジットの消費効率を公式のトークン単価から比較した。参照日は2026-09-09。

## 結論

- 同じ入力・出力・キャッシュ条件なら、クレジット効率は **Luna > Terra > Sol** の順である。LunaはGPT-5.6シリーズ内で最も低価格、Terraは中間、Solは最も高価格である。
- 単純な質問、短い修正、反復的な作業はLunaが最も長く使える。通常の対話的・エージェント型コーディングはTerra、複雑な推論、大規模コードベース、長時間のエージェント作業はSolが公式の想定用途である。
- 「1回のチャット＝一定クレジット」ではない。入力、出力、キャッシュ入力、キャッシュ書き込みのトークン数で決まり、長い会話やエージェントの複数回呼び出しは消費量が増える。
- モデル倍率は実在するが、現在のGPT-5.6利用に掛かる倍率ではない。2026-06-01に移行したUsage Based Billingでは倍率を使わず、トークン単価からAIクレジットを計算する。
- 倍率が残るのは、既存の年額Copilot Pro／Pro+でレガシーのプレミアムリクエスト課金を継続している場合だけである。そのレガシー契約者は新モデルを利用できないため、GPT-5.6 Luna／Terra／Solの倍率は公式表に存在しない。
- 有料プランでAutoを使う場合はモデルコストに10%割引が適用される。一方、特定モデルを手動選択した場合の比較は、公開単価そのもので行う。
- AIクレジットの効率だけで品質を順位付けすることはできない。安価なLunaで目的を達成できる作業はLuna、失敗による再試行コストが大きい作業はTerraまたはSolを選ぶのが実用的である。

## 詳細

### 料金表

GitHub公式の価格表は1,000,000トークン単位で、1 AIクレジットは0.01米ドルである。以下は2026-09-09時点のGPT-5.6の単価（米ドル／100万トークン）。

| モデル | 区分 | 入力 | キャッシュ入力 | キャッシュ書き込み | 出力 |
| --- | --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Luna | 通常（入力200K以下） | 0.20 | 0.02 | 0.25 | 1.20 |
| GPT-5.6 Terra | 通常（入力272K以下） | 2.00 | 0.20 | 2.50 | 12.00 |
| GPT-5.6 Sol | 通常（入力272K以下） | 4.00 | 0.40 | 5.00 | 20.00 |
| GPT-5.6 Luna | 長文（入力200K超） | 0.40 | 0.04 | 0.50 | 1.80 |
| GPT-5.6 Terra | 長文（入力272K超） | 4.00 | 0.40 | 5.00 | 18.00 |
| GPT-5.6 Sol | 長文（入力272K超） | 8.00 | 0.80 | 10.00 | 30.00 |

### 同じトークン量での相対効率

通常料金の単価を比較すると、Lunaを1とした場合、Terraは入力・キャッシュ入力・キャッシュ書き込みで10倍、出力で10倍、Solはそれぞれ20倍、20倍である。したがって、同じトークン構成の処理だけを比べると、TerraはLunaの10分の1、Solは20分の1のクレジット効率になる。

1 AIクレジット（0.01米ドル）で処理できるトークン数の目安は次のとおりである。実際の1回の対話は複数種類のトークンを含むため、単一列だけを合算せず、各トークン種別の単価で計算する。

| モデル（通常料金） | 入力 | キャッシュ入力 | キャッシュ書き込み | 出力 |
| --- | ---: | ---: | ---: | ---: |
| Luna | 50,000トークン | 500,000トークン | 40,000トークン | 約8,333トークン |
| Terra | 5,000トークン | 50,000トークン | 4,000トークン | 約833トークン |
| Sol | 2,500トークン | 25,000トークン | 2,000トークン | 500トークン |

長文料金では、Lunaの入力効率が25,000トークン／クレジット、Terraが2,500、Solが1,250となる。長文コンテキストでは通常料金より効率が落ちるため、大きなリポジトリを毎回そのまま渡す使い方は、モデル選択だけでなく会話の分割や不要な文脈の削減も重要になる。

### 「モデル倍率」が掛かるケース

GitHubには、以前のプレミアムリクエスト課金でモデルごとの倍率を掛けて月間リクエスト枠を減らす仕組みがある。ただし、GitHubは2026-06-01にUsage Based Billingへ移行し、倍率は新方式には適用されないと明記している。

倍率が適用される例外は、既存の年額Copilot Pro／Pro+契約者が契約満了までレガシーのプレミアムリクエスト方式を継続している場合である。公式の現行レガシー表では、GPT-5 miniは0.33倍、GPT-5.3-Codexは6倍、GPT-5.4とGPT-5.4 miniは6倍、GPT-5.5は57倍などとされている。Autoを使う場合はレガシー方式でも10%割引され、1倍のモデルなら0.9倍として計算される。

一方、同じ公式資料はレガシー年額プランの利用者には新モデルへのアクセスがないと説明している。したがって、GPT-5.6 Luna／Terra／Solを選べる通常の利用者は、倍率ではなく入力・出力・キャッシュトークンの単価で計算する。倍率をGPT-5.6の単価へさらに掛ける計算は、二重計上になる。

### 用途別の選び方

| 作業 | 推奨 | 理由 |
| --- | --- | --- |
| 短い質問、単純なコード修正、定型的な説明 | Luna | 最低単価で、短時間・小規模タスク向け |
| 通常の実装、対話的なデバッグ、一般的なエージェント作業 | Terra | 公式にバランス型の既定候補として位置付けられている |
| 大規模コードベースの設計検討、難しいデバッグ、長時間のエージェント作業 | Sol | 推論性能の上限を重視する用途向け。ただし単価は最も高い |
| 作業内容に応じて自動選択したい | Auto | 有料プランではモデルコストに10%割引がある。ただし選択モデルと価格を固定した比較には向かない |

### 利用可能なプランと課金範囲

GitHubの案内では、SolはCopilot Pro+、Max、Business、Enterpriseで利用でき、TerraとLunaはPro、Pro+、Max、Business、Enterpriseで利用できる。展開は段階的で、BusinessとEnterpriseでは管理者によるモデルポリシーの有効化が必要な場合がある。

Copilot Chat、Copilot CLI、cloud agentなどの機能はAIクレジットを消費する。一方、コード補完とNext Edit suggestionsはAIクレジットの対象外である。したがって、補完中心の利用ではモデル単価の比較結果がそのまま月間消費量を表すわけではない。

### 効率比較の限界

ここでの「効率」は、同一トークン量を処理したときの金銭・AIクレジット上の効率であり、正答率や作業完了率を含むベンチマークではない。Solで一度で完了する作業をLunaで何度もやり直す場合、実際の総消費は逆転し得る。GitHub公式も、モデルの選択はタスクの複雑さ、品質、レイテンシー、コストのバランスで決めるよう案内している。

## 参考資料

- [Models and pricing for GitHub Copilot](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
  - 参照日: 2026-09-09
- [AI model comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
  - 参照日: 2026-09-09
- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
  - 参照日: 2026-09-09
- [OpenAI’s GPT-5.6 Sol, Terra, and Luna are now available in GitHub Copilot](https://github.blog/changelog/2026-07-09-openais-gpt-5-6-sol-terra-and-luna-are-now-available-in-github-copilot/)
  - 参照日: 2026-09-09
- [Usage-based billing for individuals](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals)
  - 参照日: 2026-09-09
- [Model multipliers for annual plans on request-based billing (legacy)](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/model-multipliers-for-annual-plans)
  - 参照日: 2026-09-09

## 更新履歴

- 2026-09-09: GitHub公式のGPT-5.6単価、AIクレジット換算、用途別推奨、プラン別提供範囲を調査して初版を作成
- 2026-09-09: レガシー年額プランのモデル倍率とGPT-5.6への非適用、Usage Based Billingとの違いを追記
