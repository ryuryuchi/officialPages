---
作成日: 2026-09-25
更新日: 2026-10-08
タグ:
  - Python
  - Pandoc
  - Markdown
  - CSS
状態: 完了
---

# Pandoc出力を装飾する方法

## 概要

PythonからPandocを使ってMarkdownなどの文書をHTML、Word、PDFへ変換するとき、
CSSなどで見た目を整えられるか、出力形式ごとの方法と制約を調べた。

## 結論

**Pandocでは出力形式に応じた方法で体裁を整えられる。** HTMLならCSS、Wordなら
Wordのスタイルを定義した参照DOCX、PDFならPDFエンジンに応じた設定やテンプレートを
使う。CSSをそのまま適用できるのはHTML出力、またはHTMLを経由してPDFを作る場合で、
どの形式にも共通のCSSを適用する仕組みではない。

Pythonで使う`pypandoc`はPandoc本体を呼び出すラッパーであり、変換機能や出力形式別の
オプションはPandocに従う。`extra_args`へPandocのコマンドライン引数をリストで渡すと、
PythonからCSSや参照DOCXなどを指定できる。

## 詳細

### PandocとPythonラッパーの役割

PandocはMarkdown、HTML、Wordなどの文書形式を相互変換するツールである。文書を内部の
構造表現に読み込み、出力形式に合わせて書き出す。そのため、装飾方法は出力形式ごとに
異なる。

Pythonから利用する場合、選択肢の一つは`pypandoc`である。これはPandocの薄いラッパー
なので、`pypandoc`だけで全ての変換処理が完結するわけではない。通常の`pypandoc`
パッケージでは別途Pandocのインストールが必要で、Pandocを含む配布物として
`pypandoc_binary`も提供されている。

### HTMLにCSSを適用する

Pandocへ`--css`を渡すと、生成するHTMLから外部CSSを読み込める。CSSリンクを含む
`<head>`が必要なため、HTMLファイル全体を出力する`--standalone`も指定する。

```python
from pathlib import Path

import pypandoc


source = Path("input.md")
pypandoc.convert_file(
    source,
    to="html",
    outputfile="output.html",
    extra_args=[
        "--standalone",
        "--css=style.css",
    ],
)
```

CSSの例は次のとおり。

```css
body {
  max-width: 48rem;
  margin: 2rem auto;
  padding: 0 1rem;
  color: #222;
  font-family: sans-serif;
  line-height: 1.7;
}

h1,
h2 {
  color: #174a7e;
}

blockquote {
  border-left: 4px solid #8aaac8;
  margin-left: 0;
  padding-left: 1rem;
}
```

このCSSはHTMLの表示を整えるもので、元のMarkdownファイル自体の見た目を変えるもの
ではない。Markdownの表示は、HTMLに変換した後にブラウザーやMarkdownビューアーが
どのCSSを使うかで決まる。

CSSは生成されたHTMLから参照されるため、配布先でもCSSを参照できるようにする。
`style.css`をHTMLと同じ場所に置く、適切な相対パスを指定する、またはWeb上の公開先を
指定するなど、HTMLを開く環境に合わせて管理する。

### Word（DOCX）の見た目を整える

Word出力ではCSSではなく、`--reference-doc`で指定する参照DOCXを使う。Wordで参照DOCXの
見出し、本文、表などのスタイルを編集し、それをPandocの出力に反映させる。

```python
pypandoc.convert_file(
    "input.md",
    to="docx",
    outputfile="output.docx",
    extra_args=["--reference-doc=reference.docx"],
)
```

HTMLで使ったCSSがDOCXに適用されるわけではない。Wordファイルとして編集・配布する
用途では、参照DOCX側のスタイルを調整する。

### PDFの見た目を整える

PDFはPandoc単独で直接描画するのではなく、別のPDFエンジンを使って生成する。既定では
LaTeXが使われるため、LaTeXの変数やヘッダー設定など、選択したエンジンに対応する方法で
調整する。HTMLを中間形式として使う構成ではCSSを利用できるが、その場合も必要な
PDFエンジンのインストールと設定が必要である。

つまり、「PDFにしたいからCSSを付ける」だけでは足りず、どのPDFエンジンで出力するかを
決めてからスタイルを選ぶ。

### 出力形式別の選び方

| 出力先 | 主なスタイル指定 | 向いている用途 |
| --- | --- | --- |
| HTML | `--css`、必要に応じてHTMLテンプレート | Web公開、ブラウザーで閲覧 |
| DOCX | `--reference-doc`で参照DOCXを指定 | Wordで編集・共有 |
| PDF | PDFエンジン別の変数、テンプレート、またはHTML経由のCSS | レイアウトを固定して配布 |

Pythonからは、これらのPandocオプションを`extra_args`のリストに入れて渡す。独自の
処理を加えたい場合はフィルターも使えるが、CSSやテンプレートが担う見た目の指定とは
役割が異なる。フィルターは変換途中の文書構造を加工する方法である。

なお、Pandocは異なる文書形式間で完全に同じ見た目を保つツールではない。元形式の
レイアウトや複雑な要素が、出力先の形式でそのまま表現できるとは限らない。実際に使う
Markdown、画像、表を含むサンプルで出力を確認する。

WordからMarkdownへ変換する方法は、[Word文書をMarkdownへ高忠実度変換する方法](../Word/Word文書をMarkdownへ高忠実度変換する方法.md)を参照。

## 参考資料

- [Pandoc User's Guide: Creating a standalone HTML file](https://pandoc.org/MANUAL.html#option--standalone)
  - 参照日: 2026-09-25
- [Pandoc User's Guide: `--css` option](https://pandoc.org/MANUAL.html#option--css)
  - 参照日: 2026-09-25
- [Pandoc User's Guide: `--reference-doc` option](https://pandoc.org/MANUAL.html#option--reference-doc)
  - 参照日: 2026-09-25
- [Pandoc User's Guide: Creating a PDF](https://pandoc.org/MANUAL.html#creating-a-pdf)
  - 参照日: 2026-09-25
- [Pandoc User's Guide: Templates](https://pandoc.org/MANUAL.html#templates)
  - 参照日: 2026-09-25
- [pypandoc README](https://github.com/JessicaTegner/pypandoc)
  - 参照日: 2026-09-25
- [pypandoc - PyPI](https://pypi.org/project/pypandoc/)
  - 参照日: 2026-09-25

## 更新履歴

- 2026-10-08: yomiyasuの原則に基づき本文を推敲

- 2026-09-25: 初版を作成。HTML/CSS、DOCX参照ファイル、PDFエンジンごとの装飾方法を整理
