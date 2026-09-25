---
作成日: 2026-08-26
更新日: 2026-08-31
タグ:
  - Word
  - Markdown
  - Pandoc
  - Python
  - 文書変換
状態: 完了
---

# Word文書をMarkdownへ高忠実度変換する方法

## 概要

Word文書（主に `.docx`）をMarkdownへ変換する方法を、Pythonによる一括自動化、
表・画像・見出しなどの保持、複雑な表を扱う場合の限界という観点で整理する。

## 結論

通常の文書には、**PandocをPythonの`subprocess`から呼び出す方法**を第一候補とする。
見出し、箇条書き、リンク、脚注、画像、単純な表などの文書構造をまとめて扱え、
`--extract-media`で画像も分離できる。Pythonからは薄いラッパーである`pypandoc`も
使えるが、実行コマンドと終了コードが明確な`subprocess`はバッチ処理を管理しやすい。

ただし、**WordとMarkdownの間に完全で可逆な変換はない**。Pandoc自身も、複雑な表は
中間表現に収まらず、表現力の高い形式からMarkdownへの変換は欠落を伴うとしている。
特に次の要素は、一般的なMarkdown表では厳密に保持できない。

- 縦・横の結合セル
- 入れ子の表
- セルごとの幅、高さ、余白、罫線、背景色
- セル内の複数段落、箇条書き、画像
- 行頭・行末で省略されたセル

したがって、目的別に次の方針を採る。

| 目的 | 推奨方式 |
| --- | --- |
| 検索、Git管理、LLM入力、通常の閲覧 | Pandocで`docx`から`gfm`へ直接変換 |
| 結合セルなどの表構造を維持 | Markdown内にHTMLの`table`を残すハイブリッド方式 |
| 見た目をほぼ同じに維持 | HTMLまたはPDFを正本とし、Markdownは検索用の派生物にする |
| Wordスタイルを独自ルールで意味構造へ変換 | MammothでHTML化し、スタイルマップを指定 |
| 多種類の文書を同じPython処理へ載せる | DoclingまたはMarkItDownも候補。ただし実ファイル評価が必要 |

表を絶対に崩せない場合は、純粋なMarkdown表へ変換しない。対象のMarkdownビューアが
生HTMLを許可することを確認したうえで、`rowspan`、`colspan`を持つHTML表を埋め込む。
ビューアが生HTMLを無効化する場合は、HTMLファイル、PDF、または元の`.docx`への
リンクを併記する。

2026年8月31日時点のPandoc 3.11では、DOCX readerで不均一な行、および通常行の後に
見出し行が現れる表の処理が改善された。ただし、これは読み取り改善であり、GFMに
結合セル、罫線、セル余白などの表現構文がないという根本的な制約は変わらない。

## 詳細

### Markdownだけでは厳密な変換ができない理由

Wordの表は単純な行列に限らない。結合セルは複数のレイアウトグリッドを占有でき、
行の先頭または末尾のセルを省略でき、セル内に別の表も配置できる。一方、GFMの表は
ヘッダー行、区切り行、データ行からなる行列で、`rowspan`や`colspan`を指定する構文を
持たない。

つまり、変換ツールの性能だけでなく、**出力先のMarkdown自体に表現手段がない**。
セル結合を解除して値を繰り返せばデータは残せるが、見出しのグループ関係など元の
意味は変わる。列幅や罫線色を落とす場合も、内容は同じでも見た目は同じにならない。

### 方式の比較

| 方式 | 長所 | 表に関する注意 | 適する用途 |
| --- | --- | --- | --- |
| Pandoc | 対応要素が広く、CLIと自動化が安定している。画像抽出やフィルターも利用可能 | 複雑な表を完全には保持できないと公式に明記されている | 第一候補、一般文書の一括変換 |
| `pypandoc` | PandocをPython APIから呼べる。Pandoc同梱版もある | 変換能力はPandoc本体と同じで、限界を解消するものではない | Python内でAPIを統一したい場合 |
| Mammoth | Wordスタイルを意味的なHTMLへ割り当てられる | 表は扱えるが罫線などの表書式を無視する。Markdown直接出力は廃止予定で、HTML経由が推奨 | 定型スタイルの文書をきれいなHTMLへ変換 |
| Docling | DOCXを読み、統一文書モデルからMarkdown、HTML、JSONへ出力できる | DOCX表の全要素保持は公式の対応形式一覧だけでは保証されない | PDFなども含む共通パイプライン |
| MarkItDown | Pythonで導入しやすく、Word、表、リンクなどに対応 | 公式に、人向けの高忠実度変換には最適でない場合があるとしている | LLM入力、検索、テキスト分析 |
| WordでHTML保存 | Word自身の解釈でHTML化でき、結合セルをHTMLで表現しやすい | WordとWindowsが必要。不要なHTML/CSSの整理が必要 | 複雑表をHTMLのまま残す場合 |
| `python-docx`で自作 | 独自テンプレートに合わせて細かく制御できる | 結合、省略、入れ子表の解析が複雑。汎用変換器の自作は高コスト | 入力様式が固定された限定用途 |

### 推奨する基本コマンド

Pandocをインストールした後、次のように変換する。

```powershell
pandoc input.docx `
  --from=docx `
  --to=gfm+raw_html `
  --wrap=none `
  --extract-media=input_assets `
  --output=output.md
```

- `gfm`はGitHub Flavored Markdownを出力する。
- `+raw_html`は出力先で生HTMLを使えるようにする指定である。ただし、この指定だけで
  複雑なWord表が自動的にHTML表として完全保持される保証はない。
- `--wrap=none`は自動改行による不要な差分を減らす。
- `--extract-media`は文書内画像を指定フォルダへ展開する。
- 出力先のMarkdownビューアがGFMと生HTMLのどちらを許可するか、先に確認する。

### Pythonによるフォルダ一括変換

次の例は、指定フォルダ直下の`.docx`を変換し、Wordが作る一時ファイルを除外する。
Pandocの異常終了を成功扱いにせず、一時出力が完成してから本番ファイルへ置き換える。

```python
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def convert_docx(source: Path, output_dir: Path) -> Path:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("pandocがPATH上に見つかりません")

    source = source.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{source.stem}.md"
    temporary = output_dir / f"{source.stem}.md.tmp"
    media_dir = f"{source.stem}_assets"

    command = [
        pandoc,
        str(source),
        "--from=docx",
        "--to=gfm+raw_html",
        "--wrap=none",
        f"--extract-media={media_dir}",
        f"--output={temporary.name}",
    ]

    try:
        subprocess.run(
            command,
            cwd=output_dir,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        temporary.unlink(missing_ok=True)
        raise

    temporary.replace(destination)
    return destination


def convert_folder(input_dir: Path, output_dir: Path) -> list[Path]:
    sources = sorted(
        path
        for path in input_dir.glob("*.docx")
        if not path.name.startswith("~$")
    )
    return [convert_docx(source, output_dir) for source in sources]


if __name__ == "__main__":
    converted = convert_folder(Path("input"), Path("output"))
    for path in converted:
        print(path)
```

実行例:

```powershell
python convert_docx.py
```

`pypandoc`を使う場合も、実体はPandocである。通常版は別途Pandocが必要で、
`pypandoc_binary`はPandocを同梱する。再現性が必要な運用では、Pandocまたは
`pypandoc_binary`のバージョンを固定する。

### 複雑な表を保持する方法

#### 1. HTML表をMarkdownへ埋め込む

結合セルを次のようなHTMLとして残す。

```html
<table>
  <tr>
    <th colspan="2">上期</th>
  </tr>
  <tr>
    <td rowspan="2">売上</td>
    <td>4月</td>
  </tr>
  <tr>
    <td>5月</td>
  </tr>
</table>
```

この方式はセル結合の構造を表せるが、次を満たす場合に限って有効である。

1. 利用するMarkdown処理系が生HTMLを削除しない。
2. HTMLの`table`、`rowspan`、`colspan`を許可する。
3. 必要な見た目をHTML属性または許可されたCSSで再現できる。

GitHubなど公開先ごとのHTMLサニタイズ規則に依存するため、最終表示先で確認する。

#### 2. WordからHTMLを作る

WindowsにMicrosoft Wordがある場合、Word Automationの`Document.SaveAs2`と
`wdFormatFilteredHTML`を使ってHTMLへ保存できる。表をHTMLのままMarkdownへ埋め込む
方式は、純粋なMarkdown表に落とすより結合構造を保ちやすい。

ただし、Filtered HTMLでも完全なピクセル一致を保証するものではない。Word由来の
CSS整理、画像パスの移動、不要な要素の除去、および最終ビューアでの表示確認が必要に
なる。サーバーでWordの自動操作を行う構成は避け、デスクトップ上の管理されたバッチ
として使う。

#### 3. 表が複雑なら変換を止める

高忠実度を必須条件にする場合は、黙って単純化するより、次の要素を事前検出して
要確認として停止する方が安全である。

- OOXMLの`w:gridSpan`または`w:vMerge`がある
- 表の中に別の`w:tbl`がある
- `w:gridBefore`または`w:gridAfter`による省略セルがある
- セル内に複数段落、箇条書き、画像がある

これらを含む文書はHTML表ルートへ振り分けるか、元の`.docx`を正本として残す。
`python-docx`の通常の行セル列挙は、結合セルの値を各グリッド位置へ繰り返す近似を
行うため、単純な二次元配列だけを比較して「構造が保持された」と判定してはいけない。

### 変換後の検証

「コマンドが成功した」ことと「文書が正しく変換された」ことを分けて確認する。
実運用前に、少なくとも次の要素を持つ基準用DOCXを作成する。

1. 見出し1～3、通常段落、太字、斜体、リンク
2. 番号付き・番号なし・入れ子の箇条書き
3. 単純な表、横結合、縦結合、入れ子表
4. セル内の複数段落、箇条書き、画像
5. 本文画像、脚注、改ページ、テキストボックス
6. 日本語、英数字、記号、改行

検証は次の順で行う。

- **機械検証:** Pandocの終了コード、出力ファイル、画像ファイル、リンク切れを確認する。
- **構造検証:** 見出し数、表数、行列数、セル本文、画像数、脚注数を元文書と照合する。
- **複雑表検証:** 結合数と結合範囲、入れ子表数をOOXMLまたはHTMLの
  `rowspan`、`colspan`と照合する。
- **表示検証:** 実際に使うMarkdownビューアで、原本と並べて目視確認する。
- **回帰検証:** 変換器のバージョン更新時に同じ基準文書を再変換し、差分を確認する。

厳密な運用では、文書ごとに元DOCX、変換済みMarkdown、抽出画像、変換ログを同じ
識別子で保存する。Markdownだけを残して元文書を破棄してはならない。

### 選定の目安

- まずPandocで代表的な実文書を10件程度変換する。
- 単純な表だけで要件を満たすなら、そのままバッチ化する。
- 結合表が崩れる場合は、表だけHTMLとして残せる処理へ切り替える。
- 見た目の一致が要件なら、Markdown化を正本化の手段にせず、HTMLまたはPDFを正本に
  する。
- LLMへの入力が主目的であれば、MarkItDownやDoclingも同じ評価用文書で比較する。
  公式の対応形式一覧だけで精度を判断しない。

## 参考資料

- [Pandoc User's Guide](https://pandoc.org/MANUAL.html)
  - 参照日: 2026-08-31
- [Pandoc 3.11 release notes](https://github.com/jgm/pandoc/releases/tag/3.11)
  - 参照日: 2026-08-31
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/#tables-extension-)
  - 参照日: 2026-08-31
- [pypandoc README](https://github.com/JessicaTegner/pypandoc)
  - 参照日: 2026-08-31
- [Mammoth .docx to HTML converter](https://github.com/mwilliamson/python-mammoth)
  - 参照日: 2026-08-31
- [Docling Supported formats](https://docling-project.github.io/docling/usage/supported_formats/)
  - 参照日: 2026-08-31
- [Docling Quickstart](https://docling-project.github.io/docling/getting_started/quickstart/)
  - 参照日: 2026-08-31
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
  - 参照日: 2026-08-31
- [python-docx: Working with Tables](https://python-docx.readthedocs.io/en/latest/user/tables.html)
  - 参照日: 2026-08-31
- [Document.SaveAs2 method (Word)](https://learn.microsoft.com/en-us/office/vba/api/word.saveas2)
  - 参照日: 2026-08-31
- [WdSaveFormat enumeration (Word)](https://learn.microsoft.com/en-us/office/vba/api/word.wdsaveformat)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、Pandoc 3.11のDOCX表処理改善とMammothのMarkdown直接出力廃止予定を反映
- 2026-08-26: 初版を作成
