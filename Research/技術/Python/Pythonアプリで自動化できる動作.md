---
作成日: 2026-08-28
更新日: 2026-08-31
タグ:
  - Python
  - 自動化
  - API
  - 業務効率化
状態: 完了
---

# Pythonアプリで自動化できる動作

## 概要

Pythonで作成したアプリケーションを使って、日常作業や業務の定型処理のうち、入力・判断・出力の手順を明確にできるものをどこまで自動化できるかを整理した。

## 結論

Pythonでは、ファイル操作、データの読み書き・集計、Web APIとの通信、メール送受信、外部コマンドの実行、データベース処理、ブラウザー操作、定期実行、結果通知まで自動化できる。単純なバッチから、GUI付きの業務アプリや複数サービスをつなぐ処理まで発展させられる。

ただし、Pythonだけで全てが完結するわけではない。ブラウザー操作にはPlaywrightなどの外部ライブラリ、Excel固有の処理にはopenpyxlなど、OSの起動設定にはタスクスケジューラなどを組み合わせる。ログ、再実行、認証情報の保護、対象サービスの利用規約を設計に含める必要がある。

## 詳細

### 2026年8月時点の前提

本メモの標準ライブラリ参照先`docs.python.org/3`は、現行の安定版系列Python 3.14の文書へ解決される。Python 3.15はプレリリース段階であり、本番自動化では利用パッケージの対応を確認してから採用する。

主な外部パッケージのPyPI最新安定版は、Playwright 1.62.0（Python 3.10以上）、openpyxl 3.1.5（Python 3.8以上）、pandas 3.0.5（Python 3.11以上）である。要件は今後変わるため、導入時には固定値として扱わず各プロジェクトのメタデータを再確認する。

openpyxlのRead the Docsは`latest`でも3.1.4を表示し、PyPIの3.1.5より遅れている。
版確認にはPyPIも併用し、機能説明とセキュリティ上の注意には公式文書を使う。

### 自動化できる代表例

| 分野 | 自動化できる動作 | 主な手段 |
|---|---|---|
| ファイル・フォルダー | 拡張子別の収集、名前変更、移動、コピー、バックアップ、フォルダー監視 | `pathlib`、`shutil` |
| 文書・画像 | テキスト抽出、形式変換、画像のリサイズ・透かし、PDFの分割・結合 | 標準ライブラリ、目的別パッケージ |
| Excel・CSV | 複数ファイルの統合、値の整形、集計、帳票作成、セルへの書き込み | `csv`、`pandas`、`openpyxl` |
| データベース | データの登録・検索・更新、重複排除、集計結果の保存 | `sqlite3`、各DB用ドライバー |
| Web・API | HTTPリクエスト、データ取得・登録、JSON変換、定期的な情報収集 | `urllib`、HTTPクライアント、API SDK |
| ブラウザー | ログイン後の画面操作、フォーム入力、ダウンロード、スクリーンショット、E2Eテスト | Playwright、Selenium |
| メール・通知 | 定型メール送信、受信メールの取得・添付保存、処理結果の通知 | `smtplib`、`imaplib`、`email`、通知サービス |
| PC・他のアプリ | コマンド実行、別アプリへのデータ受け渡し、処理結果の取得 | `subprocess`、OS機能 |
| 定期処理 | 毎日・毎時の実行、複数処理の順番制御、並行実行 | タスクスケジューラ、cron、`sched`、`asyncio` |
| GUI・運用 | ボタンからの処理開始、入力フォーム、進捗表示、エラー表示 | `tkinter`、GUI外部ライブラリ、ログ |

### 具体的な業務フローの例

- 指定フォルダーに届いたCSVを読み込み、列名・日付・重複を検査してExcelの集計表を作る。
- Web APIから毎朝データを取得し、SQLiteに保存して前日との差分をメールで通知する。
- 複数の帳票ファイルを一括処理し、処理済みフォルダーへ移動して実行ログを残す。
- ブラウザーで社内システムへアクセスし、決められた項目を入力して結果をダウンロードする。
- 外部コマンドや別のPythonモジュールを順番に実行し、失敗時に後続処理を止めて通知する。
- GUIのボタンから処理を開始し、利用者が設定値を変更できる小規模な業務ツールにする。

### 自動化の構成パターン

1. **入力**: ファイル、フォーム、API、メールなどからデータを受け取る。
2. **検証**: 必須項目、形式、対象範囲、重複、権限を確認する。
3. **処理**: 整形、計算、検索、変換、外部サービスへの登録を行う。
4. **出力**: ファイル、データベース、メール、画面、APIレスポンスへ結果を出す。
5. **運用**: ログ、エラー通知、再実行、バックアップ、実行スケジュールを管理する。

定型的な処理は自動化しやすい一方、最終承認、例外的な判断、本人確認、規約で禁止されている大量アクセスなどは、人の確認を残す設計が安全である。

### 選び方と注意点

- **APIがあるサービス**: 画面操作よりAPIを優先する。認証方式、レート制限、利用規約、取得データの個人情報を確認する。
- **画面しかないサービス**: PlaywrightやSeleniumを使えるが、画面変更で壊れやすい。待機条件、失敗時のスクリーンショット、再実行方法を用意する。
- **ファイル処理**: 上書き前にバックアップまたは一時ファイルを使い、対象拡張子やフォルダーを限定する。
- **Excel入力の安全性**: 信頼できないOffice Open XMLファイルをopenpyxlで処理する場合、公式文書が案内する`defusedxml`の利用を検討する。
- **外部コマンド**: `subprocess`では引数を文字列連結せず、引数の配列として渡す。外部入力をコマンドとして実行しない。
- **認証情報**: パスワードやAPIキーをソースコード・ログに書かず、環境変数やOSの資格情報管理などを使う。
- **失敗への対応**: `logging`で開始・終了・対象件数・エラーを記録し、部分成功時の扱いと再実行時の重複登録を決める。
- **負荷と並行性**: ネットワーク待ちが多い処理は`asyncio`などを検討するが、相手サービスへの過剰な同時アクセスは避ける。
- **配布**: 利用者がPython環境を持たない場合は、実行ファイル化やインストーラーを検討する。ただし外部ブラウザーや設定ファイルの配布も必要になる。

## 参考資料

- [Python Standard Library](https://docs.python.org/3/library/index.html)
  - 参照日: 2026-08-31
- [subprocess — Subprocess management](https://docs.python.org/3/library/subprocess.html)
  - 参照日: 2026-08-31
- [pathlib — Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html)
  - 参照日: 2026-08-31
- [urllib.request — Extensible library for opening URLs](https://docs.python.org/3/library/urllib.request.html)
  - 参照日: 2026-08-31
- [email — An email and MIME handling package](https://docs.python.org/3/library/email.html)
  - 参照日: 2026-08-31
- [sqlite3 — DB-API 2.0 interface for SQLite databases](https://docs.python.org/3/library/sqlite3.html)
  - 参照日: 2026-08-31
- [asyncio — Asynchronous I/O](https://docs.python.org/3/library/asyncio.html)
  - 参照日: 2026-08-31
- [logging — Logging facility for Python](https://docs.python.org/3/library/logging.html)
  - 参照日: 2026-08-31
- [Playwright Python Library](https://playwright.dev/python/docs/library)
  - 参照日: 2026-08-31
- [Playwright - PyPI](https://pypi.org/project/playwright/)
  - 参照日: 2026-08-31
- [openpyxl documentation](https://openpyxl.readthedocs.io/en/latest/)
  - 参照日: 2026-08-31
- [openpyxl - PyPI](https://pypi.org/project/openpyxl/)
  - 参照日: 2026-08-31
- [pandas documentation](https://pandas.pydata.org/docs/)
  - 参照日: 2026-08-31
- [pandas - PyPI](https://pypi.org/project/pandas/)
  - 参照日: 2026-08-31
- [Python Developer's Guide: Status of Python versions](https://devguide.python.org/versions/)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、Python系列、主要外部パッケージの現行版・要件、openpyxlの安全上の注意を追記
- 2026-08-28: 初版を作成
