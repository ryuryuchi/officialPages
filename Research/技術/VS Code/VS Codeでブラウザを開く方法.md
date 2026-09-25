---
作成日: 2026-09-01
更新日: 2026-09-01
タグ:
  - VS Code
  - ブラウザ
  - HTML
  - Integrated Browser
状態: 完了
---

# VS Codeでブラウザを開く方法

## 概要

VS Code内でWebページを開く方法と、HTMLのプレビュー、外部ブラウザへの切り替えを整理する。

## 結論

URLをVS Code内で開くだけなら、拡張機能は不要である。`Ctrl+Shift+P`でコマンドパレットを開き、`Browser: Open Integrated Browser`を実行してURLを入力する。

HTMLファイルは、エクスプローラーまたはエディターのタブを右クリックし、`Open in Integrated Browser`を選ぶとプレビューできる。外部ブラウザでローカル開発サーバーを確認したい場合は、設定でlocalhostリンクの動作を切り替えるか、ライブリロードが必要ならLive Server拡張機能を使う。

## 詳細

### WebページをVS Code内で開く

1. `Ctrl+Shift+P`または`F1`でコマンドパレットを開く。
2. `Browser: Open Integrated Browser`を選ぶ。
3. アドレスバーに`https://example.com`などのURLを入力し、`Enter`を押す。

メニューバーの`View` > `Browser`や、タイトルバーの地球儀ボタンからも開ける。Integrated Browserは`http://`、`https://`、`file://`に対応し、複数のブラウザータブをVS Code内に開ける。

通常のブラウザより機能が限定される場合があり、ポップアップはブロックされる。普段のWeb閲覧よりも、開発中の画面確認やデバッグに向いている。

### HTMLファイルをプレビューする

1. VS CodeでHTMLファイルを開く。
2. エクスプローラー上のファイル、またはエディターのタブを右クリックする。
3. `Open in Integrated Browser`を選ぶ。

HTMLファイルを開いているときは、エディター右上の`Show Preview`アイコンからも表示できる。HTMLを変更すると、プレビューへリアルタイムに反映される。

`file://`での表示では、JavaScriptモジュール、`fetch`、ルーティングなどがブラウザのセキュリティ制約で正しく動かない場合がある。その場合は、プロジェクトの開発サーバーを起動して`http://localhost:ポート番号`を開く。

### localhostを外部ブラウザで開く

現行のVS Codeでは、ターミナルやチャットに表示されたlocalhostリンクは、既定でIntegrated Browserに開く。

OSの既定ブラウザで開くようにするには、設定画面で`workbench.browser.openLocalhostLinks`を無効にする。使用する外部ブラウザを固定する場合は、`workbench.externalBrowser`に`edge`、`chrome`、`firefox`、またはブラウザ実行ファイルの絶対パスを設定する。

設定例:

```json
{
  "workbench.browser.openLocalhostLinks": false,
  "workbench.externalBrowser": "edge"
}
```

この設定後、ターミナルなどの`http://localhost:3000`といったリンクを選択すると外部ブラウザで開く。Integrated Browserは、コマンドパレットから引き続き明示的に開ける。

### Live Server拡張機能を使う場合

静的なHTML、CSS、JavaScriptを外部ブラウザで確認し、保存時に自動再読み込みしたい場合は、サードパーティー製のLive Server拡張機能を利用できる。

1. 拡張機能ビューを開き、`Live Server`を検索してインストールする。
2. HTMLファイルを開く。
3. ステータスバーの`Go Live`、または右クリックメニューの`Open with Live Server`を選ぶ。

単にHTMLをVS Code内で確認するだけなら、標準のIntegrated Browserを先に試す。React、Vue、Viteなどのプロジェクトでは、Live Serverではなく、そのプロジェクトが用意する開発サーバーを使う。

### コマンドが見つからない場合

`Browser: Open Integrated Browser`や`Open in Integrated Browser`が見つからない場合は、VS Codeを最新版へ更新して再確認する。古い環境では、組み込みのSimple Browserが提供する簡易プレビューを利用できる場合もあるが、現行の公式ドキュメントではIntegrated Browserが案内されている。

## 参考資料

- [Integrated browser](https://code.visualstudio.com/docs/debugtest/integrated-browser)
  - 参照日: 2026-09-01
- [HTML in Visual Studio Code](https://code.visualstudio.com/docs/languages/html)
  - 参照日: 2026-09-01
- [Simple Browser README](https://github.com/microsoft/vscode/blob/main/extensions/simple-browser/README.md)
  - 参照日: 2026-09-01
- [Live Server - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)
  - 参照日: 2026-09-01

## 更新履歴

- 2026-09-01: 初版を作成
