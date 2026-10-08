---
作成日: 2026-09-28
更新日: 2026-09-28
タグ:
  - JavaScript
  - 静的サイト
  - 動的UI
  - アニメーション
  - ブラウザーAPI
状態: 完了
---

# 静的JavaScriptサイトでできることと制約

## 概要

静的ホスティングで公開するHTML・CSS・JavaScriptのサイトで、どのような操作、
アニメーション、データ処理ができるかを整理する。サーバーやデータベースが必要に
なる境界も確認する。

## 結論

静的サイトでも、クリックに反応するUI、画面内容の切り替え、入力フォーム、
アニメーション、ゲームやグラフなどを作れる。JavaScriptは閲覧者のブラウザーで
実行されるため、画面内で完結する動作なら、サイト用のアプリケーションサーバーが
なくても実現できる。

一方、JavaScriptだけではサーバー上に秘密を隠したり、全利用者で共有するデータを
安全に保存したりできない。ログイン後のデータ保護、共有データベース、秘密のAPIキー、
サーバー側の定期処理などが必要なら、API、認証サービス、データベース、サーバーレス
機能などを別に用意する。

## 詳細

### 「静的サイト」でも画面は動かせる

ここでいう静的サイトは、Webサーバーが完成済みのHTML、CSS、JavaScriptなどの
ファイルを配信するサイトを指す。ページを開いた後はJavaScriptがブラウザーで動くため、
利用者の操作に応じて画面を書き換えられる。静的ホスティングのGitHub Pagesも、
HTML・CSS・JavaScriptを公開するサービスとして説明されている。

### できること

| 種類 | 例 | サーバーなしで可能か |
| --- | --- | --- |
| 動くUI | メニュー、タブ、アコーディオン、モーダル、ステップ表示、画面の切り替え | 可能 |
| 一覧の操作 | ダウンロード済みデータの検索、絞り込み、並べ替え、ページ送り | 可能 |
| 入力への反応 | 入力チェック、計算、プレビュー、進捗表示、簡単なフォーム | 可能。ただし重要な検証はサーバー側でも行う |
| 見た目や演出 | ホバー効果、画面遷移、通知、ローディング表示、グラフ、ゲーム | 可能 |
| ブラウザー内の保存 | テーマ設定、下書き、チェック状態、端末内データ | 可能。保存先は利用者のブラウザー |
| 外部サービスとの通信 | 天気、公開API、外部フォームや認証サービスとの連携 | API側の公開条件、認証方式、CORS設定による |
| オフライン利用 | キャッシュ済みページの表示や、端末内データを使う機能 | Service Workerなどで可能。事前設計が必要 |

たとえば、次のような小さなWebツールは静的サイトと相性がよい。

- 料金・単位・日付などの計算ツール
- FAQや商品リストを条件で絞り込むページ
- アンケートの入力補助や、その場で結果を表示する診断
- ブラウザー内に下書きを保存するメモ
- クイズ、カード、簡単なゲーム
- ボタン操作に反応する説明画面、グラフ、アニメーション

### アニメーションや動くUI

アニメーションは可能である。単純な色・位置・サイズの変化にはCSSの
`transition`や`@keyframes`、JavaScriptから再生・停止・時間を制御したい場合には
Web Animations API、図形を連続的に描画する場合にはCanvasなどを使える。
ボタンのクリックをきっかけにパネルを開く、通知を表示する、画面を切り替える、と
いった動きもブラウザー内で作れる。

ただし、動きを多用すると操作しづらくなったり、端末によって重くなったりする。
キーボード操作やフォーカス位置を保ち、画面読み上げに状態変化を伝え、OSの
「視差効果を減らす」設定（`prefers-reduced-motion`）にも配慮する。

### データの保存と外部API

`localStorage`は小さな文字列データ、IndexedDBは構造化データなどをブラウザー内に
保存する用途に使える。これらは利用者の端末・ブラウザーに属する保存先であり、
サーバーへのバックアップや複数端末間の同期にはならない。また、利用者が消去でき、
容量などの制限もある。秘密情報やAPIキーを保存する場所としても使えない。

JavaScriptから`fetch`で外部APIへ通信することもできる。ただし、相手のサーバーが
ブラウザーからのアクセスを許可している必要があり、別ドメインへの通信はCORSなどの
制約を受ける。CORSはフロントエンドのJavaScriptだけで解除できず、APIを提供する側の
設定が必要である。

### 同じ公開フォルダーのJSONをフォームに表示する

HTMLと同じフォルダーに`data.json`を置き、`fetch("./data.json")`で読み込める。
読み取った配列から`<option>`を作れば、フォームの選択肢をJSONの内容で表示できる。
`fetch`は相対URLをページのURLから解決するため、ページの置き場所に合わせてパスを
指定する。

例として、次のJSONを公開フォルダーに置く。

```json
[
  { "id": "a", "label": "りんご" },
  { "id": "b", "label": "みかん" }
]
```

HTMLに選択欄と状態表示を置く。

```html
<label for="item">項目</label>
<select id="item"></select>
<p id="status" role="status"></p>
<script type="module" src="./app.js"></script>
```

`app.js`でJSONを読み込み、選択肢へ反映する。

```javascript
const select = document.querySelector("#item");
const status = document.querySelector("#status");

async function loadItems() {
  if (!(select instanceof HTMLSelectElement) || !(status instanceof HTMLElement)) {
    throw new Error("フォーム要素が見つかりません。");
  }

  const response = await fetch("./data.json");
  if (!response.ok) {
    throw new Error(`JSONの取得に失敗しました: HTTP ${response.status}`);
  }

  const items = await response.json();
  if (
    !Array.isArray(items) ||
    !items.every(
      (item) =>
        item !== null &&
        typeof item === "object" &&
        typeof item.id === "string" &&
        typeof item.label === "string",
    )
  ) {
    throw new TypeError("JSONの形式が正しくありません。");
  }

  select.replaceChildren(new Option("選択してください", ""));
  for (const item of items) {
    const option = new Option(item.label, item.id);
    select.append(option);
  }
}

loadItems().catch((error) => {
  console.error("JSONの読み込みに失敗しました。", error);
  if (status instanceof HTMLElement) {
    status.textContent = "データを読み込めませんでした。";
  }
});
```

この方法は、静的ホスティングへ`data.json`も公開しておく必要がある。公開したJSONは
URLを知る人が取得できるため、個人情報や秘密情報を含めない。`fetch`はHTTPエラーで
自動的に失敗扱いにならないため、例のように`response.ok`を確認する。HTMLを
`file://`で直接開くとブラウザーのセキュリティ制約で取得できない場合があるので、
ローカル開発サーバーまたは公開先のHTTPSで確認する。GitHub Pagesのプロジェクトサイト
などでページがサブパスにある場合は、ファイルの配置に合う相対パスを使う。

### 静的サイトだけではできないこと・苦手なこと

| 要件 | 静的サイトだけでは難しい理由 | 必要になるもの |
| --- | --- | --- |
| サーバーでの処理 | 静的ホスティングは、リクエストごとに独自プログラムを実行しない | APIサーバー、サーバーレス関数など |
| 全利用者で共有する保存 | `localStorage`やIndexedDBは各利用者のブラウザー内にある | APIとデータベース、またはBaaS |
| 秘密のAPIキーの保管 | 配信したJavaScriptや設定値は利用者が調べられる | 秘密情報を保持するサーバー側のAPI |
| 保護されたデータの認可 | 画面を隠すだけではデータへのアクセスを制限できない | 認証サービスと、サーバー側での認可チェック |
| 長時間・定期的な処理 | ブラウザーやタブを閉じると、常時実行を前提にできない | サーバー側のジョブやスケジューラー |

外部の認証サービスやデータサービスを使えば、静的なフロントエンドからログインや
データ操作を開始する構成も作れる。ただし、認証情報やデータへのアクセス制御を
フロントエンドだけに任せず、APIやサービス側で検証する必要がある。

### ブラウザーと利用者の制約

JavaScriptが使える機能は、ブラウザーの種類・バージョン、権限、セキュリティ設定に
左右される。位置情報、カメラ、マイクなどは、対応ブラウザーに加えてHTTPSなどの
安全な接続と利用者の許可が必要になる。PC内の任意のファイルを無断で読み書きする
こともできず、ファイル選択など利用者の明示的な操作が必要である。

したがって、重要な操作にはエラー表示や代替手段を用意し、異なる画面サイズ、
キーボード操作、支援技術でも使えるようにする。

### 用途の判断

- **静的サイト向き**: 画面内の操作、計算、表示切り替え、公開データの検索、端末内の設定保存。
- **バックエンドを追加**: 利用者間の共有、複数端末での同期、非公開データ、決済、
  信頼できるログイン・認可、定期実行。

「動くUIが欲しい」だけなら、まずHTML・CSS・JavaScriptで始められる。画面や機能が
増えてから、必要に応じてフレームワークやバックエンドを選べばよい。

### 関連メモ

- [静的サイトジェネレーターの基本](../HTML/静的サイトジェネレーターの基本.md):
  静的HTMLの生成と、ビルド時・アクセス時の処理の違い。
- [GitHub Pagesの基本と公開方法](../Git/GitHub%20Pagesの基本と公開方法.md):
  静的ファイルの公開方法とホスティング側の制約。

## 参考資料

- [DOM scripting introduction - Learn web development | MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/DOM_scripting)
  - 参照日: 2026-09-28
- [Using CSS animations - CSS | MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Animations/Using)
  - 参照日: 2026-09-28
- [Using the Web Animations API - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API/Using_the_Web_Animations_API)
  - 参照日: 2026-09-28
- [Canvas API - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
  - 参照日: 2026-09-28
- [Using the Fetch API - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
  - 参照日: 2026-09-28
- [Cross-Origin Resource Sharing (CORS) - HTTP | MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
  - 参照日: 2026-09-28
- [Window: localStorage property - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
  - 参照日: 2026-09-28
- [Client-side storage - Learn web development | MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Client-side_APIs/Client-side_storage)
  - 参照日: 2026-09-28
- [IndexedDB API - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
  - 参照日: 2026-09-28
- [Using Service Workers - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers)
  - 参照日: 2026-09-28
- [Geolocation API - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)
  - 参照日: 2026-09-28
- [MediaDevices: getUserMedia() method - Web APIs | MDN](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
  - 参照日: 2026-09-28
- [prefers-reduced-motion CSS media feature - CSS | MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion)
  - 参照日: 2026-09-28
- [What is GitHub Pages? - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
  - 参照日: 2026-09-28
- [GitHub Pages limits - GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
  - 参照日: 2026-09-28

## 更新履歴

- 2026-09-28: 同じ公開フォルダーのJSONをfetchし、フォームへ表示する例と公開・パス上の注意を追加
- 2026-09-28: 静的サイトで可能な動的UI、アニメーション、保存・API連携とバックエンドの境界を整理
