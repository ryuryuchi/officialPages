---
作成日: 2026-08-26
更新日: 2026-08-31
タグ:
  - Excel
  - VBA
  - VS Code
  - xlwings
状態: 完了
---

# VS CodeでExcel VBAを編集してブックへ反映する方法

## 概要

Microsoft ExcelのVBAをVS Codeで編集し、マクロ有効ブックへ反映する方法を整理する。VS Codeをテキストエディター兼Git管理環境として使いながら、Excel側のVBAプロジェクトと同期することを目的とする。

## 結論

Windows版Excelでは、`xlwings vba edit`を使う方法が扱いやすい。初回にブック内のVBAコンポーネントを`.bas`、`.cls`、`.frm`へ書き出し、その後はVS Codeでファイルを保存するたびに開いているブックへ反映できる。

ただし、VS CodeだけでVBA開発のすべてを置き換えることはできない。UserFormの画面設計、参照設定、VBAプロジェクトのコンパイル、ブレークポイントを使ったデバッグなどは、従来どおりExcelのVisual Basic Editor（VBE）で行う。

Pythonを導入したくない場合は、VBEからモジュールを手動でエクスポートし、VS Codeで編集してから再インポートする。継続的に編集するなら`xlwings`、一度だけの修正や厳しく管理されたPCでは手動方式が適している。

## 詳細

### 前提

- デスクトップ版Excelを使用する。Excel for the webではVBAを作成、実行、編集できない。
- ブックをVBAを保存できる`.xlsm`、`.xlsb`、`.xlam`などの形式にする。通常の`.xlsx`にはVBAコードを保存できない。
- 作業前にブックのバックアップを作る。
- VS CodeでVBA用のシンタックスハイライト拡張機能を追加すると読みやすくなるが、拡張機能だけではブックとの同期は行われない。

### 推奨方法: xlwingsで自動同期する

#### 1. Pythonとxlwingsを用意する

現行のxlwingsはPython 3.9以上を前提としている。PowerShellで次を実行する。`vba edit`のファイル監視には`watchgod`も必要である。

```powershell
py -m pip install --upgrade xlwings watchgod
```

xlwingsのExcelアドインは、VBAファイルの同期だけを行う場合には不要である。
2026年8月31日の再確認時点で、公式changelogの最新掲載はxlwings 0.36.17
（2026年8月17日）である。公式CLI説明と現行ソースは引き続き`xlwings vba edit`、
`export`、`import`および`watchgod`を使用しており、この手順に廃止予告はない。

#### 2. Excelの設定を変更する

Excelで次の順に開く。

1. `ファイル` > `オプション`
2. `トラスト センター` > `トラスト センターの設定`
3. `マクロの設定`
4. `VBA プロジェクト オブジェクト モデルへのアクセスを信頼する`を有効にする

これは外部プログラムからVBAプロジェクトを書き換えるために必要な設定である。Microsoftによると、ユーザー単位かつOfficeアプリ単位の設定で、既定では拒否される。

`すべてのマクロを有効にする`まで選ぶ必要はない。この設定はMicrosoftも非推奨としている。同期を常用しない場合は、作業後にVBAプロジェクトへのアクセス許可を戻す。

#### 3. ブックと作業フォルダーを用意する

1. 対象ブックをExcelで開く。
2. ブックごとに専用の作業フォルダーを作る。
3. VS Codeでそのフォルダーを開く。
4. VS Codeのターミナルで、そのフォルダーへ移動する。

同じフォルダーへ無関係な`.bas`、`.cls`、`.frm`を置かない。`xlwings vba import`はカレントフォルダーの対象ファイルをブックへ取り込むため、ブックごとに分ける方が安全である。

#### 4. 編集監視を開始する

対象ブックがアクティブなら、作業フォルダーで次を実行する。

```powershell
xlwings vba edit
```

ブックを明示する場合は、次のように指定する。

```powershell
xlwings vba edit --file "C:\Work\Book1.xlsm"
```

確認画面に対象ブックと作業フォルダーが表示されるので、誤りがないことを確認して続行する。

初回実行時は、ブック内のコンポーネントが作業フォルダーへ書き出される。

| VBAコンポーネント | 主な拡張子 |
| --- | --- |
| 標準モジュール | `.bas` |
| クラスモジュール | `.cls` |
| `ThisWorkbook`、ワークシート | `.cls` |
| UserForm | `.frm`と付随する`.frx` |

書き出されたファイルをVS Codeで編集して保存すると、監視中の`xlwings`がブック内のコードを更新し、ブックを保存する。監視を終了するにはターミナルで`Ctrl+C`を押す。

#### 5. Excel側で行った変更を取り直す

UserFormのレイアウト、モジュールのプロパティなどをVBEで変更した場合は、VS Code側へ自動反映されない。次を実行して、Excel側の内容でローカルファイルを上書きする。

```powershell
xlwings vba export --file "C:\Work\Book1.xlsm"
```

反対に、ローカルファイル一式でExcel側を明示的に更新する場合は次を使う。

```powershell
xlwings vba import --file "C:\Work\Book1.xlsm"
```

どちらも対象ブックとフォルダーを確認してから実行する。取り違えると新しい変更を上書きするため、実行前にGitへコミットするかバックアップを取る。

#### 6. 新規モジュールとUserFormを扱う

監視中にVS Codeで新しい`.bas`、`.cls`、`.frm`を作成しても、`vba edit`は新規コンポーネントとして追加しない。新しいモジュールやUserFormはVBEで作成してから、`xlwings vba export`で作業フォルダーへ書き出す。

UserFormの画面部品はVBEのデザイナーで編集する。`.frm`だけでなく、画像などを保持する`.frx`も対で管理する。

### 手動方式: VBEでエクスポートとインポートを行う

Pythonや自動同期ツールを使えない場合は、次の手順で編集できる。

1. Excelで`Alt+F11`を押してVBEを開く。
2. プロジェクトエクスプローラーで標準モジュール、クラス、UserFormを右クリックする。
3. `ファイルのエクスポート`を選び、専用フォルダーへ保存する。
4. VS Codeでファイルを編集して保存する。
5. VBEで古い標準モジュールまたはクラスを削除する。削除時に再エクスポートするか聞かれた場合、すでにバックアップ済みなら不要である。
6. プロジェクトを右クリックし、`ファイルのインポート`で編集済みファイルを読み込む。
7. VBEの`デバッグ` > `VBAProjectのコンパイル`を実行し、Excelで動作確認して保存する。

MicrosoftのVBA Add-In Object Modelでも、`Export`はコンポーネントを別ファイルへ保存し、`Import`はファイルからコンポーネントをプロジェクトへ追加する操作として定義されている。

`ThisWorkbook`や各ワークシートはブック固有のドキュメントモジュールである。単純にインポートすると通常のクラスとして追加され、既存のドキュメントモジュールを置き換えられない。この部分を手動で扱う場合は、VS Codeで編集したコード本文を既存の`ThisWorkbook`または対象シートのコード画面へ貼り戻す。自動同期が必要なら`xlwings vba edit`を使う方がよい。

### XVBA拡張機能という選択肢

VS Code Marketplaceの第三者製拡張機能`XVBA - Live Server VBA for Excel & Access`には、VBAのインポート、保存時の自動反映、補完、フォーマット、マクロ実行などがまとめられている。Pythonを別途操作せずVS Code内で完結させたい場合の候補になる。

一方で、Excelを外部から操作する拡張機能であり、セットアップ時にはマクロ実行やブック書き換えに関する設定が必要になる。業務PCでは組織の拡張機能ポリシーを確認し、ブックをバックアップしたうえで導入する。構成を単純にし、同期処理をコマンドとして確認しながら使いたい場合は`xlwings`の方が分かりやすい。

### VS CodeとVBEの役割分担

| 作業 | VS Code | ExcelのVBE |
| --- | --- | --- |
| コード編集、検索、一括置換 | 適する | 可能 |
| Gitで差分確認、履歴管理 | 適する | 不向き |
| UserFormの画面設計 | 不可 | 必要 |
| 参照設定 | 不可 | 必要 |
| コンパイル | 不可 | 必要 |
| ステップ実行、ブレークポイント | 原則不可 | 必要 |
| イミディエイトウィンドウ | 不可 | 必要 |

### Gitで管理する場合

- `.bas`、`.cls`、`.frm`はテキスト差分を確認できるのでGit管理に向く。
- `.frx`はバイナリだが、UserFormに必要なため`.frm`と一緒に管理する。
- ブック本体はバイナリで差分を読みづらい。コードレビューはエクスポートしたファイルを中心に行う。
- Excel側だけで変更した後は、コミット前に必ず`xlwings vba export`を実行する。
- 同じモジュールをVS CodeとVBEで同時に編集しない。どちらを正とするか決めてから同期する。

### 制約と注意点

- `xlwings vba edit`によるVBA同期は、現行実装ではWindows向けである。
- パスワードでロックされたVBAプロジェクトは、外部ツールから更新できないことがある。
- 会社のグループポリシーでトラストセンター設定が固定されている場合は、管理者へ確認する。
- コード保存直後にブックも更新されるため、構文エラーを含む途中状態が入ることがある。大きな変更はGitブランチやコピーしたブックで行う。
- VS Codeで保存できてもVBAとして正しいとは限らない。最後は必ずVBEでコンパイルし、Excel上でマクロを実行して確認する。

## 参考資料

- [Command Line Client (CLI) - xlwings Documentation](https://docs.xlwings.org/en/stable/command_line.html)
  - 参照日: 2026-08-31
- [Installation - xlwings Documentation](https://docs.xlwings.org/en/stable/installation.html)
  - 参照日: 2026-08-31
- [Changelog - xlwings Documentation](https://docs.xlwings.org/en/stable/whatsnew.html)
  - 参照日: 2026-08-31
- [xlwings CLI source code - GitHub](https://github.com/xlwings/xlwings/blob/main/xlwings/cli.py)
  - 参照日: 2026-08-31
- [Change macro security settings in Excel - Microsoft Support](https://support.microsoft.com/en-US/Excel/change-macro-security-settings-in-excel)
  - 参照日: 2026-08-31
- [File formats that are supported in Excel - Microsoft Support](https://support.microsoft.com/en-US/Excel/file-formats-that-are-supported-in-excel)
  - 参照日: 2026-08-31
- [Export method (VBA Add-In Object Model) - Microsoft Learn](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/export-method-vba-add-in-object-model)
  - 参照日: 2026-08-31
- [Import method (VBA Add-In Object Model) - Microsoft Learn](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/import-method-vba-add-in-object-model)
  - 参照日: 2026-08-31
- [XVBA - Live Server VBA for Excel & Access - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=local-smart.excel-live-server)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLと現行CLIソースを再確認し、xlwings 0.36.17時点の対応状況とchangelogを追記
- 2026-08-26: 初版を作成
