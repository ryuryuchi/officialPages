---
作成日: 2026-09-17
更新日: 2026-09-17
タグ:
  - OpenAI
  - API
  - 料金
  - データ管理
  - GPT-5.6
状態: 完了
---

# OpenAI APIの料金プランとデータ管理

## 概要

OpenAI APIを15人程度で利用する場合に、ChatGPTのサブスクリプションとの違い、
APIの料金体系・処理モード・利用ティア、データ保持と管理方法を調査した。
GPT-5.6 Sol、Terra、Lunaを使った場合の概算も示す。

## 結論

- **OpenAI APIには、ChatGPT Plusのような固定月額の席数プランはない。**
  原則として、モデル・入力トークン・出力トークンなどに応じた従量課金である。
- **ChatGPT Plus、Business、Enterpriseの契約とAPIの請求は別である。**
  ChatGPTの契約だけではAPIクレジットは付与されない。
- 15人がリアルタイムに使うなら通常の**Standard**処理を基本にし、
  月額の支出上限、プロジェクト単位のAPIキー、レート制限を設定する。
  非同期の一括処理は**Batch**、遅延を許容できる低優先度処理は**Flex**が候補になる。
- OpenAI APIへ送ったデータは、現行の公式資料では**明示的にオプトインしない限り、
  モデルの学習・改善には使われない**。一方、乱用監視ログは標準で最大30日保持される
  ため、「学習に使われない」と「外部に一切保存されない」は別である。
- 15人の利用量を「1人20リクエスト/日、月22営業日、1リクエストあたり入力2,000・
  出力1,000トークン」と仮定すると、GPT-5.6 Solは月約185ドル、Terraは約106ドル、
  Lunaは約11ドルがモデル入出力の概算になる。実際の費用はプロンプト長、ツール、
  画像、リトライ、キャッシュ、処理モードで変わる。
- 機密情報を組織外へ出せない場合は、標準APIではなく、承認が必要な
  Zero Data Retention等の適格性を確認するか、ローカルLLMを選ぶ。

## 詳細

### 1. APIとChatGPTの契約の違い

OpenAI API PlatformとChatGPTのサブスクリプションは、請求・利用枠が分離している。
ChatGPT Plus等を契約していてもAPI利用料は別に発生し、API側で支払い方法と利用上限を
設定する必要がある。逆にAPIへ入金してもChatGPTの有料機能は付与されない。

したがって、15人で自社システムや社内チャットを作る場合はAPIのOrganizationと
Projectを用意し、ブラウザーへAPIキーを直接配布せず、社内サーバーを経由して利用する。
ChatGPTの画面を15人へ提供したい場合は、APIではなくChatGPTのBusinessまたは
Enterpriseの契約条件を別途比較する必要がある。

### 2. APIの請求と利用ティア

新しいAPIアカウントはプリペイド課金が基本で、購入クレジットを使うと残高から
差し引かれる。購入クレジットの有効期限は購入から1年で、原則として返金されない。
自動チャージを使う場合は、残高不足による停止と予想外の請求の両方を管理する。

利用ティアは支払い実績に応じて自動的に上がり、レート制限とOpenAIが承認する
月間利用上限が増える。下表の金額は2026年9月17日時点の公式資料に記載された
資格条件・承認月間利用上限であり、実際のRPM・TPMはモデルとOrganizationの
ダッシュボードで確認する。

| ティア | 資格条件 | OpenAI承認の月間利用上限 |
| --- | --- | ---: |
| Free | 対象地域のユーザー | 100ドル |
| Tier 1 | 5ドル支払い済み | 100ドル |
| Tier 2 | 50ドル支払い済み | 500ドル |
| Tier 3 | 100ドル支払い済み | 1,000ドル |
| Tier 4 | 250ドル支払い済み | 5,000ドル |
| Tier 5 | 1,000ドル支払い済み | 200,000ドル |

ここでいう承認月間利用上限は、ユーザーが設定するハード上限とは別である。
OpenAIの承認上限とは別に、OrganizationまたはProjectに月間のSpend alertと
hard spend limitを設定できる。15人で始める場合は、通知用のSpend alertと、
暴走時に429で停止するhard spend limitを併用するのが安全である。

### 3. 処理モードと使い分け

| モード | 料金・特性 | 15人利用での用途 |
| --- | --- | --- |
| Standard | 通常の従量課金。リアルタイム応答向け | 社内チャット、対話型アプリ |
| Batch | Standardより50%安く、別枠の高いレート制限。完了は24時間以内 | 夜間の要約、分類、評価、埋め込み作成 |
| Flex | Batchと同じ料金水準。遅延やリソース不足による一時利用不可がある | 非本番の評価、低優先度の非同期処理 |
| Fast | Pay-as-you-goの柔軟性を保ちながら低遅延を狙う追加処理モード | 応答速度を優先する利用者向け |
| Scale Tier | トークン単位を事前購入し、予測可能なスループットを確保する方式 | 大規模・高信頼な本番処理 |

Batchは即時応答用ではなく、Flexは本番の必須処理にそのまま使う前提ではない。
FastやScale Tierの適用モデル、料金、利用可否はモデル・契約によって変わるため、
導入時に価格ページとOrganizationの設定画面で再確認する。

### 4. GPT-5.6の料金目安

価格ページの短いコンテキスト向け、100万トークンあたりの料金を示す。
キャッシュ入力、キャッシュ書き込み、長いコンテキスト、画像・音声などは別料金になる。

| モデル | Standard入力 | Standard出力 | Batch/Flex入力 | Batch/Flex出力 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol | 4ドル | 20ドル | 2ドル | 10ドル |
| GPT-5.6 Terra | 2ドル | 12ドル | 1ドル | 6ドル |
| GPT-5.6 Luna | 0.20ドル | 1.20ドル | 0.10ドル | 0.60ドル |

#### 15人での試算例

次の仮定で計算する。

- 利用者15人
- 1人あたり1日20リクエスト
- 月22営業日
- 1リクエストあたり入力2,000トークン、出力1,000トークン

月間では6,600リクエスト、入力13.2百万トークン、出力6.6百万トークンになる。
この条件でのStandard処理のモデル料金は次のとおりである。

| モデル | 月額概算（Standard） | Batch/Flex料金水準の概算 |
| --- | ---: | ---: |
| GPT-5.6 Sol | 184.80ドル | 92.40ドル |
| GPT-5.6 Terra | 105.60ドル | 52.80ドル |
| GPT-5.6 Luna | 10.56ドル | 5.28ドル |

これはトークン料金だけの試算であり、税、検索・コンピューター操作などのツール、
画像・音声、長文入力、リトライ、キャッシュ書き込み、アプリケーションサーバー費用は
含まない。実際の設計では、少なくとも2週間の実測使用量から見積もる。

### 5. データ利用と保持

OpenAI公式の「Your data」資料では、2023年3月1日以降、APIへ送信したデータは
明示的に共有へオプトインしない限り、OpenAIモデルの学習・改善には使われないと
説明されている。

ただし、次の区別が必要である。

| 項目 | Standard APIの扱い |
| --- | --- |
| モデル学習への利用 | オプトインしない限り利用しない |
| 乱用監視ログ | プロンプト・応答等を含む場合があり、標準では最大30日保持 |
| API機能のアプリケーション状態 | エンドポイントや機能によって保存期間が異なる |
| Zero Data Retention | 適格な顧客がOpenAIの事前承認を受けて利用 |
| Modified Abuse Monitoring | 適格な顧客が事前承認を受け、監視ログから顧客コンテンツを除外 |

Zero Data Retentionを有効にしても、全エンドポイント・全機能が同じ扱いになるとは
限らない。会話、ファイル、エージェント、スレッド等の状態を保存する機能を使う場合は、
対象エンドポイントの保存条件を個別に確認する必要がある。

### 6. 15人で使う場合の推奨設定

1. Organization内に用途別のProjectを作り、社内チャット用と検証用を分ける。
2. APIキーはサーバー側だけに置き、利用者ごとにキーを配布しない。
3. ProjectごとにSpend alertとhard spend limitを設定する。
4. 1ユーザーあたりのリクエスト数、入力サイズ、最大出力トークン、同時実行数を制限する。
5. Standardは対話、Batch/Flexは非同期処理へ分ける。
6. 機密情報はマスキングし、アプリケーションログへプロンプトや応答を丸ごと残さない。
7. 契約上のデータ保持要件が厳しい場合は、Zero Data Retention等の適格性を営業へ確認し、
   承認を得られない場合はローカルLLMを優先する。

関連するローカル実行のハードウェア要件は、
[ローカルLLMのPC要件と15人利用の構成](../AI/ローカルLLMのPC要件と15人利用の構成.md)を参照する。

## 参考資料

- [Pricing（OpenAI API公式）](https://developers.openai.com/api/docs/pricing)
  - 参照日: 2026-09-17
- [Rate limits（OpenAI API公式）](https://developers.openai.com/api/docs/guides/rate-limits)
  - 参照日: 2026-09-17
- [Setting up and managing prepaid API billing（OpenAI Help）](https://help.openai.com/en/articles/8264644-how-can-i-set-up-prepaid-billing)
  - 参照日: 2026-09-17
- [Spend limits（OpenAI API公式）](https://developers.openai.com/api/docs/guides/spend-limits)
  - 参照日: 2026-09-17
- [Data controls in the OpenAI platform（OpenAI API公式）](https://developers.openai.com/api/docs/guides/your-data)
  - 参照日: 2026-09-17
- [Batch API（OpenAI API公式）](https://developers.openai.com/api/docs/guides/batch)
  - 参照日: 2026-09-17
- [Flex processing（OpenAI API公式）](https://developers.openai.com/api/docs/guides/flex-processing)
  - 参照日: 2026-09-17
- [Fast mode（OpenAI API公式）](https://developers.openai.com/api/docs/guides/fast-mode)
  - 参照日: 2026-09-17
- [Scale Tier for API Customers（OpenAI公式）](https://openai.com/api-scale-tier/)
  - 参照日: 2026-09-17
- [Managing billing for ChatGPT and the API platform（OpenAI Help）](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform)
  - 参照日: 2026-09-17

## 更新履歴

- 2026-09-17: APIの請求、利用ティア、処理モード、GPT-5.6料金、データ保持、15人利用の管理方法を公式資料から調査して初版を作成
