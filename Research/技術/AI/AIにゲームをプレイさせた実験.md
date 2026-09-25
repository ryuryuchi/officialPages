---
作成日: 2026-08-26
更新日: 2026-08-31
タグ:
  - AIエージェント
  - ゲームAI
  - LLM
  - マルチモーダル
  - メモリ
状態: 完了
---

# AIにゲームをプレイさせた実験

## 概要

Claude Fable 5の『Slay the Spire』実験に似た、汎用LLMやマルチモーダルAIへ
実際のゲームを長時間・自律的にプレイさせる実験を調べた。従来のゲーム専用AIとは
分けて、推論、計画、視覚操作、外部メモリ、未知環境への汎化を評価した事例を中心に
整理する。

## 結論

- 類似実験は複数ある。**最も直接的に近いのはAgenticSTS**で、同じゲーム系列の
  『Slay the Spire 2』を使い、永続メモリの層を切り替えて成績を比較している。
- 長時間の進行と記憶を見る実演では、**Claude Plays Pokémon**、
  **Gemini Plays Pokémon**、Minecraftの**Voyager**が特に近い。
- 画面だけを見てキーボード・マウスを操作する条件では、複数の市販ゲームを扱う
  **Cradle**が近い。
- **BALROG**や**VideoGameBench**は、派手な成功例よりも「現在のモデルがどこで
  失敗するか」を複数モデルで比較できる公開ベンチマークである。
- ただし、実験ごとにハーネスが大きく異なる。画面だけを見る方式、ゲーム内部状態を
  読む方式、コードを生成して操作する方式の成績を、そのままモデル性能として
  横並びにはできない。

## 詳細

### 特に近い事例

| 実験 | 年 | ゲーム | 主な評価対象 | 公開状況 |
|---|---:|---|---|---|
| AgenticSTS | 2026 | Slay the Spire 2 | 長期計画、層別の永続メモリ | 論文、コード、軌跡データ |
| Claude Plays Pokémon | 2025 | Pokémon Red | 拡張思考、長期継続、メモリ | 公式説明と配信。コード非公開 |
| Gemini Plays Pokémon | 2025 | Pokémon Blue | 長文脈、要約メモリ、自己批評 | 技術報告と制作者記事。コード非公開 |
| Voyager | 2023 | Minecraft | 自動カリキュラム、スキル記憶、転移 | 論文、コード |
| Cradle | 2024 | 複数の市販ゲーム | 視覚による汎用PC操作、反省、メモリ | 論文、コード |

#### AgenticSTS

2026年公開のAgenticSTSは、『Slay the Spire 2』を長期LLMエージェントの
テストベッドにした実験である。ゲームModから状態を取得し、LLMの行動をゲームへ
戻す。プロンプト、ゲーム知識、ラン後のエピソード要約、再利用可能なスキルなどを
別々のメモリ層として扱い、どの層が成績に効くかを切り替えて調べている。

固定難易度A0、各条件10試行では、スキャフォールドなしが3勝、スキル層ありの
条件が6勝だった。ただし著者は、標本が小さく統計的に有意ではない
（Fisherの正確確率検定で約0.37）と明記している。公開軌跡は298件で、コード、
凍結したメモリ、分析スクリプトも公開されている。

Fable 5実験と「同じゲーム系列」「永続メモリの効果を見る」という点で最も近く、
Fable 5側では非公開だった試行数やメモリ構造を確認できる。一方、Fable 5の
再現実験ではなく、ゲームも初代ではなく続編である。

#### Claude Plays Pokémon

AnthropicはClaude 3.7 Sonnetに、基本的なメモリ、画面ピクセル、ボタン入力用の
function callを与え、『Pokémon Red』を通常のコンテキスト上限を超えて
数万回のインタラクションにわたりプレイさせた。公式説明では、Claude 3.0 Sonnetが
最初の家から出られなかったのに対し、3.7 Sonnetはジムリーダー3人を倒して
バッジを3個得た。

後のClaude 4発表では、Opus 4がプレイ中に自ら「Navigation Guide」という
メモリファイルを作成・維持したことも紹介された。Fable 5のファイルベースメモリ
評価につながる実演と見られるが、ハーネス、全ログ、試行回数は公開されていない。

#### Gemini Plays Pokémon

独立開発者Joel ZhangがGemini 2.5 Pro用のハーネスを作り、『Pokémon Blue』を
自律プレイさせた。Google DeepMind自身の企画ではないが、API提供を受け、後に
Gemini 2.5技術報告の事例として分析された。

エミュレータの画面を注釈・テキスト化し、RAMから得た情報、外部マップ、
100ターンごとのコンテキスト要約、別エージェントによる自己批評を利用する。
開発と同時進行だった最初の走行は813時間、ハーネスを固定した完全自律の2回目は
406.5時間で殿堂入りしたと技術報告に記載されている。

長文脈をそのまま伸ばすと、10万トークンを超えた付近から過去の行動を繰り返す
場合があった。制作者は、約8時間同じ場所を回り続けた事例を受けて、定期的な
要約リセットを導入した。長いコンテキストだけでなく、情報の圧縮と外部記憶が
長期プレイに必要だと示す事例である。

#### Voyager

VoyagerはGPT-4を使ってMinecraftを探索するオープンエンド型エージェントである。
次に挑む課題を自動生成するカリキュラム、環境のフィードバックを使う反復改善、
成功したJavaScriptコードを保存するスキルライブラリを組み合わせる。

公式プロジェクトページでは、比較手法に対して発見したユニークアイテム数が
3.3倍、木の道具段階への到達が15.3倍高速で、ダイヤモンド段階へ到達した唯一の
手法だったとしている。保存したスキルを別のワールドの未知タスクにも転用できた。

スキルライブラリは、経験を次の試行へ持ち越す永続メモリに相当する。ただし画面を
直接操作せず、Mineflayer経由でコードを実行するため、視覚能力の評価ではない。

#### Cradle

CradleはGPT-4oを中核に、スクリーンショットだけを入力し、キーボードとマウスで
ゲームや一般ソフトを操作する公開フレームワークである。情報収集、自己反省、
タスク推論、スキル整理、行動計画、メモリの6モジュールを持つ。

『Red Dead Redemption 2』のミッションのほか、『Cities: Skylines』、
『Stardew Valley』、『Dealer's Life 2』などで評価された。公式結果では、
『Dealer's Life 2』で取引機会の93.6%を成立させ、総利益率39.6%を記録した。
一方、リアルタイム戦闘、細かな物体位置、配管接続などでは失敗が多い。

市販ゲームを改造せず、画面と通常の入力だけで動かす点は、最小限の視覚ハーネスで
ゲームをプレイさせる実験に近い。ただし主目的はメモリ単体の比較ではなく、
汎用コンピュータ操作である。

### 複数モデルを比較するベンチマーク

#### BALROG

BALROGはNetHack、MiniHack、Crafter、BabyAI、TextWorldを使い、LLMや
マルチモーダルモデルの長期的・対話的な意思決定を比較するベンチマークである。
論文は、簡単な課題では部分的に成功する一方、難しい課題では大きく苦戦し、
モデルによってはテキスト表現より視覚表現を与えた方が性能が下がると報告している。
コードとリーダーボードが公開されている。

#### VideoGameBench

VideoGameBenchは1990年代の実ゲーム10本を、生の画面入力とコントローラ操作だけで
進めさせる評価である。ゲーム固有の攻略用スキャフォールドを避け、未知のゲームも
含めて汎化を測る。論文の集計では、上位のGemini 2.5 ProやClaude 3.7 Sonnetでも、
到達できたゲーム全体の進行度はリアルタイム設定で0.48%、軽量設定で1.6%だった。

成功例だけを見るとゲームAIがかなり進んだように見えるが、共通条件で多種類の
ゲームをプレイさせると、現在の汎用モデルはまだ序盤で止まりやすいことを示す。

### 広義の先行例

AlphaGo、AlphaStar、OpenAI FiveもAIにゲームをさせた代表例である。ただし、
これらは囲碁、StarCraft II、Dota 2向けに大量の対戦から専用方策を学習した
強化学習システムである。学習済みの汎用モデルへ薄いハーネスと外部メモリを与える
近年の実験とは、目的と仕組みが異なる。

### 比較するときの注意点

1. **AIが見られる情報が違う。** 生の画面だけ、注釈付き画面、RAMや構造化された
   ゲーム状態、ゲームAPIでは難易度が大きく異なる。
2. **操作の細かさが違う。** 1回ずつボタンを押す方式と、数十手の経路やコードを
   一度に生成する方式は比較できない。
3. **モデルとハーネスを分けて考える。** 成功はモデル本体だけでなく、地図、
   要約、攻略知識、自己批評、スキル検索などの設計にも依存する。
4. **単発デモとベンチマークを分ける。** 配信での1回のクリアは長期継続の実例には
   なるが、勝率やモデル間の優劣を確定する統計にはならない。
5. **公開度に差がある。** AgenticSTS、Voyager、Cradle、BALROGは追試しやすい。
   Claude/GeminiのPokémon実演は観察材料は多いが、完全な再現は難しい。

### 2026年8月31日の再確認

全14件の参考URLを再確認した。AgenticSTSの公開ページは固定A0・各条件10試行の
表と統計的非有意という留保を維持しており、他の論文・プロジェクトにも本メモの
主要数値を覆す訂正や後継版は確認できなかった。したがって比較結論は変更しない。
AlphaStarの記事は旧`/discover/blog/`から現行`/blog/`へ転送されるため、参考資料を
現行の正規URLへ更新した。

### 関連メモ

- [Slay the Spire実験](Slay%20the%20Spire実験.md)
  - Claude Fable 5の実験内容と、公開情報だけでは判断できない点を詳しく整理

## 参考資料

- [AgenticSTS: A Bounded-Memory Testbed for Long-Horizon LLM Agents](https://arxiv.org/abs/2607.02255)
  - 参照日: 2026-08-31
- [AgenticSTSプロジェクトページ](https://alayalab.github.io/AgenticSTS/)
  - 参照日: 2026-08-31
- [Visible extended thinking（Anthropic）](https://www.anthropic.com/research/visible-extended-thinking)
  - 参照日: 2026-08-31
- [Introducing Claude 4（Anthropic）](https://www.anthropic.com/news/claude-4)
  - 参照日: 2026-08-31
- [Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic Capabilities](https://arxiv.org/abs/2507.06261)
  - 参照日: 2026-08-31
- [The Making of Gemini Plays Pokémon（Joel Zhang）](https://blog.jcz.dev/the-making-of-gemini-plays-pokemon)
  - 参照日: 2026-08-31
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291)
  - 参照日: 2026-08-31
- [Voyagerプロジェクトページ](https://voyager.minedojo.org/)
  - 参照日: 2026-08-31
- [Cradle: Empowering Foundation Agents Towards General Computer Control](https://arxiv.org/abs/2403.03186)
  - 参照日: 2026-08-31
- [Cradleプロジェクトページ](https://baai-agents.github.io/Cradle/)
  - 参照日: 2026-08-31
- [BALROG: Benchmarking Agentic LLM and VLM Reasoning On Games](https://arxiv.org/abs/2411.13543)
  - 参照日: 2026-08-31
- [VideoGameBench: Can Vision-Language Models complete popular video games?](https://arxiv.org/abs/2505.18134)
  - 参照日: 2026-08-31
- [AlphaStar: Grandmaster level in StarCraft II using multi-agent reinforcement learning（Google DeepMind）](https://deepmind.google/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/)
  - 参照日: 2026-08-31
- [OpenAI Five](https://openai.com/index/openai-five/)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全14参考URL、公開結果、訂正・後継版の有無を再確認し、AlphaStarの
  URLを現行の正規URLへ更新
- 2026-08-26: 初版を作成
