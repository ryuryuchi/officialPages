---
作成日: 2026-09-15
更新日: 2026-09-15
タグ:
  - Python
  - Microsoft
  - Office
  - ファイル形式
  - 自動化
状態: 完了
---

# Microsoft系ファイルを扱うPythonライブラリ

## 概要

Microsoft Officeで使われるファイル拡張子を、Pythonから読み取り・編集・変換する
ための代表的なライブラリを調べた。Word、Excel、PowerPointの現行形式だけでなく、
旧形式、Outlook、Visio、Access、Microsoft 365上のファイルも対象にした。

## 結論

Microsoft系の拡張子を扱うPythonライブラリは複数ある。ただし、拡張子を一括して
高水準に扱う単一の標準ライブラリはなく、形式と目的に応じて選ぶ。

| 対象 | 第一候補 | 主な用途と制約 |
| --- | --- | --- |
| `.docx` | `python-docx` | Word文書の文章、段落、表、画像などの読み書き。Wordアプリ不要 |
| `.xlsx`、`.xlsm` | `openpyxl` | セル、数式、書式、シートの読み書き。旧式`.xls`は対象外 |
| `.pptx` | `python-pptx` | スライド、テキスト、画像、表、図形、グラフの読み書き |
| `.xls` | `xlrd` | 古いExcel形式の読み取り。書き込みやマクロ、図形などは扱わない |
| `.xlsb` | `pyxlsb` | バイナリExcelの基本的な読み取り。機能は限定的 |
| 複数のExcel形式 | `python-calamine` | `.xls`、`.xlsx`、`.xlsm`、`.xlsb`などの読み取りを一つのAPIに寄せる候補 |
| Outlook `.msg` | `extract-msg` | メール本文、宛先、日時、添付ファイルの抽出 |
| Visio `.vsdx` | `vsdx` | ページ、図形、テキストの読み取り・一部編集 |
| Access `.mdb`、`.accdb` | `pyodbc` | Access ODBCドライバー経由のデータベース接続。別途ドライバーが必要 |
| Officeファイルの暗号化解除 | `msoffcrypto-tool` | パスワードで保護されたOfficeファイルを復号し、別ライブラリへ渡す |
| Windows版Officeの完全自動化 | `pywin32` | COM経由でWord、Excel、PowerPointなどを操作。WindowsとOfficeが必要 |
| OneDrive、SharePoint上のファイル | `msgraph-sdk`など | Microsoft Graph経由の取得・保存・共有。ローカル形式の解析器ではない |

したがって、**ローカルの`.docx`、`.xlsx`、`.pptx`を処理するなら、まず
`python-docx`、`openpyxl`、`python-pptx`を検討する**のが分かりやすい。Excelの
データ抽出だけなら、複数形式を読める`python-calamine`や、`pandas.read_excel()`
と各形式用のエンジンを組み合わせる方法もある。

## 詳細

### ファイル形式による違い

`.docx`、`.xlsx`、`.pptx`はOffice Open XML（OOXML）系で、ZIP内のXMLなどを扱う
形式である。一方、`.doc`、`.xls`、`.ppt`、古い`.vsd`や`.mpp`、Outlookの
`.msg`などにはOLE2/Compound File Binary Formatが使われるものがある。形式の内部
構造が異なるため、`openpyxl`を使って`.xls`を開く、といった使い方はできない。

`olefile`はOLE2コンテナーの解析に使える低レベルライブラリだが、WordやExcelの
文書を高水準のオブジェクトとして編集するライブラリではない。旧形式を扱う場合は、
専用ライブラリ、OLE2解析、またはOffice COM自動化のどれが必要かを先に決める。

### 代表的な使い分け

#### Word

`python-docx`は`.docx`の作成・更新を対象にしている。段落、スタイル、表、画像、
ヘッダー・フッターなどをPythonオブジェクトとして操作できる。Wordのレイアウトを
完全に再現する変換器ではなく、複雑な図形、フィールド、マクロなどは別途確認する。

`.docx`をHTMLへ変換して見出しやスタイルを意味構造へ寄せたい場合は`mammoth`も
候補になる。ただし、入力文書をサニタイズしないため、信頼できないファイルを扱う
場合は出力HTMLを検査する。

#### Excel

`openpyxl`は`.xlsx`、`.xlsm`、`.xltx`、`.xltm`の読み書きに向く。セルの値や数式、
書式、シート、画像などを扱えるが、Excelアプリケーションそのものの計算結果を
再計算するものではない。マクロを保持する場合は、読み込み時の設定と保存後の
動作確認が必要である。

旧式`.xls`の読み取りは`xlrd`、`.xlsb`の読み取りは`pyxlsb`が代表例である。
`pandas.read_excel()`は、`openpyxl`、`xlrd`、`pyxlsb`、`calamine`などを形式に
応じて使い分けられる。データ分析が目的で、書式や図形を保持しないなら、この
組み合わせが扱いやすい。

`python-calamine`はRustの`calamine`をPythonから利用するバインディングで、
Excelの複数形式を読み取る用途の候補である。ネイティブのExcelファイルを編集して
保存する用途では、`openpyxl`など対象形式専用のライブラリを優先する。

#### PowerPoint

`python-pptx`は`.pptx`の読み書きに対応し、スライド、テキスト、画像、表、図形、
グラフなどを操作できる。PowerPoint 2007以降のOpen XML形式が対象で、すべての
PowerPoint機能がPython APIに公開されているわけではない。高度なアニメーションや
未対応要素を完全に編集する場合は、`pywin32`によるPowerPoint COM操作も比較する。

#### Outlook、Access、Visio

- `.msg`からメールと添付ファイルを取り出すなら`extract-msg`が用途に合う。
- `.pst`はメールボックス全体のコンテナーであり、単純な`.msg`抽出とは別問題である。
  `libpff`/`pypff`などの環境依存の選択肢、またはOutlook COMを検討し、対象OSと
  配布方法を確認する。
- `.mdb`、`.accdb`は`pyodbc`だけで完結せず、対応するMicrosoft Access Database
  EngineなどのODBCドライバーをインストールして接続する。
- `.vsdx`はOOXML系のVisio形式で、`vsdx`パッケージに図形・テキストの読み書き
  機能がある。古いバイナリ`.vsd`は同じAPIで扱えるとは限らない。
- `.mpp`は専用形式であり、汎用のOfficeライブラリだけで高忠実度に扱えるとは
  考えない。対象のProject環境、変換サービス、商用SDKなどを個別に比較する。

#### Officeアプリを実際に操作する場合

書式、印刷設定、更新リンク、マクロ、PowerPointの高度な機能などをOffice自身に
処理させたい場合は、Windows版Officeを`pywin32`のCOMから操作する方法がある。
この方式はファイル形式の直接解析ではなく、Officeアプリを起動して操作する方式で
ある。そのため、Officeのインストール、ユーザーセッション、ダイアログ、プロセス
終了、同時実行、サーバー上での運用制約を考慮する。LinuxコンテナーやOffice未導入
環境には向かない。

### 最小の導入例

OOXML形式を直接処理する基本パッケージは次のように導入できる。

```powershell
python -m pip install python-docx openpyxl python-pptx
```

Excelの値だけを読み取る例:

```python
from pathlib import Path

import openpyxl


source = Path("sample.xlsx")
workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
worksheet = workbook.active

for row in worksheet.iter_rows(values_only=True):
    print(row)

workbook.close()
```

実際のアプリでは、入力拡張子を許可リストで検査し、上書き前に一時ファイルや
バックアップを使う。信頼できないOOXMLを読む場合は、`openpyxl`の公式注意事項に
従い、XML処理の防御策として`defusedxml`の利用を検討する。

### 選定の目安

1. **値・文章の抽出だけ**: `pandas`、`python-calamine`、`xlrd`、`pyxlsb`、
   `python-docx`、`extract-msg`など、読み取り中心のライブラリ。
2. **Office形式を編集して保存**: 形式専用の`openpyxl`、`python-docx`、
   `python-pptx`、`vsdx`。
3. **見た目やOffice固有機能を維持**: Windows上の`pywin32`または商用SDK。
4. **Microsoft 365のクラウドファイルを取得・更新**: `msgraph-sdk`または
   SharePoint対応クライアント。認証、権限、テナント設定が別途必要。

ライブラリの対応範囲はバージョンで変わるため、採用時は対象ファイルの実サンプル
（マクロ、結合セル、図形、暗号化、埋め込みオブジェクトを含む）で、読み取りだけ
でなく保存後のOfficeでの再現性も確認する。

## 参考資料

- [python-docx documentation](https://python-docx.readthedocs.io/en/latest/)
  - 参照日: 2026-09-15
- [openpyxl documentation](https://openpyxl.readthedocs.io/en/stable/)
  - 参照日: 2026-09-15
- [python-pptx documentation](https://python-pptx.readthedocs.io/en/latest/)
  - 参照日: 2026-09-15
- [pandas.read_excel documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
  - 参照日: 2026-09-15
- [xlrd - PyPI](https://pypi.org/project/xlrd/)
  - 参照日: 2026-09-15
- [pyxlsb - PyPI](https://pypi.org/project/pyxlsb/)
  - 参照日: 2026-09-15
- [python-calamine - PyPI](https://pypi.org/project/python-calamine/)
  - 参照日: 2026-09-15
- [extract-msg - GitHub](https://github.com/TeamMsgExtractor/msg-extractor)
  - 参照日: 2026-09-15
- [olefile - PyPI](https://pypi.org/project/olefile/)
  - 参照日: 2026-09-15
- [vsdx - PyPI](https://pypi.org/project/vsdx/)
  - 参照日: 2026-09-15
- [msoffcrypto-tool - PyPI](https://pypi.org/project/msoffcrypto-tool/)
  - 参照日: 2026-09-15
- [pywin32 - PyPI](https://pypi.org/project/pywin32/)
  - 参照日: 2026-09-15
- [Microsoft Graph SDK for Python](https://github.com/microsoftgraph/msgraph-sdk-python)
  - 参照日: 2026-09-15
- [driveItem resource type - Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0)
  - 参照日: 2026-09-15
- [Mammoth documentation](https://pypi.org/project/mammoth/)
  - 参照日: 2026-09-15

## 更新履歴

- 2026-09-15: 初版を作成。Office文書、旧形式、Outlook、Access、Visio、
  Microsoft 365を扱うPythonライブラリを比較。
