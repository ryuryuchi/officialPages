---
作成日: 2026-10-07
更新日: 2026-10-07
タグ:
  - CVSS
  - 脆弱性評価
  - CVSS 4.0
  - CVSS 3.1
状態: 完了
---

# CVSS判定基準とスコアの読み方

## 概要

CVSS（Common Vulnerability Scoring System：共通脆弱性評価システム）の評価項目、スコア区分、CVSS 4.0と3.1の違い、および実際の脆弱性対応でスコアを使う際の注意点を整理する。

## 結論

- CVSSは脆弱性の**技術的な深刻度**を共通の尺度で表すもので、組織固有の**リスクそのもの**ではない。
- CVSS 4.0では、Base（基本特性）、Threat（脅威状況）、Environmental（利用環境）、Supplemental（追加情報）の4つのメトリクス群を扱う。Supplementalは数値スコアに影響しない。
- 0.0はNone、0.1～3.9はLow、4.0～6.9はMedium、7.0～8.9はHigh、9.0～10.0はCriticalである。
- スコアだけでなく、バージョン、ベクタ文字列、評価時点を併記する。実際の対応順は、公開状況、悪用の確認、対象資産の重要度、外部公開状況、緩和策なども考慮して決める。

## 詳細

### 1. CVSSの役割とスコア区分

CVSSはFIRSTが管理するオープンな枠組みで、ソフトウェア、ハードウェア、ファームウェアの脆弱性について、技術的特性と相対的な深刻度を伝える。スコアは0.0～10.0で表し、通常は小数第1位まで示す。

| CVSSスコア | 深刻度 |
| --- | --- |
| 0.0 | None（なし） |
| 0.1～3.9 | Low（低） |
| 4.0～6.9 | Medium（中） |
| 7.0～8.9 | High（高） |
| 9.0～10.0 | Critical（緊急） |

この区分は深刻度を読みやすくするためのラベルであり、対応期限や業務上の優先順位を直接定めるものではない。バージョンによって評価モデルや項目が異なるため、CVSS 3.1と4.0の数値を同じ尺度の測定値として単純比較しない。

### 2. CVSS 4.0のメトリクス群

#### Base（基本特性）

脆弱性そのものに関する、時間や利用者の環境に依存しない特性を評価する。基本メトリクスは、攻撃の成立しやすさと、成功時の影響に分かれる。

**攻撃の成立しやすさ**

| 項目 | 判定の観点 |
| --- | --- |
| Attack Vector（AV：攻撃元） | Network（N）はネットワーク越し、Adjacent（A）は隣接ネットワーク、Local（L）はローカル環境、Physical（P）は物理的な接触が必要かを示す。より遠隔から攻撃できる条件ほど、一般に深刻度は高くなる。 |
| Attack Complexity（AC：攻撃の複雑さ） | Low（L）は既存の組み込みセキュリティ機能を回避するための特別な行動が不要な場合、High（H）は攻撃者がその機能を回避・迂回するための行動を要する場合を示す。 |
| Attack Requirements（AT：攻撃の前提条件） | None（N）は特別な前提条件がない場合、Present（P）は攻撃者が制御できない対象システム側などの条件が成立している必要がある場合を示す。 |
| Privileges Required（PR：必要な権限） | None（N）、Low（L）、High（H）。攻撃前に対象でどの程度の権限を得ている必要があるかを示す。 |
| User Interaction（UI：利用者の操作） | None（N）は操作不要、Passive（P）は閲覧など一般的・受動的な操作、Active（A）は攻撃を成立させるための特定の操作を利用者に実行させる必要がある場合を示す。 |

ACとATは混同しやすい。攻撃を成功させるために攻撃者が乗り越える複雑さはAC、脆弱なシステム側に事前に成立していなければならない条件はATで評価する。

**成功時の影響**

影響は、脆弱性を含むシステム（Vulnerable System）と、そこから影響を受ける後続システム（Subsequent System）を分けて評価する。それぞれについて、機密性（Confidentiality：C）、完全性（Integrity：I）、可用性（Availability：A）への影響をNone（N）、Low（L）、High（H）から選ぶ。Noneはその属性への影響なし、Lowは限定的な影響、Highは重大な影響を表す。具体的な程度は、機密性・完全性・可用性ごとの仕様上の定義に照らして判定する。したがって、Baseの影響項目はVC、VI、VA、SC、SI、SAの6つである。

後続システムへの影響には、脆弱なコンポーネントの権限や信頼境界を越えて、連携先などに及ぶ影響を含める。CVSS 3.1のScope（S）を4.0でそのまま指定するのではなく、この2種類のシステムへの影響を個別に判定する。

#### Threat（脅威状況）

時間とともに変化する悪用状況を反映する。中心となるExploit Maturity（E：悪用成熟度）は、公開情報が未定義（X）、悪用が確認されている（A：Attacked）、概念実証コードがある（P：Proof-of-Concept）、悪用情報が報告されていない（U：Unreported）などから評価する。実際の悪用状況や公開された証拠を根拠に選び、時間の経過に応じて見直す。

「未報告」は「悪用されていないことが確認済み」と同義ではない。また、X（Not Defined）はその項目が指定されていない状態で、N（None：なし）などの具体値とは異なる。ThreatやEnvironmentalの一部がXでもスコアは計算されるため、Xを「脅威なし」や「影響なし」と読み替えない。

#### Environmental（利用環境）

利用組織が、自身のシステム構成や重要度に合わせて評価する。Modified Attack Vector（MAV）、Modified Attack Complexity（MAC）、Modified Attack Requirements（MAT）、Modified Privileges Required（MPR）、Modified User Interaction（MUI）と、修正後の影響項目（MVC、MVI、MVA、MSC、MSI、MSA）で実環境の条件や影響を反映できる。Confidentiality Requirement（CR）、Integrity Requirement（IR）、Availability Requirement（AR）は、対象システムにおける機密性・完全性・可用性の重要度を高・中・低などで表す。安全への影響がある場合は、利用組織が評価するMSI・MSAの安全影響値も考慮する。

製品提供者が一般的な条件で付けたBaseスコアと、自組織の環境を反映したスコアは、目的が異なる。自組織内のファイアウォールなどの緩和策を評価する場合は、Baseの攻撃条件を恣意的に変えるのではなく、Environmentalの該当項目で扱う。

#### Supplemental（追加情報）

脆弱性の追加的な特徴を表すが、**CVSSの数値スコアを変更しない**。例として、Safety（安全への影響）、Automatable（攻撃の自動化可能性）、Recovery（復旧しやすさ）、Value Density（価値の集中度）、Vulnerability Response Effort（対応に必要な労力）、Provider Urgency（提供者が示す緊急度）がある。組織の対応判断に使う情報であり、深刻度スコアに加算する項目ではない。

#### CVSS 4.0のスコア表記

| 表記 | 数値に反映するメトリクス群 |
| --- | --- |
| CVSS-B | Base |
| CVSS-BT | Base + Threat |
| CVSS-BE | Base + Environmental |
| CVSS-BTE | Base + Threat + Environmental |

Supplementalはどの表記でも数値計算には含めない。スコアを共有するときは、どのメトリクス群を反映した値か分かるようにする。

ベクタ文字列は、スコアの根拠となるメトリクス値を短く表したもの。たとえば、次はCVSS 4.0のBaseメトリクスを示す形式例であり、個別の脆弱性に対する判定ではない。

```text
CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N
```

### 3. CVSS 3.1の項目と4.0との違い

CVSS 3.1では、BaseにAttack Vector（AV）、Attack Complexity（AC）、Privileges Required（PR）、User Interaction（UI）、Scope（S）、Confidentiality（C）、Integrity（I）、Availability（A）がある。Temporal（時間的）にはExploit Code Maturity（E）、Remediation Level（RL）、Report Confidence（RC）、EnvironmentalにはCR・IR・ARと、Base項目を環境向けに修正する項目がある。3.1でも深刻度区分は0.0 None、0.1～3.9 Low、4.0～6.9 Medium、7.0～8.9 High、9.0～10.0 Criticalである。

| CVSS 3.1 Base項目 | 判定の観点 |
| --- | --- |
| Attack Vector（AV） | Network（N）、Adjacent（A）、Local（L）、Physical（P）のどこから攻撃できるか。 |
| Attack Complexity（AC） | Low（L）かHigh（H）か。攻撃成功に必要な複雑な条件を評価する。 |
| Privileges Required（PR） | None（N）、Low（L）、High（H）。攻撃前に必要な権限を示す。 |
| User Interaction（UI） | None（N）かRequired（R）か。第三者の操作が攻撃成立に必要かを示す。 |
| Scope（S） | Unchanged（U）は脆弱なコンポーネントと同じ権限範囲内、Changed（C）はその範囲を越えて他のコンポーネントに影響する場合。 |
| Confidentiality（C）・Integrity（I）・Availability（A） | それぞれNone（N）、Low（L）、High（H）から、機密性・完全性・可用性への影響を評価する。 |

TemporalのEは悪用コードの成熟度（Unproven、Proof-of-Concept、Functional、Highなど）、RLは修正策の提供状況（Official Fix、Temporary Fix、Workaround、Unavailable）、RCは脆弱性情報の確度（Unknown、Reasonable、Confirmed）を扱う。EnvironmentalではCR・IR・ARで対象環境における各要件の重要度を示し、Modified AV・AC・PR・UI・Scope・C・I・Aで環境固有の条件を反映する。

主な違いは次のとおり。

- 4.0はACをAttack ComplexityとAttack Requirementsに分け、攻撃者が乗り越える複雑さと、対象側に必要な前提条件を別にする。
- 3.1のScope（S）をなくし、4.0では脆弱なシステムと後続システムの機密性・完全性・可用性への影響を分けて記録する。
- 4.0のUser InteractionはNone・Passive・Activeの3区分になり、3.1のNone・Requiredより細かい。
- 3.1のTemporalメトリクス群は4.0でThreatに改称され、悪用の成熟度を扱う。
- 4.0では、スコアに反映されないSupplementalメトリクスが定義された。

### 4. スコアの算出と確認手順

CVSSは、項目の数を単純に足し合わせて平均する方式ではない。各メトリクスの値の組み合わせを規定の算出方法に当てはめてスコアを得る。手計算で推測せず、FIRSTの公式計算機など、対象バージョンに対応した計算機を使う。

1. 対象製品、バージョン、脆弱な機能、攻撃成立条件を特定する。
2. 公開された技術情報などの根拠を確認し、Baseの攻撃経路・必要権限・利用者操作・影響を判定する。
3. Threatを付ける場合は、悪用や概念実証の公開状況を根拠とともに反映する。
4. Environmentalは、自組織の資産重要度や実際の緩和策を知る利用者側で評価する。
5. 公式計算機でスコアとベクタ文字列を確認し、CVSSの版、スコア種別、評価日と一緒に記録する。
6. Supplementalの情報は、スコアとは別に対応判断へ取り込む。

たとえば、ネットワーク越しに認証なしで攻撃でき、利用者操作を要さず、脆弱なシステムの機密性を大きく損なうことが確認できた場合、それぞれAV:N、PR:N、UI:N、VC:Hの候補になる。ただし、これだけではAC・ATや他の影響を判定できず、CVSSスコア全体は確定しない。脆弱性の仕様と攻撃条件を確認して残りの項目を評価する。

### 5. 深刻度とリスクを混同しない

CVSS Baseは、脆弱性の技術的特性を標準条件で表す深刻度であり、個別組織でその脆弱性が悪用される可能性や被害額を直接示すものではない。ThreatとEnvironmentalを追加したCVSS-BTEは状況に近づくが、それだけで組織固有のリスク全体を表すわけではない。

優先順位を決めるときは、少なくとも次の情報を組み合わせる。

- インターネットなど外部から到達可能か、対象資産が実際に存在するか
- 実際の悪用が観測されているか、実用的な攻撃コードが公開されているか
- 対象システムの業務上・安全上の重要度と、侵害時に影響する範囲
- 適用済みの緩和策、修正プログラムの有無、修正に伴う運用影響
- 組織の規制、顧客影響、復旧要件などCVSSの範囲外の判断材料

したがって「Criticalなら必ず最優先」「Highなら後回し」のように、区分だけで一律に決めるのは適切でない。CVSSは優先順位付けの入力の一つとして利用する。

## 参考資料

- [CVSS v4.0 Specification Document — FIRST](https://www.first.org/cvss/v4.0/specification-document)
  - 参照日: 2026-10-07
- [CVSS v4.0 User Guide — FIRST](https://www.first.org/cvss/v4.0/user-guide)
  - 参照日: 2026-10-07
- [CVSS v4.0 Frequently Asked Questions — FIRST](https://www.first.org/cvss/v4.0/faq)
  - 参照日: 2026-10-07
- [CVSS v3.1 Specification Document — FIRST](https://www.first.org/cvss/v3.1/specification-document)
  - 参照日: 2026-10-07
- [CVSS v4.0 Calculator — FIRST](https://www.first.org/cvss/calculator/4.0)
  - 参照日: 2026-10-07
- [CVSS v3.1 Calculator — FIRST](https://www.first.org/cvss/calculator/3.1)
  - 参照日: 2026-10-07

## 更新履歴

- 2026-10-07: 初版を作成
