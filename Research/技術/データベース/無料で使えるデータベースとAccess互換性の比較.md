---
作成日: 2026-10-08
更新日: 2026-10-08
タグ:
  - データベース
  - Access
  - ODBC
  - Windows
状態: 完了
---

# 無料で使えるデータベースとAccess互換性の比較

## 概要

SQLite以外の無料で使えるデータベースを、Windowsでの導入・運用のしやすさと、Microsoft Accessとの互換性という2つの軸で比較する。ここでいうAccess互換性は、Accessを画面・帳票のフロントエンドとして残せるか、既存のAccessデータを移行しやすいかを指す。

## 結論

Accessのフォーム、レポート、マクロ、VBAを、別のデータベース形式へ一括して「そのまま」変換する現実的な方法はない。これらはAccessのフォーム・レポート・コントロール・イベントに結び付いたAccess固有のアプリケーション層であり、SQL ServerやPostgreSQLなどのデータベースオブジェクトにはならない。

最も手戻りが少ないのは、**テーブルとデータだけをSQL Serverへ移し、Accessをフロントエンドとして残す構成**である。MicrosoftのSSMA for Accessで移行とリンクを進められ、既存のAccessフォーム、レポート、クエリ、マクロ、VBAをAccess上で使い続けられる。ただし、フォームやマクロがSQL Serverへ移ったわけではなく、Accessを廃止するには別途作り直しが必要である。

目的別には次のように選ぶとよい。

| 目的 | 推奨構成 | そのまま残るもの | 作り直しが必要なもの |
| --- | --- | --- | --- |
| 画面・帳票・マクロをほぼそのまま使い、データだけ別DBに置く | SQL Server ExpressまたはAzure SQL + Access | Accessのフォーム、レポート、マクロ、VBA | SQLや型、接続、性能の調整 |
| Access自体を廃止してクラウド化する | Dataverse + Power Apps / Power Automate | テーブル移行の一部、業務知識 | フォーム、レポート、マクロ、VBA |
| Accessに近いWindowsアプリへ置き換える | VB.NET Windows Forms + SQL Server Express | 画面項目、イベント処理の設計、業務ルール | UI、`DoCmd`、Access VBA、帳票処理 |
| 単に別のAccessファイルへ複製する | Accessのインポート・エクスポート | フォーム、レポート、マクロ、モジュール | 原則なし。ただし参照設定やリンク先は確認 |
| Accessをフロントエンドとして残し、別の無料DBへ接続する | Firebird、PostgreSQL、MariaDB + ODBC | Accessの画面と一部のロジック | 型、SQL、更新クエリ、接続設定の調整 |

したがって、「Accessを起動し続けてもよいか」が最初の分岐になる。起動してよいならSQL Server Expressへのバックエンド移行が第一候補で、起動したくないならPower AppsまたはVB.NETなどへの再実装を前提にする。

Accessを継続利用する前提なら、第一候補は **SQL Server Express** である。Microsoft公式のAccess向け移行ツール（SSMA）と、AccessアプリケーションをSQL Serverへリンクする手順が用意されているため、今回の候補ではAccessとの接続・移行経路が最も明確である。ただし、SQL Server Expressはサーバー型で、導入や管理はSQLiteより重い。

軽量さと無料のオープンソース性を重視し、AccessからODBC経由で接続できればよい場合は **Firebird** が有力である。Windows用のODBCドライバーが公式に提供され、比較的小規模な構成から始めやすい。一方、Accessのフォーム・レポート・VBAがそのまま別DBへ移るわけではない。

用途別には次のように選ぶとよい。

- Accessのフォーム・帳票・VBAをできるだけ残したい: **SQL Server Express**
- Accessを画面として残しつつ、軽量なサーバーDBへ移したい: **Firebird**
- Webアプリや複数システムのバックエンドにしたい: **PostgreSQL**
- MySQL系の知識・ツールを使いたい: **MariaDB**
- 1人でCSV・Parquetなどを集計したい: **DuckDB**

どの候補もAccessそのものの代替GUIではない。Accessのフォーム、レポート、マクロ、VBAを使い続けるなら、別途Accessのライセンスと、データ型・SQL・更新クエリの動作確認が必要である。

Accessのフロントエンドまで完全に廃止するなら、第一候補は **VB.NETのWindows Forms + SQL Server Express** である。個人利用など条件を満たす場合は、Visual Studio Community、.NET、Windows Forms、SQL Server Expressを無償でそろえられ、Visual Basicのイベント駆動UIはAccessからの考え方を移しやすい。SSMAでデータベース側の移行を進められる点も、移行完了までの速さに有利である。組織で使う場合はVisual Studio Communityのライセンス条件を確認する。

ただし、AccessのVBAやマクロをそのまま実行できるわけではない。Accessのフォーム・レポート・コントロールに結び付いたVBAとマクロは、VB.NETのイベント処理や業務ロジックへ書き換える必要がある。生かせるのは主に、データ項目、処理手順、入力規則、業務知識である。

## 詳細

### 評価方法

#### 使いやすさ

Windowsでインストールし、テーブルを作成し、日常的にバックアップ・接続設定を行うまでの負担を評価した。Accessの後継として使うことを想定し、単にインストールが簡単なだけでなく、一般的な業務データの登録・更新や複数ユーザー利用に向くかも含めた。

#### Access互換性

次の要素をまとめて評価した。

1. AccessからODBC経由で接続できる公式ドライバーがあるか。
2. Accessのリンクテーブルを使う構成を取りやすいか。
3. Accessのテーブルやデータを移行する公式または標準的な手段があるか。
4. Access特有のフォーム、レポート、VBA、クエリがそのまま使えるか。

4はどの候補でも限定的である。したがって、Access互換性の点数が高くても「Accessファイルをそのまま開ける」という意味ではない。

### フォーム・マクロを残す場合の現実的な構成

Accessのフォームやマクロを残す場合は、Accessをアプリケーション、別DBをデータストアとして分離する。SQL Serverへの移行では、SSMAがAccessのテーブルをSQL Serverへ移し、既存のAccessテーブルをSQL Server側のテーブルへリンクできる。Microsoftの説明でも、リンク後は既存Accessアプリケーションのクエリ、フォーム、レポートがSQL ServerまたはAzure SQLのデータを使う構成になっている。

この構成で残るのはAccess側のオブジェクトであり、フォームやマクロをSQL Serverの形式へ変換するわけではない。特に、次の点は移行後に確認する。

- Access固有のSQL関数、予約語、日付・真偽値・長いテキストなどの型
- `DoCmd`、`CurrentDb`、フォーム上のコントロール参照、イベントプロシージャ
- 更新クエリ、主キーの自動採番、NULL値、既定値
- リンクテーブル経由の性能。大量データをフォームで読み込む場合は、抽出条件やパススルークエリを見直す
- 接続認証。SQL Serverのリンクテーブルにパスワードを保存する方式は避け、Windows認証などを検討する

### Accessを廃止する場合

Accessを起動しない構成にする場合、候補DBを選ぶだけでは移行は完了しない。フォームはPower AppsやWindows Formsなどで再作成し、マクロとVBAはPower Automate、Power Fx、VB.NET、C#などへ業務単位で移す。移行できるのは主にテーブル、データ、業務ルール、入力項目、処理手順であり、Accessオブジェクトのファイル形式やイベント処理をそのまま再利用できるとは考えない方がよい。

DataverseはAccessデータを移行した後もAccessデスクトップクライアントを使えるほか、Power Platformからデータを扱える。ただし、Dataverseはデータソースであり、画面はPower Apps、処理はPower Automateなどで構成するため、AccessのフォームやVBAをそのまま持ち込む選択肢ではない。また、AccessとDataverseで対応するデータ型や上限が異なるため、移行前の確認が必要である。

### 別のAccessファイルへ移すだけの場合

移行先がSQL ServerなどのDBではなく、別の`.accdb`または`.mdb`ファイルでよいなら、Accessのインポート・エクスポートでフォーム、レポート、マクロ、モジュールを複製できる。この場合は「別DB形式への変換」ではなく「Accessオブジェクトの別ファイルへのコピー」であり、参照設定、リンクテーブル、外部ファイルのパスは別途確認する。

### 使いやすさランキング

| 順位 | DB | 目安点 | 評価 |
| ---: | --- | ---: | --- |
| 1 | SQL Server Express | 4.0/5 | WindowsとAccessの組み合わせに公式ツールがあり、導入後の運用情報も多い。ただしサーバー、認証、管理ツールの理解が必要。 |
| 2 | Firebird | 4.0/5 | 無料で軽量な構成を作りやすく、ODBC接続も可能。管理GUIの選択肢や日本語情報はSQL Serverより少ない。 |
| 3 | MariaDB | 3.5/5 | Windows向けインストーラーとODBCドライバーがあり、MySQL系の知識を流用しやすい。サーバー設定とDSN設定は必要。 |
| 4 | PostgreSQL | 3.5/5 | Windowsインストーラーにサーバー、pgAdmin、追加ツールが含まれ、管理機能も豊富。認証、ロール、スキーマなどの概念は初心者にはやや多い。 |
| 5 | DuckDB | 3.0/5 | サーバー不要の組み込み型で、単独の分析用途なら最も簡単。ただし一般的な業務DBや複数ユーザー向けAccessバックエンドとしては用途が異なる。 |

DuckDBは「CSVやParquetを1人で分析する」という条件なら、上表より高く評価できる。逆に、複数人が同じデータを登録・更新する業務DBを想定すると、サーバー型DBの方が適している。

### Access互換ランキング

| 順位 | DB | 目安点 | Accessとの接続・移行方法 | 主な注意点 |
| ---: | --- | ---: | --- | --- |
| 1 | SQL Server Express | 5.0/5 | MicrosoftのSSMA for AccessでAccessからSQL Serverへ移行でき、既存AccessアプリケーションをSQL Serverへリンクする公式手順がある。 | ExpressにはSQL Server 2025で1ソケットまたは4コア、バッファープール1,410 MB、リレーショナルDB 1データベースあたり50 GBの制限がある。 |
| 2 | Firebird | 4.0/5 | Firebird ODBC Driverをインストールし、AccessからODBCのリンクテーブルとして接続する。 | Access専用の移行ウィザードではないため、型、主キー、日付、更新クエリを手動検証する必要がある。 |
| 3 | MariaDB | 3.5/5 | MariaDB Connector/ODBCでDSNを作り、AccessからODBCデータベースとしてリンクする。 | MySQL系SQLとの互換性は利点だが、Access SQL、予約語、日付・真偽値の扱いは確認が必要。 |
| 4 | PostgreSQL | 3.5/5 | 公式のpsqlODBCを使い、Accessからリンクテーブルやパススルークエリで接続する。 | PostgreSQLの型、スキーマ、識別子の大文字小文字、トランザクションの違いで調整が必要。 |
| 5 | DuckDB | 1.5/5 | Windows用ODBCドライバーはあるため、接続自体は検討できる。 | DuckDBは組み込み型の分析DBであり、Accessデータベースを移行する公式経路や、一般的な業務DB向けのAccess連携を確認できない。 |

### 候補ごとの特徴

#### SQL Server Express

Microsoft SQL Serverの無償エディションである。SQL Server 2025の公式資料では、Expressの上限として、データベースエンジンの計算容量は1ソケットまたは4コアの小さい方、バッファープールは1,410 MB、リレーショナルデータベースの最大サイズは50 GBとされている。

Accessとの関係では、MicrosoftがSSMA for Accessを提供している点が大きい。SSMAはAccessを読み取り、SQL Server向けにデータベースオブジェクトを変換し、データを移行する。移行後に既存AccessアプリケーションからSQL Serverへリンクする手順も公式ドキュメントにある。

ただし、SSMAがフォーム、レポート、VBAを完全に別環境へ変換するわけではない。Accessをフロントエンドとして残す場合は、テーブルをSQL Serverへ移し、Access側のリンクテーブルを張り直す構成が現実的である。

#### Firebird

Firebirdはオープンソースのリレーショナルデータベースで、Firebird ProjectはIDPL（Initial Developer's Public License）でモジュールを公開している。Firebird 5.0では、性能、マルチスレッド処理、SQL言語などが強化されている。

公式のFirebird ODBC DriverはFirebird 3.0以降に対応し、Windows x64向けのインストーラーが提供されている。Accessからは、ODBCドライバーでDSNを作成し、外部データのODBC接続として利用する構成になる。

Accessに近い感覚で単一の業務DBから始めたい場合の候補だが、Accessの`.accdb`や`.mdb`をそのままFirebirdとして開くものではない。移行時は、テーブル、主キー、インデックス、リレーション、クエリを順番に確認する。

#### MariaDB

MariaDB Community ServerはGPLv2の無料オープンソースRDBMSで、Windows、macOS、Linuxに対応している。MySQL系の知識やツールを活用しやすいことが特徴である。

公式のMariaDB Connector/ODBCはODBC 3.5に準拠し、MariaDBとMySQLへ接続できる。Windowsではドライバーをインストールし、ODBC Data Source AdministratorでDSNを設定してから、AccessなどのODBC対応アプリケーションで利用する。

Accessのフロントエンドを残したまま、Webアプリや他のプログラムとも同じDBを共有したい場合に向く。SQL ServerほどAccess専用の移行支援はないため、既存Accessのクエリをそのまま動かせるとは考えない方がよい。

#### PostgreSQL

PostgreSQLは、PostgreSQL Licenseで公開されている無料のオープンソースRDBMSである。Windows向けの公式ダウンロード案内では、EDBのインストーラーにPostgreSQLサーバー、pgAdmin、追加ツール用のStackBuilderが含まれる。

公式のpsqlODBCはPostgreSQL用のODBCドライバーで、Access向けの接続やVBA利用に関する資料も用意されている。Accessから接続できるが、PostgreSQLのスキーマ、ロール、型、識別子の規則を理解して設計する必要がある。

長期運用、複雑な検索、他のアプリケーションからの利用を重視するなら有力である。一方、Accessの小規模ファイルを軽く置き換えたいだけなら、管理機能が多く感じられる可能性がある。

#### DuckDB

DuckDBはMIT Licenseで公開されている、組み込み型の分析向けリレーショナルDBである。サーバーを別プロセスとしてインストールせず、アプリケーション内で動作する。CSV、Parquetなどのファイルを読み込んで集計する用途に強い。

公式にWindows用ODBCドライバーが提供されているため、ODBC接続の候補にはなる。ただし、DuckDB自身が主な対象としているのはOLAP（分析処理）であり、Accessのフォームから複数人が頻繁に登録・更新するOLTP（業務トランザクション処理）の置き換えとは目的が異なる。

### 迷ったときの選び方

| 条件 | 第一候補 | 理由 |
| --- | --- | --- |
| Accessの画面・帳票・VBAを残し、データだけサーバー化したい | SQL Server Express | Microsoft公式の移行・リンク手順がある。 |
| 小規模な業務DBで、無料・軽量・ODBCを優先したい | Firebird | Windows用ODBCドライバーがあり、SQL Serverより構成を小さくしやすい。 |
| 将来Webアプリや複数の業務システムから使いたい | PostgreSQL | 高機能で、Access以外のクライアントにも広く対応できる。 |
| MySQL系の既存知識や周辺ツールを使いたい | MariaDB | MySQL互換性と公式ODBCドライバーがある。 |
| 個人の集計・データ分析が中心 | DuckDB | サーバー不要で、ファイル分析を始めやすい。 |

最初の試行では、Accessのコピーを使って「テーブル移行」「リンクテーブル経由のSELECT」「INSERT・UPDATE・DELETE」「主キー・日付・NULL」「フォーム保存」の順に確認すると、互換性の問題を早く見つけられる。元のAccessファイルを直接変換せず、必ずバックアップまたは複製から試す。

### Accessフロントエンドを完全に廃止する場合

「早い」は、移行作業を早く終えられることと、完成後の画面・DBが速く動くことに分けて考える。次の評価は、実機ベンチマークではなく、公式の移行支援、UI開発環境、DBドライバー、構成の軽さを比較した目安である。

| 順位 | 無料構成 | 移行の速さ | 完成後の速さ | 型の再利用 | マクロの再利用 | 向いているケース |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | VB.NET Windows Forms + SQL Server Express | 4.5/5 | 4.0/5 | 4.0/5 | 2.0/5 | Accessの業務画面をWindowsデスクトップアプリへ早く置き換えたい。 |
| 2 | VB.NET Windows Forms + Firebird | 3.5/5 | 4.5/5 | 3.5/5 | 2.0/5 | 軽量な構成と複数ユーザー対応を両立したい。 |
| 3 | LibreOffice Base + Firebird + Access2Base | 3.5/5 | 3.0/5 | 3.5/5 | 3.0/5 | Accessに近いフォーム・マクロの考え方を残したい。 |
| 4 | VB.NETまたはC# + PostgreSQL | 3.0/5 | 4.5/5 | 3.0/5 | 1.5/5 | 将来Webや他システムからも使う前提で作り直したい。 |

#### 第一候補: VB.NET Windows Forms + SQL Server Express

Accessの画面を、Visual StudioのフォームデザイナーでWindows Formsへ作り直す構成である。VB.NETはVBAと文法やイベント処理の考え方が比較的近いため、既存の処理を読み替える作業がC#より始めやすい。ただし、`DoCmd`、`Forms!フォーム名!コントロール名`、`CurrentDb`、Access固有のイベントなどは、そのまま移植できない。

SQL Server Expressは、既存Accessのテーブル・データ移行にSSMAを利用できる。データ型は自動変換後も、オートナンバー、Yes/No、日付時刻、長いテキスト、添付ファイル、主キー、インデックスを確認する。マクロは、ボタンのクリックイベント、入力チェック、検索条件の組み立て、帳票出力などの単位でVB.NETへ移す。

#### 軽量さ優先: VB.NET Windows Forms + Firebird

Firebirdには公式の.NET Data Providerがあり、VB.NETやC#からADO.NETで接続できる。SQL Server Expressより小さな構成にしやすく、複数ユーザーで共有するデスクトップ業務アプリの候補になる。

一方、Access向けの公式移行支援はSQL Serverほど揃っていない。Accessのテーブル定義をFirebirdへ移す作業と、型・SQL・トランザクションの確認が増えるため、Accessの規模が大きい場合はSQL Server Expressより移行作業が長くなる可能性がある。

#### マクロの書き換えを減らしたい: LibreOffice Base + Firebird

LibreOfficeには、Accessのフォーム、コントロール、テーブル、クエリ、レコードセットなどに似たAPIを提供するAccess2Baseがある。Accessのマクロアクションに似た構文もあるため、候補の中ではAccessの考え方を残しやすい。

ただし、AccessのフォームやVBAが完全移行されるわけではない。LibreOffice公式ヘルプもVBAサポートは完全ではなく、コードの編集が必要になる場合があると説明している。Access2Baseを使う場合も、フォーム、帳票、イベント、参照設定を実機で作り直して確認する必要がある。

#### 長期運用優先: VB.NETまたはC# + PostgreSQL

PostgreSQLは無料のサーバーDBとして有力で、Npgsqlを使えばVB.NETやC#から無償・オープンソースの.NET接続ができる。将来Web API、バッチ、他OSクライアントなどを追加するなら設計の自由度が高い。

ただし、Accessのマクロやフォームを生かす観点では最も作り直しが多い。Accessからの移行速度よりも、DBの機能、拡張性、複数のアプリケーションからの利用を重視する場合に選ぶ。

### 推奨する移行順序

1. Accessのテーブル、リレーション、入力規則、クエリ、フォーム、レポート、マクロ、VBAを一覧化する。
2. SQL Server ExpressまたはFirebirdへ、テーブルとデータだけを複製する。
3. Accessの型を対象DBの型へ対応付け、NULL、既定値、主キー、日付時刻を検証する。
4. 頻繁に使う画面を1つ選び、VB.NET Windows Formsで入力・検索・保存まで作る。
5. AccessのマクロとVBAを、画面イベント、検証、DB処理、帳票出力へ分割して書き換える。
6. Accessを起動しない状態で、件数、計算結果、エラー処理、同時更新、バックアップを比較する。

この順序なら、データ移行と画面移行を分離できる。最初から全フォームと全マクロを一括変換しようとするより、完成までのリスクを抑えやすい。

## 参考資料

- [SQL Server 2025 Expressのダウンロードと制限](https://www.microsoft.com/en-us/download/details.aspx?id=108836)
  - 参照日: 2026-10-08
  - SQL Server Expressが無償エディションであり、公式の制限概要を確認した。
- [SQL Server 2025のエディションとサポート機能](https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2025?view=sql-server-ver17)
  - 参照日: 2026-10-08
  - Expressの計算容量、メモリ、データベースサイズの公式制限を確認した。
- [SQL Server Migration Assistant for Access](https://learn.microsoft.com/en-us/sql/ssma/access/sql-server-migration-assistant-for-access-accesstosql?view=sql-server-ver17)
  - 参照日: 2026-10-08
  - AccessからSQL Serverへの移行、オブジェクト変換、データ移行、既存Accessアプリケーションのリンク手順を確認した。
- [Migrate Access Databases to SQL Server and Azure SQL Database](https://learn.microsoft.com/en-us/sql/ssma/access/migrating-access-databases-to-sql-server-azure-sql-db-accesstosql?view=sql-server-ver17)
  - 参照日: 2026-10-08
  - SSMAの推奨手順が、評価、変換、スキーマ・データ移行、Accessテーブルのリンクで構成されることを確認した。
- [Link Access Applications to SQL Server and Azure SQL](https://learn.microsoft.com/en-us/sql/ssma/access/linking-access-applications-to-sql-server-azure-sql-db-accesstosql?view=sql-server-ver17)
  - 参照日: 2026-10-08
  - リンク後も既存Accessのクエリ、フォーム、レポートを使えることと、性能・認証などの注意点を確認した。
- [Migrate Microsoft Access data to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/migrate-access-to-dataverse)
  - 参照日: 2026-10-08
  - DataverseがAccessデータの移行先・データソースであり、Power Platformから利用できること、データ型や上限に差があることを確認した。
- [Export a database object to another Access database](https://support.microsoft.com/en-us/access/export-a-database-object-to-another-access-database)
  - 参照日: 2026-10-08
  - 別のAccessデータベースへオブジェクトをコピー・エクスポートできることを確認した。
- [Firebird 5.0](https://firebirdsql.org/en/firebird-5-0/)
  - 参照日: 2026-10-08
  - Firebird 5.0の主な強化点と公式ドキュメントへの導線を確認した。
- [Firebirdのライセンス](https://www.firebirdsql.org/en/licensing/)
  - 参照日: 2026-10-08
  - FirebirdのIDPLを確認した。
- [Firebird ODBC Driver](https://www.firebirdsql.org/en/odbc-driver/)
  - 参照日: 2026-10-08
  - Firebird 3.0以降向けの公式ODBCドライバー、Windows対応、DSN設定の前提を確認した。
- [MariaDB Community Server](https://mariadb.com/products/community-server/)
  - 参照日: 2026-10-08
  - MariaDB Community Serverの無料性、GPLv2、対応OS、MySQL互換性を確認した。
- [MariaDB Connector/ODBC Guide](https://mariadb.com/docs/connectors/connectors-quickstart-guides/connector-odbc-guide)
  - 参照日: 2026-10-08
  - ODBC 3.5準拠、WindowsでのドライバーとDSNの設定方法を確認した。
- [PostgreSQL License](https://www.postgresql.org/about/licence/)
  - 参照日: 2026-10-08
  - PostgreSQL Licenseによる無料・オープンソース提供を確認した。
- [PostgreSQL Windows installers](https://www.postgresql.org/download/windows/)
  - 参照日: 2026-10-08
  - Windowsインストーラーにサーバー、pgAdmin、StackBuilderが含まれることを確認した。
- [psqlODBC - PostgreSQL ODBC driver](https://odbc.postgresql.org/)
  - 参照日: 2026-10-08
  - PostgreSQL公式ODBCドライバーと、Access向け資料の存在を確認した。
- [Why DuckDB](https://duckdb.org/why_duckdb)
  - 参照日: 2026-10-08
  - DuckDBの組み込み型、分析向け、MIT Licenseという特徴を確認した。
- [DuckDB ODBC API on Windows](https://duckdb.org/docs/current/clients/odbc/windows)
  - 参照日: 2026-10-08
  - Windows用ODBCドライバーの提供を確認した。
- [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/)
  - 参照日: 2026-10-08
  - Visual Studio Communityが無償のIDEとして提供され、個人利用と組織利用で条件が異なることを確認した。
- [.NETの無償ツール](https://dotnet.microsoft.com/en-us/platform/free)
  - 参照日: 2026-10-08
  - Visual Studio Code、Visual Studio Community、.NETアプリ開発ツールの無償提供を確認した。
- [Windows Forms for .NET](https://learn.microsoft.com/en-us/dotnet/desktop/winforms/)
  - 参照日: 2026-10-08
  - Windows Formsが.NETのオープンソースGUIであることを確認した。
- [Visual BasicでWindows Formsアプリを作成するチュートリアル](https://learn.microsoft.com/en-us/visualstudio/ide/create-a-visual-basic-winform-in-visual-studio?view=visualstudio)
  - 参照日: 2026-10-08
  - Visual BasicのWindows Formsプロジェクト作成とイベント処理の公式手順を確認した。
- [Firebird ADO.NET Data Provider](https://www.firebirdsql.org/en/net-provider/)
  - 参照日: 2026-10-08
  - Firebirdの高性能な.NETデータプロバイダーがC#で実装されていることを確認した。
- [Npgsql - .NET Access to PostgreSQL](https://www.npgsql.org/)
  - 参照日: 2026-10-08
  - VB.NETやC#からPostgreSQLへ接続できる無料・オープンソースのADO.NETプロバイダーを確認した。
- [Access object model for VBA](https://learn.microsoft.com/en-us/office/vba/api/overview/access/object-model)
  - 参照日: 2026-10-08
  - Access VBAがフォーム、レポート、イベントなどAccess固有のオブジェクトモデルに依存することを確認した。
- [Introduction to macros in Access](https://support.microsoft.com/en-us/access/introduction-to-macros)
  - 参照日: 2026-10-08
  - Accessマクロがフォーム、レポート、コントロールのイベントに関連付く仕組みを確認した。
- [Access2Base](https://help.libreoffice.org/latest/en-US/text/sbasic/guide/access2base.html)
  - 参照日: 2026-10-08
  - LibreOfficeがAccessに似たフォーム、DBアクセス、マクロアクション用のAccess2Base APIを提供することを確認した。
- [Working with VBA Macros in LibreOffice](https://help.libreoffice.org/latest/en-US/text/sbasic/shared/vbasupport.html)
  - 参照日: 2026-10-08
  - LibreOfficeのVBAサポートは完全ではなく、コード編集が必要になる場合があることを確認した。

## 更新履歴

- 2026-10-08: Accessフロントエンドを廃止する場合のVB.NET、Firebird、LibreOffice Base、PostgreSQL構成と移行順序を追記
- 2026-10-08: フォーム・マクロ・VBAをそのまま移せるかを明確化し、Accessを残す構成、Access廃止、別Accessファイルへの複製を整理
- 2026-10-08: yomiyasuの原則に基づき本文を推敲
- 2026-10-08: SQLite以外の無料DBを、使いやすさとAccess互換性の2軸で比較する初版を作成
