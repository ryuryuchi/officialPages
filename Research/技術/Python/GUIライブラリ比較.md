---
作成日: 2026-08-24
更新日: 2026-08-31
タグ:
  - Python
  - GUI
  - デスクトップアプリ
  - UI
状態: 完了
---

# Python GUIライブラリ比較

## 概要

Pythonの代表的なGUIライブラリを、軽さ、見た目、自由度の観点で比較する。

## 結論

| 重視する点 | 第一候補 | 特徴 |
| --- | --- | --- |
| 軽さ | Tkinter / ttk | Python標準で、追加インストールが基本的に不要 |
| 軽さと見た目の両立 | CustomTkinter | Tkinterベースでモダンな外観 |
| 見た目のきれいさ | PySide6 | 高品質で本格的なデスクトップGUI |
| 手軽なモダンUI | Flet | Flutter風のUIをPythonで構築可能 |
| 自由度 | PySide6 | ウィジェット、描画、デザインの自由度が高い |
| 独自デザイン・タッチ操作 | Kivy | アニメーションやカスタム描画に強い |
| 高速グラフ・開発ツール | Dear PyGui | GPU描画とリアルタイム更新に強い |

## 詳細

### 2026年8月31日時点の公開状況

各プロジェクトの公式文書とPyPIメタデータを照合した。バージョン番号と
`Requires-Python`は調査日時点の値であり、導入時には再確認する。

| ライブラリ | 最新安定版 | Python要件 |
| --- | --- | --- |
| CustomTkinter | 6.0.0 | 3.7以上 |
| ttkbootstrap | 2.2.2 | 3.10以上 |
| PySide6 | 6.11.2 | 3.10以上、3.15未満 |
| Flet | 0.86.5 | 3.10以上 |
| NiceGUI | 3.16.0 | 3.10以上、4未満 |
| Kivy | 2.3.1 | 3.8以上 |
| Dear PyGui | 2.3.1 | 3.8以上 |
| wxPython | 4.3.1 | 3.10以上 |

TkinterはPython標準ライブラリだが、PythonビルドによってはTkが任意部品となる。
利用可否は`python -m tkinter`で確認できる。Python 3.15はプレリリース段階であり、
特にバイナリwheelを使うGUIでは、Python 3.14以下の対応済み安定版を選ぶ方が確実である。

### 軽さ重視

#### Tkinter / ttk

Pythonに標準搭載されており、小規模なGUIツールに適している。

**長所**

- 追加インストールが基本的に不要
- 起動が速く、メモリ使用量も比較的少ない
- 配布サイズを小さくしやすい
- 情報やサンプルが多い

**短所**

- 標準状態では見た目が古くなりやすい
- 複雑な画面ではコード量が増えやすい
- アニメーションや高度な描画には不向き

**適した用途**

- ファイル変換ツール
- CSV・Excel操作ツール
- 社内業務ツール
- 設定画面
- 小規模なWindows自動化ツール

#### CustomTkinter

Tkinterをベースに、モダンなウィジェットを提供する。

**長所**

- Tkinterより現代的な見た目
- ダークモードに対応
- Tkinter経験者には理解しやすい
- 小規模ツールを短期間で作りやすい

**短所**

- 標準ライブラリではない
- ウィジェットの種類はPySide6ほど多くない
- 複雑なアプリケーションでは限界がある

「軽くて、ある程度きれい」を求める場合の有力候補。

#### ttkbootstrap

Tkinterの`ttk`ウィジェットにBootstrap風のテーマを適用する。

**長所**

- 既存のTkinterコードを活用しやすい
- CustomTkinterより標準の`ttk`に近い
- テーマを変更しやすい
- 比較的軽量

**短所**

- 独自デザインの自由度はあまり高くない
- 高度なGUIにはPySide6のほうが適している

既存のTkinterアプリの外観を改善したい場合に適している。

### GUIのきれいさ重視

#### PySide6

Qtの公式Pythonバインディング。本格的なデスクトップアプリの有力候補。

**長所**

- 標準ウィジェットの品質が高い
- Windowsらしい本格的なアプリを作れる
- ダークテーマやスタイルシートに対応
- Qt Designerで画面を視覚的に設計できる
- テーブル、ツリー、タブ、ドックなどが充実
- 中規模から大規模なアプリにも対応できる

**短所**

- Tkinterより重い
- インストールサイズと配布サイズが大きい
- Qtの仕組みを覚える必要がある
- シグナル、スロット、イベントループなどの理解が必要

**適した用途**

- 一般ユーザー向けデスクトップアプリ
- 高品質な社内ツール
- データ管理アプリ
- 画像・動画処理アプリ
- 複数画面を持つ中規模以上のアプリ

PyQt6も類似した選択肢だが、新規開発ではライセンス条件を確認したうえで、
まずPySide6を検討するとよい。

#### Flet

FlutterベースのGUIをPythonから構築する。

**長所**

- モダンなデザインを作りやすい
- レスポンシブレイアウトに対応
- デスクトップ、Web、モバイルへの展開を検討できる
- Pythonだけで比較的手軽に画面を作れる

**短所**

- Tkinterより重い
- ネイティブなWindowsアプリとは操作感が多少異なる
- 細かな制御ではQtに劣る場合がある
- Flet独自の仕組みへの依存が大きくなる

**適した用途**

- モダンな業務アプリ
- Webとデスクトップの両方を視野に入れたアプリ
- ダッシュボード
- 入力フォーム中心のアプリ
- プロトタイプ

#### NiceGUI

Web技術を使用し、ブラウザ上にモダンなGUIを構築する。

**長所**

- Webらしい画面を作りやすい
- ダッシュボードや管理画面に強い
- HTML、CSS、JavaScriptと組み合わせられる
- ネットワーク経由で複数端末から利用できる

**短所**

- 従来型のデスクトップGUIではない
- ローカルサーバーとブラウザを使用する
- 単純なツールとしては構成が重い
- デスクトップ固有機能との連携には工夫が必要

### GUIの自由度重視

#### PySide6

自由度と実用性のバランスに優れている。

**主な機能**

- Qt Style Sheetsによるデザイン変更
- 独自ウィジェットの作成
- マウス・キーボードイベントの詳細制御
- 2DグラフィックスとOpenGL連携
- Webページ表示
- 動画・音声再生
- ドラッグ＆ドロップ
- 複数ウィンドウとシステムトレイ
- 高度なテーブルとツリー
- Qt Quick/QMLによるアニメーションUI

通常のデスクトップアプリで自由度を求める場合の第一候補。

#### Kivy

独自デザイン、タッチ操作、アニメーションに強い。

**長所**

- ウィジェットを自由にデザインできる
- アニメーションとマルチタッチに対応
- Windows、Linux、macOS、Android、iOSを対象にできる
- ゲーム風、タブレット風のUIを作りやすい

**短所**

- Windows標準アプリのような外観にはなりにくい
- 通常の業務アプリでは操作感が独特になる
- 配布やモバイル向けビルドの難易度が高め
- 日本語入力やプラットフォーム固有の挙動に注意が必要

**適した用途**

- タッチパネルやキオスク端末
- 展示用・教育用アプリ
- 独自UI
- モバイル展開を考えたアプリ

#### Dear PyGui

GPUを利用するImmediate Mode GUIライブラリ。

**長所**

- 描画が高速
- グラフやリアルタイム更新に強い
- コードから画面を動的に構築しやすい
- OpenGLやGPU系ツールとの相性がよい

**短所**

- 一般的なWindowsアプリとは異なる外観
- フォーム中心の業務アプリにはやや不向き
- PySide6ほどデスクトップ機能が充実していない

**適した用途**

- リアルタイムモニター
- グラフ表示
- シミュレーター
- 開発者向けツール
- 画像処理パラメーターの調整画面

#### wxPython

OSのネイティブウィジェットを利用する。

**長所**

- OSに自然になじむ見た目と操作感
- 本格的なデスクトップアプリを作れる
- Tkinterより高機能

**短所**

- PySide6より日本語資料や最近の事例が少ない
- レイアウト管理に慣れが必要
- 独自デザインではQtに劣る

### 総合比較

5段階の相対評価。軽さには、起動速度、依存関係、メモリ使用量、
配布サイズを含む。

| ライブラリ | 軽さ | 見た目 | 自由度 | 学習しやすさ | 大規模開発 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tkinter / ttk | 5 | 2 | 2 | 5 | 2 |
| ttkbootstrap | 4 | 3 | 2 | 4 | 2 |
| CustomTkinter | 4 | 4 | 3 | 4 | 2 |
| PySide6 | 2 | 5 | 5 | 3 | 5 |
| wxPython | 3 | 4 | 3 | 3 | 4 |
| Flet | 2 | 5 | 3 | 4 | 3 |
| NiceGUI | 2 | 5 | 4 | 4 | 4 |
| Kivy | 2 | 4 | 5 | 2 | 3 |
| Dear PyGui | 4 | 3 | 4 | 3 | 3 |

### 用途別のおすすめ

| 用途 | おすすめ |
| --- | --- |
| 小さなWindows便利ツール | Tkinter / ttk |
| 軽さと見た目を両立した小規模ツール | CustomTkinter |
| 既存Tkinterアプリの外観改善 | ttkbootstrap |
| きれいで本格的なデスクトップアプリ | PySide6 |
| Webとデスクトップの両対応 | Flet |
| ブラウザや社内ネットワークで利用 | NiceGUI |
| 独自UIやタッチ操作 | Kivy |
| リアルタイムグラフや高速描画 | Dear PyGui |
| OSになじむネイティブな外観 | wxPython |

### 選び方

1. 小規模で軽さを優先するなら、Tkinterを選ぶ。
2. 小規模で見た目も重視するなら、CustomTkinterを選ぶ。
3. 長期運用や本格開発なら、PySide6を選ぶ。
4. Webとデスクトップの両対応なら、Fletを選ぶ。
5. 独自UIやタッチ操作なら、Kivyを選ぶ。
6. グラフやリアルタイム描画なら、Dear PyGuiを選ぶ。

Windows向けのファイル処理・自動化ツールでは、簡単なものには
CustomTkinter、複雑で長期運用するものにはPySide6が実用的である。

## 参考資料

- [tkinter — Python interface to Tcl/Tk（Python公式ドキュメント）](https://docs.python.org/3/library/tkinter.html)
  - 参照日: 2026-08-31
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
  - 参照日: 2026-08-31
- [CustomTkinter - PyPI](https://pypi.org/project/customtkinter/)
  - 参照日: 2026-08-31
- [ttkbootstrap Documentation](https://www.ttkbootstrap.org/en/latest/)
  - 参照日: 2026-08-31
- [ttkbootstrap - PyPI](https://pypi.org/project/ttkbootstrap/)
  - 参照日: 2026-08-31
- [Qt for Python Documentation（PySide6）](https://doc.qt.io/qtforpython-6/)
  - 参照日: 2026-08-31
- [PySide6 - PyPI](https://pypi.org/project/PySide6/)
  - 参照日: 2026-08-31
- [Flet Documentation](https://flet.dev/docs/)
  - 参照日: 2026-08-31
- [Flet - PyPI](https://pypi.org/project/flet/)
  - 参照日: 2026-08-31
- [NiceGUI Documentation](https://nicegui.io/documentation)
  - 参照日: 2026-08-31
- [NiceGUI - PyPI](https://pypi.org/project/nicegui/)
  - 参照日: 2026-08-31
- [Kivy Documentation](https://kivy.org/doc/stable/)
  - 参照日: 2026-08-31
- [Kivy - PyPI](https://pypi.org/project/Kivy/)
  - 参照日: 2026-08-31
- [Dear PyGui Documentation](https://dearpygui.readthedocs.io/en/latest/)
  - 参照日: 2026-08-31
- [Dear PyGui - PyPI](https://pypi.org/project/dearpygui/)
  - 参照日: 2026-08-31
- [wxPython API Documentation](https://docs.wxpython.org/)
  - 参照日: 2026-08-31
- [wxPython - PyPI](https://pypi.org/project/wxPython/)
  - 参照日: 2026-08-31
- [Python Developer's Guide: Status of Python versions](https://devguide.python.org/versions/)
  - 参照日: 2026-08-31

なお、「総合比較」の評価と「用途別のおすすめ」は、上記の公式情報を
踏まえた相対的な評価である。

## 更新履歴

- 2026-08-31: 全参考URLと各プロジェクトのPyPI情報を実査し、現行版・Python要件を追加してRule形式へ補正
- 2026-08-24: 初版を作成
