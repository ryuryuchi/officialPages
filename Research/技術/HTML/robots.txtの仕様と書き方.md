---
作成日: 2026-09-08
更新日: 2026-09-08
タグ:
  - robots.txt
  - クローラー
  - SEO
  - Web公開
状態: 完了
---

# robots.txtの仕様と書き方

## 概要

Webサイトの`robots.txt`について、目的、標準仕様（Robots Exclusion Protocol: REP）、実際に記載する項目、書式と照合の規則、利用時の注意を整理する。

## 結論

`robots.txt`は、検索エンジンなどのクローラーへ「どのURLパスをクロールしてよいか」を伝えるための公開テキストファイルである。サイトのルートに小文字で`/robots.txt`として置き、UTF-8の`text/plain`で配信する。

標準で中心となる項目は、対象クローラーを指定する`User-agent`、許可する`Allow`、禁止する`Disallow`である。ルールはアクセス制御でもインデックス削除手段でもない。非公開情報は認証で保護し、検索結果から確実に除外したいHTML等は、クロール可能な状態で`noindex`を返すか、認証・削除など目的に合う方法を使う。

## 詳細

### 役割と適用範囲

- **事実**: REPは、クローラーにURIへのアクセス方法を知らせ、クローラーが尊重することを求めるプロトコルである。RFC 9309は、これは認可（アクセス権の制御）ではないと明記している。
- **事実**: HTTP(S)での標準的な配置先は`https://example.com/robots.txt`である。`https://example.com/folder/robots.txt`のようなサブディレクトリ内のファイルは、Googleのrobots.txtとしては有効ではない。
- **事実**: Googleでは、ルールはその`scheme`、ホスト、ポートの組合せだけに適用される。したがって、`https://example.com/robots.txt`は`https://www.example.com/`、`http://example.com/`、別ポートには自動では適用されない。
- **判断**: 本番サイトでは、公開するホストごとに必要性を確認して配置する。クロールを制限する理由がなければ、空の`robots.txt`を置く必要はない。

### 基本の書式

各行は`項目名: 値`で書く。項目名は大文字・小文字を区別しないが、パスは大文字・小文字を区別するものとして書く。行頭・行末の空白は避け、説明には`#`から始めるコメントを使う。

```text
# 全クローラーを対象にするグループ
User-agent: *

# 管理画面と検索結果ページはクロールさせない
Disallow: /admin/
Disallow: /search

# /private/全体を禁止しつつ、この公開ファイルだけは許可する
Disallow: /private/
Allow: /private/public-guide.pdf

# サイトマップの場所（検索エンジン実装で広く対応）
Sitemap: https://example.com/sitemap.xml
```

空行はグループ内で使用できる。`User-agent`から次の`User-agent`またはファイル末尾までが一つのグループであり、連続する複数の`User-agent`は同じルール群を共有する。

```text
User-agent: ExampleBot
User-agent: AnotherBot
Disallow: /download/

User-agent: *
Disallow:
```

最後の`Disallow:`は空のパスであり、禁止ルールとしては無視される。そのため、上の例では一般のクローラーにクロール制限をかけない。

### 標準の項目と検索エンジン固有の項目

| 項目 | 意味 | RFC 9309での位置付け |
| --- | --- | --- |
| `User-agent` | ルールを適用するクローラー名。`*`は汎用グループ | 規定 |
| `Disallow` | 指定パスへのクロールを禁止する | 規定 |
| `Allow` | 指定パスへのクロールを許可する | 規定 |
| `Sitemap` | XMLサイトマップまたはサイトマップインデックスの絶対URL | 拡張項目。RFCはクローラーが解釈してよいとしている |
| `Crawl-delay` | リクエスト間隔を示す慣習的な拡張 | RFCには規定されず、Googleは対応しない |

`Sitemap`は特定の`User-agent`グループに属さない。Googleの説明では完全修飾URLで書き、複数行を指定できる。サイトマップのURLはrobots.txtと同じホストでなくてもよい。

### パスの照合規則

- **事実**: クローラーは、自身の製品トークンに一致する`User-agent`グループを大文字・小文字を区別せずに選ぶ。複数グループが一致するとき、RFC 9309ではそれらのルールを結合する。一致がなければ`User-agent: *`を使い、それもなければ制限は適用されない。
- **事実**: `Allow`と`Disallow`はURLパスの先頭から照合し、最も長く一致するルールを使う。同じ長さで`Allow`と`Disallow`が競合する場合は、`Allow`を優先する。
- **事実**: `*`は0文字以上の任意文字、`$`はパターン末尾を表す。`#`以降はコメントである。これらはRFC 9309でクローラーが対応すべき特殊文字として規定されている。
- **事実**: 日本語などASCII外の文字、および予約文字をパスに含める場合、RFC 9309ではUTF-8のパーセントエンコードをして照合する。実務ではURLに表示されるエンコード済みのパスを書く。

照合例は次のとおりである。

| ルール | 対象になる例 | 対象外の例 |
| --- | --- | --- |
| `Disallow: /draft/` | `/draft/a.html` | `/drafts/a.html` |
| `Disallow: /*.pdf$` | `/manual.pdf` | `/manual.pdf?lang=ja` |
| `Allow: /private/public-guide.pdf` | `/private/public-guide.pdf` | `/private/other.pdf` |

### 書くときの実務ルール

1. クロールを減らす目的を明確にする。ログイン後の画面、重複・検索結果URL、負荷が大きいパラメータURLなどが候補になる。
2. 禁止したい範囲をディレクトリ単位でまとめ、必要な公開物だけ長い`Allow`ルールで例外にする。
3. CSS、JavaScript、画像など、検索エンジンがページを理解・描画するために必要なリソースは、原則として禁止しない。
4. URLを実際に確認してから、先頭の`/`を含むパスを書く。`/admin/`と`/admin`は一致範囲が異なる。
5. ファイルをUTF-8のプレーンテキストで保存し、`Content-Type: text/plain`で配信する。RFC 9309はルートの小文字`/robots.txt`を要求する。
6. 公開後に`https://対象ホスト/robots.txt`を取得して、リダイレクト、HTTPエラー、文字化けがないことを確認する。Googleは通常最大24時間キャッシュするため、変更の即時反映は保証されない。

### 目的別に使い分けること

| 目的 | 適切な方法 |
| --- | --- |
| クロール負荷を減らす | `robots.txt`の`Disallow` |
| 検索結果に表示させない | クロールを許可した上で`noindex`、または認証・削除など |
| 非公開ページ・ファイルを守る | 認証・認可、ネットワーク制限などのアクセス制御 |
| URL一覧をクローラーへ知らせる | XMLサイトマップを用意し、必要に応じて`Sitemap`を記載 |

**注意**: robots.txtでクロールを禁止したURLでも、外部リンクなどからURL自体が検索結果に現れる可能性がある。また、ルールに従わないクローラーを技術的に止めるものではない。機密情報のパスを`Disallow`に書くと、むしろその存在を公表することにもなる。

## 参考資料

- [RFC 9309: Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html)
  - 参照日: 2026-09-08
- [Google Search Central: robots.txt の概要](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
  - 参照日: 2026-09-08
- [Google for Developers: Google における robots.txt 仕様の解釈](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)
  - 参照日: 2026-09-08
- [Sitemaps.org: Sitemap XML形式](https://www.sitemaps.org/protocol.html)
  - 参照日: 2026-09-08

## 更新履歴

- 2026-09-08: 初版を作成
