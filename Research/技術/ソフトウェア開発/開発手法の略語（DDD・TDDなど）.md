---
作成日: 2026-10-07
更新日: 2026-10-07
タグ:
  - DDD
  - TDD
  - BDD
  - ATDD
  - 開発手法
状態: 完了
---

# 開発手法の略語（DDD・TDDなど）

## 概要

DDDの正式名称と意味を確認し、TDDやBDDなど、名前に「Driven Development」を含む代表的な開発手法・設計アプローチを比較した。

## 結論

ソフトウェア設計の文脈でDDDは、通常 **Domain-Driven Design（ドメイン駆動設計）** を指す。「Domain-Driven Development」ではなく、正式名称の末尾は「Design」である。ビジネス上の複雑な領域を理解し、その知識や用語をソフトウェアのモデルに反映する考え方である。

「〇〇駆動開発」は一つの分類体系ではない。よく見かける略語にはTDD、BDD、ATDD、FDDがあり、MDDも関連する用語として使われる。それぞれが重視するものは異なり、互いに置き換えるものとは限らない。DDDとTDDなどを組み合わせて使うこともできる。

## 詳細

### 主な略語

| 略語 | 英語名 | 日本語名 | 主に重視するもの |
| --- | --- | --- | --- |
| DDD | Domain-Driven Design | ドメイン駆動設計 | 業務領域の知識、業務ルール、開発者と業務担当者が共有する言葉やモデル |
| TDD | Test-Driven Development | テスト駆動開発 | 実装前にテストを書き、失敗・成功・リファクタリングを短い周期で繰り返すこと |
| BDD | Behavior-Driven Development | 振る舞い駆動開発 | 利用者や関係者が理解できる言葉で、システムに期待する振る舞いを表すこと |
| ATDD | Acceptance Test-Driven Development | 受け入れテスト駆動開発 | 開発・テスト・業務側が協力し、実装前に受け入れ条件やテストを決めること |
| FDD | Feature-Driven Development | フィーチャ駆動開発 | 利用者に価値のある機能を単位に、計画・設計・実装を反復すること |
| MDD | Model-Driven Development | モデル駆動開発 | システムのモデルを中心に仕様や実装を組み立てること。ツールによってはモデルからコードなどを生成する |

### それぞれの違い

- **DDD**は、何を作るかを業務領域の理解から考える設計アプローチである。複雑な業務ルールをモデルに反映し、業務担当者と開発者の共通語彙を育てる。Eric Evansの参考資料では、Entity、Value Object、Aggregate、Bounded Contextなどのパターンを扱う。
- **TDD**は、次に実現する機能のテストを先に書き、そのテストを通す最小限の実装を行ってからコードを整理する反復手法である。一般に「Red-Green-Refactor」と呼ばれる。
- **BDD**は、単にテストを書くことより、システムがどう振る舞うべきかを関係者間で明確にすることに重点を置く。Given-When-Then形式のシナリオがよく使われる。
- **ATDD**は、顧客・開発・テストなど異なる立場の人が、実装前に受け入れ条件を話し合う実践である。BDDと重なる部分はあるが、同じ意味の用語とは限らない。
- **FDD**は、機能の一覧を作り、機能ごとに計画、設計、構築する反復型の開発方法である。代表的な説明では、全体モデルの作成、機能一覧の作成、機能ごとの計画、設計、構築という流れを取る。
- **MDD**はモデルを中心に開発を進める考え方である。OMGのModel Driven Architecture（MDA）は関連するアプローチだが、MDDとMDAは同じ略語ではない。

### 覚え方と注意点

「何を中心に進めるか」で大まかに区別できる。

- 業務の知識・ルールを中心に設計する: DDD
- テストを先に書いて実装を進める: TDD
- 期待する振る舞いを共有する: BDD
- 受け入れ条件を関係者で決める: ATDD
- 利用者価値のある機能を単位に反復する: FDD
- モデルを中心に仕様や実装を組み立てる: MDD

DDDとTDDは競合する方法ではない。例えば、DDDで業務ルールをモデル化し、そのルールを実装するときにTDDを使える。BDDやATDDで期待する振る舞い・受け入れ条件を共有し、実装の細部をTDDで進める構成も可能である。

BDDとATDDの境界は資料やチームによって重なる。略語だけで違いを決めつけず、チームがどのような活動や成果物を指しているか確認する。

また、DDDは文脈によって「Data-Driven Development」など別の語の略として使われることがある。ソフトウェア設計の話ではDomain-Driven Designを指すことが多いが、会話や文書では正式名称を併記すると誤解を避けやすい。

「Event-Driven Architecture（EDA）」のように、似た言い方でも開発プロセスではなくシステム構成の考え方を指すものがある。そのため、「〇〇駆動」という言葉をすべて同じ種類の開発手法として扱わない。

## 参考資料

- [Domain Driven Design | Martin Fowler](https://martinfowler.com/bliki/DomainDrivenDesign.html)
  - 参照日: 2026-10-07
- [DDD Reference | Domain Language](https://domainlanguage.com/ddd/reference/)
  - 参照日: 2026-10-07
- [Test-Driven Development | Martin Fowler](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
  - 参照日: 2026-10-07
- [Introducing BDD | Dan North](https://dannorth.net/blog/introducing-bdd/)
  - 参照日: 2026-10-07
- [BDD History | Cucumber](https://cucumber.io/docs/bdd/history/)
  - 参照日: 2026-10-07
- [Acceptance Test Driven Development (ATDD) | Agile Alliance](https://www.agilealliance.org/glossary/atdd/)
  - 参照日: 2026-10-07
- [Feature Driven Development | ProductPlan](https://www.productplan.com/glossary/feature-driven-development)
  - 参照日: 2026-10-07
- [MDA - The Architecture Of Choice For A Changing World | Object Management Group](https://www.omg.org/mda/)
  - 参照日: 2026-10-07

## 更新履歴

- 2026-10-07: 初版を作成。DDDの正式名称と、TDD・BDD・ATDD・FDD・MDDとの違いを整理。
