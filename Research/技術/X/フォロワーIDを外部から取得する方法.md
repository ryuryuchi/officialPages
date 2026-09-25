---
作成日: 2026-08-25
更新日: 2026-08-31
タグ:
  - X
  - Twitter
  - API
  - フォロワー
  - ユーザーID
状態: 完了
---

# XのフォロワーIDを外部から取得する方法

## 概要

X（旧Twitter）のあるアカウントを対象に、外部のアプリケーションからフォロワーの
ユーザーIDを取得できるかを調べた。

## 結論

可能である。公式X API v2の`GET /2/users/{id}/followers`を利用すると、指定ユーザーの
フォロワーを`data`配列で取得でき、各要素の`id`がXのユーザーIDである。

ただし、無認証では取得できない。X DeveloperアカウントとApp、認証情報、従量課金用の
クレジットが必要である。2026-08-31時点の公式OpenAPIでは、アプリ専用Bearer Token、
OAuth 1.0aユーザーコンテキスト、またはOAuth 2.0ユーザーコンテキストを利用できる。
取得不能なユーザーや部分エラーもあり得るため、`errors`も処理する。画面スクレイピング
ではなく公式APIを使い、X Developer Policyと適用法令に従う。

## 詳細

### 利用するエンドポイント

- エンドポイント: `GET https://api.x.com/2/users/{id}/followers`
- `{id}`: 対象アカウントの1～19桁の数値ユーザーID
- 返却形式: `data`にユーザーオブジェクトの配列が入り、各要素の`id`がフォロワーID
- 1回の取得件数: `max_results`で1～1,000件（公式Quickstart記載の既定値は100）
- 続きを取得する方法: 応答の`meta.next_token`を次回の`pagination_token`に指定する
- 追加フィールド: `user.fields`で`username`、`protected`、`public_metrics`などを指定する
- レート制限: 2026-08-31時点ではアプリ単位・ユーザー単位とも300リクエスト/15分

概念的なリクエスト例は次のとおり。

```text
GET https://api.x.com/2/users/{対象ユーザーID}/followers?max_results=1000
Authorization: Bearer <access-token>
```

OAuth 2.0ユーザーコンテキストでは、`follows.read`、`tweet.read`、`users.read`の各
スコープが必要である。対象をユーザー名しか知らない場合は、先に
`GET /2/users/by/username/{username}`で数値IDを取得する。

### ページネーションの処理

1. 最初の応答から`data[].id`を保存する。
2. `meta.next_token`があれば、同じ条件に
   `pagination_token={next_token}`を加えて次ページを取得する。
3. `next_token`がなくなるまで繰り返す。
4. `data`だけでなく`errors`、HTTPステータス、レート制限ヘッダーを記録する。

一覧は取得中にも変化し得るため、複数ページの結果は厳密な同一時点スナップショットとは
限らない。定期同期では取得時刻を保存し、IDで重複排除する。

### 費用と運用上の注意

- X APIは前払いクレジットを使う従量課金で、サブスクリプションではない。
  2026-08-31時点の公式価格表では、Following/Followers Readは返却1リソース当たり
  0.010米ドルである。
- App所有者自身が認証し、`{id}`もその本人である場合はOwned Readsとなり、
  1リソース当たり0.001米ドルである。
- 読み取りリソースは同一UTC日内で重複排除されると案内されているが、公式資料はこれを
  soft guaranteeとしている。料金・制限は変更され得るため、実行直前にDeveloper Console
  も確認する。
- レート上限を超えるとHTTP 429になる。`x-rate-limit-limit`、
  `x-rate-limit-remaining`、`x-rate-limit-reset`を監視して待機・再試行する。
- API応答の`errors`を無視しない。権限、対象ユーザーの状態、利用プラン、停止・削除
  されたアカウントなどによる欠落を、完全取得として扱わない。
- 公式Developer Guidelinesは公式APIのみを使い、スクレイピングやブラウザー自動化を
  避けるよう案内している。

### 「外部から」の範囲

ここでいう「外部」は、XのWeb画面以外の自作プログラムや外部サービスを指す。APIで
取得可能であることは、第三者が無制限・無条件にユーザーデータを収集、保存、公開して
よいことを意味しない。目的、保存期間、アクセス制御、削除対応を定め、X Developer
Policy、ユーザーの合理的なプライバシー期待、個人情報保護法その他の適用法令を確認する。

## 参考資料

- [Get Users Followers - X API](https://docs.x.com/x-api/users/get-followers)
  - 参照日: 2026-08-31
- [Follows Quickstart - X API](https://docs.x.com/x-api/users/follows/quickstart)
  - 参照日: 2026-08-31
- [X API pay-per-usage pricing and credits](https://docs.x.com/x-api/getting-started/pricing.md)
  - 参照日: 2026-08-31
- [X API Rate Limits](https://docs.x.com/x-api/fundamentals/rate-limits)
  - 参照日: 2026-08-31
- [Authentication](https://docs.x.com/fundamentals/authentication/overview.md)
  - 参照日: 2026-08-31
- [X Developer Policy](https://docs.x.com/developer-terms/policy)
  - 参照日: 2026-08-31
- [Developer Guidelines - X API](https://docs.x.com/developer-guidelines.md)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLと公式OpenAPIを再確認し、認証方式、ページネーション、レート制限、従量課金、データ取扱上の注意を更新
- 2026-08-25: 初版を作成
