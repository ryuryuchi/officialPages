---
作成日: 2026-08-31
更新日: 2026-08-31
タグ:
  - HTML
  - CSS
  - スタイルシート
  - 保守
状態: 完了
---

# 複数HTMLにCSSを共通適用する方法

## 概要

複数の既存HTMLファイルへ同じCSSを適用し、後から一括でデザインを変更しやすくする方法を整理する。

## 結論

最適な基本方法は、共通スタイルを1つの外部CSSファイルへまとめ、各HTMLの`<head>`から`<link rel="stylesheet">`で読み込む構成である。CSSの修正が参照中の全ページへ反映されるため、各HTMLへ同じ`<style>`を複製するより保守しやすい。

```html
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="assets/css/common.css">
  <title>ページタイトル</title>
</head>
```

ページ固有の装飾がある場合は、共通CSSを先、ページ固有CSSを後に読み込む。

```html
<link rel="stylesheet" href="/assets/css/common.css">
<link rel="stylesheet" href="/assets/css/products.css">
```

既存HTMLが多い場合でも、最初に各ファイルへ`link`要素を一括追加すれば、その後の共通デザイン変更は原則としてCSSファイルだけで行える。今後もページを増やすサイトでは、テンプレートまたは静的サイトジェネレーターで共通の`head`を生成すると、`link`要素自体の管理も一元化できる。

## 詳細

### 推奨するファイル構成

```text
site/
├─ index.html
├─ about.html
├─ products/
│  └─ index.html
└─ assets/
   └─ css/
      ├─ common.css
      └─ products.css
```

`common.css`には、色、文字、余白、ヘッダー、フッターなど全ページ共通の規則を置く。ページ固有の規則は別ファイルに分けるか、規模が小さければページを表すクラスの内側にまとめる。

```html
<body class="page-products">
```

```css
.page-products .product-list {
  display: grid;
}
```

### CSSを読み込むパスの選び方

HTMLの`href`はHTML文書のURLを基準に解決される。配置に応じて次のように使い分ける。

| 指定 | 例 | 向く状況 | 注意点 |
| --- | --- | --- | --- |
| 文書相対URL | `assets/css/common.css`、`../assets/css/common.css` | PC上でHTMLを直接開く場合、小規模な静的ファイル群 | HTMLの階層ごとに記述が変わる |
| ルート相対URL | `/assets/css/common.css` | Webサーバー上で同じサイトルートから配信する場合 | `file://`で直接開く用途には不向き。サブパス配信では公開ルートを確認する |
| 絶対URL | `https://example.com/assets/css/common.css` | 複数サイトや異なる配信元で同じCSSを使う場合 | ドメイン変更、通信障害、CSPなどの影響を受ける |

CSS内の`url(...)`で指定する背景画像やフォントの相対URLは、HTMLではなく、そのCSSファイルの場所を基準に解決される。

```css
/* assets/css/common.css から assets/images/logo.svg を参照 */
.site-logo {
  background-image: url("../images/logo.svg");
}
```

### 既存CSSと併用する場合

CSSの競合結果は、スタイルの出所、カスケードレイヤー、詳細度、適用範囲、記述順などで決まる。同じ優先度と詳細度なら、後に現れる宣言が優先される。このため、既存CSSを残しながら新しい共通CSSで上書きする移行では、新しいCSSを後に読み込む。

```html
<link rel="stylesheet" href="/assets/css/legacy.css">
<link rel="stylesheet" href="/assets/css/common.css">
```

ただし、読み込み順だけに頼った上書きを増やすと保守しにくい。次の順で整理する。

1. ブラウザーの開発者ツールにあるComputedまたはStylesで、どの規則が勝っているか確認する。
2. 共通部品にはクラスセレクターを使い、ページ固有規則は`body`のページクラスなどで適用範囲を限定する。
3. セレクターの過度な詳細化と`!important`の常用を避ける。
4. 移行後に不要になった重複規則を削除する。

より大きいサイトでは`@layer`で既存CSS、共通部品、ページ固有規則などの優先順を明示する方法もある。ただし、既存CSSへ段階的に導入する際は、レイヤー外の通常スタイルがレイヤー内の通常スタイルより優先される点を理解して設計する必要がある。

### `link`と`@import`の使い分け

HTMLから主要なCSSを読み込む用途では`link`を基本とする。

```html
<link rel="stylesheet" href="/assets/css/common.css">
```

`@import`も別のスタイルシートを読み込めるが、CSS内に依存関係が隠れ、インポート規則を他の通常規則より前へ記述する制約がある。カスケードレイヤーやメディア条件を付けてCSS側で構成を制御したい場合には有効だが、単に複数HTMLで共通CSSを共有する目的なら`link`の方が構成を把握しやすい。

### 多数の既存HTMLへ導入する方法

対象が数ファイルなら、各`head`へ手作業で同じ`link`要素を追加するのが確実である。数十ファイル以上なら、次の方法で一度だけ一括追加する。

1. 先にバックアップまたはGitの作業ブランチを用意する。
2. HTMLの配置階層を確認し、全ファイルで同じURLを使えるか判断する。
3. 構造が統一されたHTMLなら、VS Codeの「ファイルを置換」などで`</head>`の直前へ`link`要素を追加する。
4. 構造が不統一、または既存の`link`有無が混在する場合は、正規表現による置換ではなくHTMLパーサーを使う一括処理を選ぶ。
5. 差分を確認し、二重追加、`head`外への追加、文字コードの変化がないことを確認する。

今後も各HTMLの共通部分を繰り返し変更するなら、HTMLテンプレート、静的サイトジェネレーター、またはサーバー側テンプレートへ移行する。外部CSSは「スタイルの一元管理」を解決するが、ナビゲーションや`head`などHTML断片の一元管理までは行わない。

### 避ける方法

- 各HTMLへ同じ`<style>`ブロックをコピーする。修正漏れやページ間の差異が発生しやすい。
- 各要素へ同じ`style`属性を付ける。再利用性が低く、外部CSSからの上書きも複雑になる。
- JavaScriptでCSSを後付けする。通常の静的なスタイル適用に不要な依存と表示の遅れを増やす。
- CSSファイルをページごとに丸ごと複製する。共通部分と固有部分を分けた方が変更箇所を追いやすい。
- URLの階層を確認せず、すべてのHTMLへ同じ文書相対URLを一括挿入する。

### 適用後の確認

代表ページだけでなく、異なる階層と異なるレイアウトのページを選んで確認する。

- 開発者ツールのNetworkでCSSが`200`またはキャッシュから正常に取得され、`404`になっていない。
- ConsoleにCSP違反やMIMEタイプのエラーがない。
- ComputedまたはStylesで意図した規則が適用されている。
- PC幅とスマートフォン幅で、主要な画面崩れがない。
- CSSファイルを1か所変更すると、参照する複数ページへ反映される。
- 公開環境で古いCSSが残る場合は、配信時のキャッシュ設定を確認する。更新ごとに無条件でクエリー文字列を変える運用は、キャッシュ効率との兼ね合いを考えて採用する。

## 参考資料

- [MDN: link - The External Resource Link element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/link)
  - 参照日: 2026-08-31
- [WHATWG HTML Living Standard: Link type stylesheet](https://html.spec.whatwg.org/multipage/links.html#link-type-stylesheet)
  - 参照日: 2026-08-31
- [MDN: Introduction to the CSS cascade](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Introduction)
  - 参照日: 2026-08-31
- [MDN: url CSS type](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/url_value)
  - 参照日: 2026-08-31
- [MDN: @import](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@import)
  - 参照日: 2026-08-31
- [MDN: Organizing your CSS](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Organizing)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを実査し、`link`、URL解決、カスケード、`@import`の記述が現行仕様と一致することを確認
- 2026-08-31: 初版を作成
