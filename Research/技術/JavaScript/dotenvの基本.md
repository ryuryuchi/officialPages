---
作成日: 2026-09-10
更新日: 2026-09-10
タグ:
  - dotenv
  - JavaScript
  - Node.js
  - 環境変数
状態: 完了
---

# dotenvの基本

## 概要

Node.jsアプリケーションで設定値や秘密情報を環境変数として扱うための
`dotenv`について、役割、導入方法、`.env`の書式、利用時の注意点を調べた。
Node.js本体に追加された`.env`対応との使い分けも整理する。

## 結論

`dotenv`は、プロジェクトの`.env`ファイルを読み込み、値を
`process.env`へ追加する依存関係のないNode.jsパッケージである。アプリの
ソースコードと環境ごとの設定値を分離したい場合に使える。

基本的な導入は`npm install dotenv`後、アプリケーションの早い段階で
`require('dotenv').config()`または`import 'dotenv/config'`を実行する方法である。
ただし、`.env`は秘密情報を含み得るため、通常はGitへコミットせず、`.gitignore`
へ追加する。キーをクライアントへ公開するフロントエンドへ渡す用途には、
秘密情報を置いてはならない。

Node.jsには`.env`を読む`--env-file`と`process.loadEnvFile()`があるため、
Node.jsだけで完結する新規アプリでは追加パッケージが不要な場合がある。
一方、`dotenv`はNode.js 12以上で動作し、既存コード、複数ファイルの統合、
`parse`や`populate`などのAPIを使う場合に選択肢になる。採用時は対象Node.jsの
バージョンと実行環境の方式を統一する。

## 詳細

### dotenvの役割

`dotenv`は`.env`を解析し、デフォルトでは現在の作業ディレクトリにある
`.env`の値を`process.env`へ設定する。OSや実行環境ですでに設定された値は、
`override: true`を指定しない限り上書きされない。環境変数をコードへ直書きせず、
開発・テスト・本番で設定を差し替えやすくするために使う。

### 導入と基本的な使い方

```bash
npm install dotenv
```

プロジェクトルートの`.env`に設定を書く。

```dotenv
PORT=3000
DATABASE_URL="postgres://localhost/example"
API_KEY="開発用のキー"
```

CommonJSでは、`process.env`を参照する処理より前に読み込む。

```js
require('dotenv').config()

const port = Number(process.env.PORT || 3000)
console.log(`listening on ${port}`)
```

ES Modulesでは、設定用エントリーポイントを先に読み込める。

```js
import 'dotenv/config'

console.log(process.env.API_KEY)
```

値は文字列として読み込まれるため、ポート番号や真偽値はアプリ側で変換・検証
する。必須値がない場合に起動時エラーにするなど、設定の妥当性確認も別途行う。

### `.env`の主な書式

Node.js公式仕様では、変数名は英字・数字・アンダースコアで構成し、数字から
始めない。値は引用符で囲め、引用符付きの値は複数行にできる。`#`以降はコメント
だが、引用符内の`#`は値に含まれる。`export`接頭辞は無視される。

```dotenv
# コメント
HOST=localhost
MESSAGE="hello # dotenv"
PRIVATE_KEY="line one
line two"
```

アプリケーション、利用するライブラリ、デプロイ基盤の`.env`解釈が完全に同じ
とは限らないため、特殊な書式は実行環境で確認する。

### オプションとAPI

標準の`config()`は次の指定に対応する。

- `path`: `.env`以外のファイルを指定する。複数ファイルを配列で渡せる。
- `override`: 既存の環境変数を`.env`の値で上書きする。既定値は`false`。
- `debug`: 値が設定されない理由を調べるログを有効にする。
- `quiet`: 読み込み時のログを抑制する。
- `processEnv`: `process.env`ではなく、指定したオブジェクトへ値を書き込む。

`dotenv.parse()`は文字列または`Buffer`をオブジェクトへ変換し、
`dotenv.populate()`は任意のオブジェクトへ値を投入する。通常のアプリでは
`config()`だけで足りるが、設定のテストや独自ローダーを作る場合に利用できる。

### Node.js本体の機能との比較

Node.jsには`.env`を読む機能があり、CLIでは次のように起動できる。

```bash
node --env-file=.env app.js
```

プログラムからは`process.loadEnvFile('./.env')`を使える。Node.js公式は
`.env`の一般的な仕様を定義しているが、`.env`には言語横断の正式な標準仕様が
ないと説明している。

Node.js本体を対象にでき、起動コマンドを管理できるなら標準機能が簡潔である。
既存の`dotenv`利用、Node.js以外のツールとの慣習、`config()`のオプションやAPIが
必要なら`dotenv`を継続する、という基準で選ぶとよい。これは調査結果に基づく
使い分けの判断であり、プロジェクト固有の要件で再確認する。

### セキュリティと運用上の注意

- `.env`を`.gitignore`へ追加し、実際の秘密情報をリポジトリへ保存しない。
- `.env.example`には値そのものではなく、必要なキー名と説明だけを置く。
- フロントエンドへ埋め込まれる環境変数は利用者から見えるため、秘密情報を入れない。
- 本番では、クラウドのシークレット管理やデプロイ環境の環境変数を優先する。
- `process.env`の値は文字列なので、型、範囲、必須性を起動時に検証する。
- `override: true`は、実行環境が意図せず`.env`で上書きされる危険があるため、
  明示的な理由がある場合だけ使う。

## 参考資料

- [dotenv README（公式）](https://github.com/motdotla/dotenv/blob/master/README.md)
  - 参照日: 2026-09-10
- [dotenv package.json（公式リポジトリ）](https://raw.githubusercontent.com/motdotla/dotenv/master/package.json)
  - 参照日: 2026-09-10
- [Environment Variables | Node.js v26 Documentation](https://nodejs.org/api/environment_variables.html)
  - 参照日: 2026-09-10
- [dotenv - npm](https://www.npmjs.com/package/dotenv)
  - 参照日: 2026-09-10

## 更新履歴

- 2026-09-10: dotenvの役割、導入、書式、Node.js標準機能との使い分け、運用上の注意を整理
