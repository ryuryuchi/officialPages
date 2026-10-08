---
作成日: 2026-09-28
更新日: 2026-10-08
タグ:
  - API
  - ゲーム
  - Riot Games
  - モンスターハンター
  - Apex Legends
状態: 完了
---

# ゲームシリーズ別に利用できるAPI

## 概要

モンスターハンターシリーズ、VALORANT、Apex Legends、ストリートファイター6
(SF6)、League of Legends (LoL) について、2026-09-28時点で利用できる公式APIと
コミュニティ提供API・データソースを調べた。プレイヤー統計、試合データ、ゲーム内
データベースのどれを取得できるかを区別する。

## 結論

- **公式のプレイヤー・試合APIが最も充実しているのはLoL**。Riot Developer Portalの
  APIキーを使い、プレイヤー識別、試合詳細・タイムライン、ランクなどを取得できる。
  チャンピオンやアイテムなどの静的データには別系統のData Dragonがある。
- **VALORANTにもRiot公式APIはある**が、プレイヤー別データを使うアプリには本番キーと
  Riot Sign On (RSO) による本人の共有同意が必要。現在のVALORANTポリシーでは個人用
  APIキー申請を受け付けていないため、気軽な個人用戦績取得には向かない。
- **モンスターハンターは、確認できた範囲でCapcom公式の公開Web APIは見つからない**。
  代わりにWorld向けのMHW DB、Wilds向けのMHDB Wildsなど、作品別のコミュニティAPIが
  JSONデータを提供している。単一のシリーズ共通APIではない。
- **Apex Legendsは、確認できた範囲でEA/Respawn公式の公開プレイヤー戦績APIは
  見つからない**。Apex Legends APIやTracker Networkなどの非公式サービスが候補だが、
  APIキー、利用条件、稼働状況、取得できるプラットフォームを各サービスで確認する。
- **SF6は、Capcom公式のBuckler's Boot Campでプロフィールやランキング等を閲覧
  できる一方、外部開発者向けの公開APIは確認できない**。コミュニティが非公開のWeb
  ルートを記録しているが、ログインセッションを要し、仕様変更や利用規約上のリスクが
  あるため、安定した公開APIとして扱わない。

| 対象 | 公式に確認できた開発者向けAPI | コミュニティ等の候補 | 実用上の見立て |
| --- | --- | --- | --- |
| モンスターハンター | 公開APIは確認できず | MHW DB、MHDB Wilds、MonHunAPI | モンスター・装備などの図鑑データ向け。作品ごとに選ぶ |
| VALORANT | Riot API: Content、Match、Ranked、Status | VALORANT-API.com（ゲーム内コンテンツのカタログ） | 静的コンテンツ参照は比較的容易。個人戦績は本番キーとRSO同意が前提 |
| Apex Legends | 公開プレイヤー戦績APIは確認できず | Apex Legends API、Tracker Network、DGS Ingram | 非公式サービスに依存。プレイヤー戦績・ゲーム情報の可用性は提供元次第 |
| SF6 | BucklerのWeb機能はあるが公開APIは確認できず | Buckler API Notes、SF6 Stats | 非公式・未文書化ルート。試作以外の基盤には不向き |
| LoL | Riot API: Account、Match、League、Champion Mastery等 | CommunityDragon（補助的なクライアントデータ） | プレイヤー・試合・ランク取得には公式APIが第一候補。静的データはData Dragon |

## 詳細

### モンスターハンターシリーズ

Capcom公式の開発者向けAPIドキュメントや公開Web APIは確認できなかった。確認できた
実用的な選択肢は、Capcomではなくコミュニティが整備するデータベースAPIである。

| サービス | 対象・取得データ | 確認事項 |
| --- | --- | --- |
| [MHW DB](https://docs.mhw-db.com/) | Monster Hunter: Worldのモンスター、武器、アイテム等。`https://mhw-db.com/monsters` のようなJSONエンドポイント | ドキュメントには複数言語のエンドポイントがある。全言語の値が揃っているとは限らない |
| [MHDB Wilds](https://docs.wilds.mhdb.io/) | Monster Hunter Wildsのモンスター、装備、アイテム等。例: `https://wilds.mhdb.io/en/monsters` | 英語ロケールのJSONレスポンスを実際に確認。コミュニティ管理であり、データの未収録・更新遅れ・スキーマ変更があり得る |
| [MonHunAPI](https://github.com/pkwlo/MonHun-API) | 複数作品のモンスター情報をまとめることを掲げるコミュニティAPI | リポジトリの説明ではWorldやRiseなどを順次扱う構想。Wildsを含む現在の網羅性・稼働状況は利用前に確認する |

アイテム検索や装備シミュレーターのような「ゲーム内図鑑」機能なら、対象作品に対応する
データソースを使うのが現実的である。API提供者と権利元は別であるため、ゲームデータや画像の
再配布・商用利用をする場合は、APIプロジェクトのライセンスだけでなくゲーム素材の権利と
各サービスの利用条件も別に確認する。APIが無料で応答することは、データの自由な再配布を
意味しない。

### VALORANT

Riot公式のVALORANT APIとして、少なくとも次のカテゴリがDeveloper Portalに記載されている。

| API | 主な用途 |
| --- | --- |
| VAL-CONTENT-V1 | コンテンツ情報の取得 |
| VAL-MATCH-V1 | match IDによる試合詳細、PUUIDのmatch list、キュー別の最近の試合 |
| VAL-RANKED-V1 | Actごとの競技ランキング |
| VAL-STATUS-V1 | プラットフォームのサービス状態 |

ただし、APIが公開されていることと、誰でもプレイヤー戦績を取得できることは同じではない。
VALORANTの公式ポリシーでは、プレイヤー別データを扱うアプリはユーザーのオプトインを
求める必要があり、RSOと本番APIキーが必要とされる。また、ドキュメントには個人用キーの
申請を現在受け付けていない旨がある。したがって、個人が試しに開発キーを取得して他人の
戦績を自由に調べるAPIとしては考えない。

[VALORANT-API.com](https://valorant-api.com/)は、武器やスキン等のゲーム内コンテンツと
アセットを提供する非公式コミュニティAPIである。これはRiotのプレイヤー戦績APIの代替では
なく、コンテンツカタログ向けである。Riot公式ポリシーの公開コンテンツカタログも、画像や
テキストなどの静的素材を配布する別の手段として案内されている。

### Apex Legends

公開ドキュメントを確認できるEA/Respawn公式プレイヤー統計APIは見つからなかった。
プレイヤー情報やゲームデータが必要なら、第三者が運営するサービスを使うことになる。

| サービス | 取得できるもの・条件 |
| --- | --- |
| [Apex Legends API](https://apexlegendsapi.com/) | 非公式API。プレイヤー統計とゲーム情報を提供すると明記。APIキーが必要で、提供者自身が無保証・稼働保証なしと明記している。プレイヤー照会は名前とプラットフォームを指定する形式 |
| [Tracker Network Apex API](https://tracker.gg/developers/docs/titles/apex) | Tracker Networkの開発者API資料がある。APIキーの取得可否や最新の利用制限・商用条件を登録前に確認する |
| [DGS "Ingram" API](https://apexlegendsstatus.com/tournament-stable/api) | ApexLegendsStatusの大会データ向けAPI。トーナメント、スコア、参加選手の大会成績など。プレイヤーの一般的な全試合履歴を取るAPIとは異なる。トークンが必要で、資料上は標準2 requests/second、非商用利用可、商用は事前連絡が必要 |

API提供者のデータソースやEA側の変更に依存するため、長期運用では応答エラー、更新停止、
取得可能なプラットフォームの縮小を想定する。特にApex Legends APIはドキュメント上で
無保証としているため、唯一のデータ供給元にしない設計がよい。

### ストリートファイター6 (SF6)

Capcom公式の[Buckler's Boot Camp](https://www.streetfighter.com/6/buckler/en/welcome)
ではプロフィール、ランキング、キャラクター統計等を閲覧できる。しかし、第三者が利用する
ための公式公開APIドキュメントは確認できなかった。

[Buckler API Notes](https://sfstats.app/buckler)は、BucklerのWebフロントエンドが使う
未文書化のNext.jsページデータルートを観察してまとめたコミュニティ資料である。資料自身が
「REST APIではない」「非公式」「ルート・フィールド・認証が変更され得る」と注意している。
ログイン済みの自分のブラウザーセッションを使う想定であり、認証の回避や他人の資格情報の
利用を目的としたものではない。

個人の検証であっても、セッションCookieを秘密情報として保護し、利用規約・アクセス制御に
従う必要がある。公開サービスや継続運用での依存先としては、Capcomの公式提供や許可を
得られない限り推奨しない。試合データが必要な場合は、Bucklerを人が閲覧する用途と、
コミュニティの未保証な取得手段を分けて判断する。

### League of Legends (LoL)

Riot Developer Portalから公式APIを利用できる。主な用途は次のとおり。

| API | 主な用途 |
| --- | --- |
| Account-V1 | Riot ID等からRiotアカウント識別情報を取得 |
| Match-V5 | PUUIDからmatch ID一覧を取得し、試合詳細・タイムラインを取得 |
| League-V4 | ランクリーグやリーグ情報を取得 |
| Champion-Mastery-V4 | プレイヤーのチャンピオン熟練度情報を取得 |

利用にはRiot APIキーが必要。RiotアカウントでDeveloper Portalにログインすると開発用キーが
発行され、プロダクトを登録して審査を受けることで追加アクセスやレート上限の引き上げを
申請できる。プレイヤー向けに公開するプロダクトはDeveloper Portalへの登録とRiotの
ポリシー順守が必要で、APIキーを配布アプリやブラウザー側のコードへ埋め込んではならない。
正確なレート上限、キーの有効条件、必要なルーティング地域は利用時点の公式ドキュメントで
確認する。

[Data Dragon](https://ddragon.leagueoflegends.com/cdn/)は、チャンピオン、アイテム、
ルーン、サモナースペル、画像などの**パッチ単位の静的データ配布**であり、プレイヤーの
試合履歴を返すAPIとは別である。バージョン一覧を取得して、対象バージョンと言語のJSONを
選んで使う。クライアント由来の追加データが必要な場合は[CommunityDragon](https://communitydragon.org/)
等の非公式資料もあるが、公式Data Dragonと同等のサポートや安定性は期待できない。

Riotの一般・ゲーム別ポリシーはタイトルごとに異なる。LoLで許される使い方をVALORANTにも
そのまま適用できるとは限らない。試合前の相手のスカウティング、隠されたプレイヤーの特定、
公式ランク制度の代替、ゲーム内で得られない競争上の優位につながる機能などは特に避け、
各ゲームのポリシーを確認する。

### 用途別の選び方

- **モンスター・武器・装備図鑑**: WildsならMHDB Wilds、WorldならMHW DBなど、作品対応を
  明示するコミュニティAPIを選ぶ。
- **VALORANTのスキン・武器等の表示**: 公式コンテンツカタログまたはVALORANT-API.com。
- **VALORANTの個人戦績**: Riotにプロダクトを登録し、本番キーとRSO同意を含む要件を満たせる
  場合に限る。
- **Apexのプレイヤー統計**: Apex Legends APIやTracker Networkの提供条件・対象プラット
  フォームを確認して選ぶ。大会統計ならDGS Ingramも候補。
- **SF6のランク・バトル履歴**: まずBuckler公式サイトを利用。機械取得は非公式かつ未保証な
  方法であることを前提に、公開サービス用途では公式許可を優先する。
- **LoLの試合・ランク・プレイヤー情報**: Riot公式API。チャンピオン・アイテム等の静的情報は
  Data Dragon。

いずれも、キーやログインCookieをクライアントコード・公開リポジトリに置かず、APIの利用規約、
レート制限、データの再配布条件を確認する。コミュニティAPIは、エンドポイントが現在応答する
ことだけで、将来の継続提供や商用利用が保証されるわけではない。

## 参考資料

- [Riot Developer Portal: VALORANT API Policy](https://developer.riotgames.com/docs/valorant)
  - 参照日: 2026-09-28
- [Riot Developer Portal: League of Legends API Policy](https://developer.riotgames.com/docs/lol)
  - 参照日: 2026-09-28
- [Riot Developer Portal Overview](https://developer.riotgames.com/docs/portal)
  - 参照日: 2026-09-28
- [Riot Developer Portal API Catalog](https://developer.riotgames.com/apis)
  - 参照日: 2026-09-28
- [Data Dragon CDN](https://ddragon.leagueoflegends.com/cdn/)
  - 参照日: 2026-09-28
- [CommunityDragon](https://communitydragon.org/)
  - 参照日: 2026-09-28
- [VALORANT-API.com](https://valorant-api.com/)
  - 参照日: 2026-09-28
- [Monster Hunter: Wilds API Reference](https://docs.wilds.mhdb.io/)
  - 参照日: 2026-09-28
- [Monster Hunter World API documentation](https://docs.mhw-db.com/)
  - 参照日: 2026-09-28
- [MonHun-API GitHub repository](https://github.com/pkwlo/MonHun-API)
  - 参照日: 2026-09-28
- [Apex Legends API documentation](https://apexlegendsapi.com/)
  - 参照日: 2026-09-28
- [Tracker Network: Apex Legends API](https://tracker.gg/developers/docs/titles/apex)
  - 参照日: 2026-09-28
- [Apex Legends Status: DGS "Ingram" API](https://apexlegendsstatus.com/tournament-stable/api)
  - 参照日: 2026-09-28
- [Buckler's Boot Camp](https://www.streetfighter.com/6/buckler/en/welcome)
  - 参照日: 2026-09-28
- [Buckler API Notes: Undocumented SF6 Data Routes](https://sfstats.app/buckler)
  - 参照日: 2026-09-28
- [Street Fighter 6 Terms of Service and EULA](https://www.streetfighter.com/6/eula/ps/en/)
  - 参照日: 2026-09-28

## 更新履歴

- 2026-10-08: yomiyasuの原則に基づき本文を推敲
- 2026-09-28: モンスターハンター、VALORANT、Apex Legends、SF6、LoLで利用できる公式・コミュニティAPIを比較して初版を作成
