---
作成日: 2026-08-27
更新日: 2026-10-08
タグ:
  - Excel
  - HTML
  - Officeアドイン
  - Power Query
状態: 完了
---

# ExcelにHTMLを表示する方法

## 概要

HTMLをExcelのセル内やワークシート上に、Webブラウザーと同じ見た目で表示できるかを調査した。HTMLの表示、Webデータの取り込み、外部ブラウザーで開く方法を区別し、用途別の選択肢を整理する。

## 結論

セルにHTML文字列を入れるだけでは、HTMLとして描画されない。`<b>太字</b>`などのタグも文字列として表示される。

ワークシート上にブラウザーに近い表示領域を置くことは可能である。Microsoftが提供するOfficeアドインの「コンテンツアドイン」を使うと、HTML、CSS、JavaScriptで作ったUIをシートへ直接埋め込める。Excel画面の右側に表示する「作業ウィンドウアドイン」も選べる。

HTMLの表データだけが必要なら、Power Queryの「データ > Webから」が適している。これはWebページ全体を表示するのではなく、検出した表をExcelのセルへ読み込む機能である。

表示だけなら、ハイパーリンクで既定のブラウザーを開く方法が最も簡単で安全である。

VBAの古いWebBrowserコントロールでもHTMLを表示できる場合がある。しかし、Windows依存、古い描画エンジン、配布や保守の難しさがあるため、新規構築ではOfficeアドインを優先する。

## 詳細

### 「そのまま表示」の意味別の可否

| やりたいこと | 可否 | 適した方法 |
|---|---|---|
| セル内のHTMLタグをブラウザーのように描画する | 不可 | 必要な文字や書式へ変換してセルへ設定する |
| HTMLの表をセルへ取り込む | 可能 | Power Queryの「Webから」 |
| HTML UIをワークシート上に埋め込む | 可能 | Officeのコンテンツアドイン |
| HTML UIをExcel画面の右側に表示する | 可能 | Officeの作業ウィンドウアドイン |
| Webページを別画面で表示する | 可能 | `HYPERLINK`関数または通常のハイパーリンク |
| HTMLの見た目だけをシート上に置く | 可能 | ブラウザーで表示して画像として貼り付ける |

### 1. セルはHTMLレンダラーではない

セルに次の文字列を貼り付けても、太字の「重要」にはならず、タグを含む文字列として扱われる。

```html
<b>重要</b>
```

表示したい内容が限定的なら、HTMLを解析し、`<br>`をセル内改行へ、`<b>`や`<strong>`の範囲を太字書式へ、`<ul>`や`<ol>`を記号付き・番号付きのテキストへ変換する方法もある。画像は別途ダウンロードして貼り付ける。

ただし、これはHTMLを描画するのではなく、Excelで扱える値や書式へ個別に変換する処理である。CSSレイアウト、JavaScript、フォームなどを同じように再現することはできない。

### 2. シート上でHTMLを本当に描画する

MicrosoftのExcelアドインには、WebベースのUIを表示する仕組みがある。コンテンツアドインはワークシートへ直接埋め込み、作業ウィンドウアドインはExcel画面の右側に表示する。

アドインはWebアプリとマニフェストで構成され、HTML、CSS、JavaScriptを使用する。
2026年8月時点のMicrosoft Learnでは、Windows版ではEdge WebView2、MacとiOSではSafari WKWebView、AndroidではChrome、Excel for the webでは利用中のブラウザーが表示を担当する。利用できるAPIは、Excelの版とプラットフォームごとの要件セットも確認する。

これは、任意のHTMLファイルをセルへ貼り付ける機能ではない。Officeアドインとして開発・配布する必要がある。社内だけで使う場合でも、マニフェストの用意、Webコンテンツのホスト、組織のアドイン配布・信頼設定などを検討する。

### 3. HTMLの表をExcelデータとして取り込む

HTMLページ中の表を編集・集計したい場合は、次の手順でPower Queryを使う。

1. `データ`タブを開く。
2. `Webから`を選ぶ。
3. URLを入力して接続する。
4. ナビゲーターで検出された表を選ぶ。
5. `読み込み`または`データの変換`を選ぶ。

読み込まれるのは表データであり、元ページ全体のレイアウトではない。Webコネクターには`Web.BrowserContents`のようにWebView2を必要とする機能もあるが、取得結果は最終的にExcelの表として扱われる。

### 4. 表示だけならブラウザーで開く

セルからWebページを開くだけなら、次の式で十分である。

```excel
=HYPERLINK("https://example.com/page.html","HTMLを開く")
```

クリックすると、Excel内ではなく、対象の文書またはURLが開かれる。Excel for the webの`HYPERLINK`関数では、リンク先はWebアドレスに限定される。

### 5. 方式の選び方

Webページを見せたいだけならハイパーリンク、見た目を固定して資料に載せたいなら画像として貼り付ける。Web上の表を集計したい場合はPower Query、Excel内で操作できるHTML UIが必要ならOfficeアドインを使う。HTML付き文章をセルへ入れたい場合は、必要なタグだけExcel書式へ変換する。

「HTMLをそのまま表示」に最も近いのはコンテンツアドインだが、簡単さではハイパーリンク、データ利用ではPower Queryが適している。

## 参考資料

- [Build Excel add-ins with Office Add-ins - Microsoft Learn](https://learn.microsoft.com/en-us/office/dev/add-ins/excel/excel-add-ins-overview)
  - 参照日: 2026-08-31
- [Content Office Add-ins - Microsoft Learn](https://learn.microsoft.com/en-us/office/dev/add-ins/design/content-add-ins)
  - 参照日: 2026-08-31
- [Browsers and webview controls used by Office Add-ins - Microsoft Learn](https://learn.microsoft.com/en-us/office/dev/add-ins/concepts/browsers-used-by-office-web-add-ins)
  - 参照日: 2026-08-31
- [Power Query Web Connector - Microsoft Learn](https://learn.microsoft.com/en-us/power-query/connectors/web/web)
  - 参照日: 2026-08-31
- [Import data from the web using the web connector - Microsoft Support](https://support.microsoft.com/en-us/excel/get-started/import-data-from-the-web)
  - 参照日: 2026-08-31
- [HYPERLINK function - Microsoft Support](https://support.microsoft.com/en-us/excel/functions/hyperlink-function)
  - 参照日: 2026-08-31
- [Displaying HTML in an Excel cell - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/5405884/displaying-html-in-an-excel-cell)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-10-08: yomiyasuで本文の構成と表現を再点検し、箇条書きと太字を整理
- 2026-10-08: yomiyasuの原則に基づき本文を推敲
- 2026-08-31: 全参考URLと本文事実を再確認し、Officeアドインの現行WebView構成と要件セットの注意を更新
- 2026-08-27: 初版を作成
