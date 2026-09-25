---
作成日: 2026-08-26
更新日: 2026-08-31
タグ:
  - Python
  - uv
  - パッケージ管理
  - 仮想環境
状態: 完了
---

# Pythonのuvの基本

## 概要

Python開発ツールの `uv` について、何をするものなのか、従来の `pip` や
`venv` とどう違うのか、主な使い道と基本操作を初心者向けに整理する。

## 結論

`uv` は、Python本体、仮想環境、ライブラリ、プロジェクト、Python製CLIツールを
まとめて扱える、高速なパッケージ・プロジェクト管理ツールである。Rustで実装され、
Ruffを開発するAstralが提供している。

一言でいえば、従来は `pyenv`、`venv`、`pip`、`pip-tools`、`pipx`、
Poetryなどに分かれていた役割の多くを、1つの `uv` コマンドで扱えるようにしたもの。
ただし、それらすべてと完全に同じ挙動ではない。

新しくPythonプロジェクトを始めるなら、まず次の流れを覚えればよい。

```powershell
uv init --app --no-package my-app
cd my-app
uv add requests
uv run python main.py
```

この操作で、プロジェクト定義、仮想環境、依存関係の記録と固定、プログラムの実行を
一貫して管理できる。仮想環境を手作業で有効化しなくても `uv run` から実行可能である。
2026年8月31日時点の最新安定版は`0.12.7`（2026年8月27日公開）である。

## 詳細

### uvは何を解決するものか

Pythonでは、従来は目的ごとに複数の操作やツールを使うことが多かった。

| やりたいこと | 従来の代表例 | uvでの代表例 |
| --- | --- | --- |
| Python本体を入れる・切り替える | 公式インストーラー、pyenv | `uv python install`、`uv python pin` |
| 仮想環境を作る | `python -m venv .venv` | `uv venv`、またはプロジェクト操作時に自動作成 |
| ライブラリを追加する | `pip install requests` | `uv add requests` |
| 依存バージョンを固定する | `pip-tools`など | `uv.lock`を自動生成 |
| 環境を同じ状態にそろえる | `pip install -r requirements.txt` | `uv sync` |
| 環境内でコマンドを実行する | 仮想環境を有効化して実行 | `uv run ...` |
| Python製CLIを一時実行する | `pipx run` | `uvx` |
| Python製CLIを常用できるように入れる | `pipx install` | `uv tool install` |

`uv` の利点は単にインストールが速いことだけではない。プロジェクトで必要なPythonの
バージョンとライブラリをファイルに記録し、別のPCや他の開発者でも同じ環境を
再現しやすくする点が重要である。

### 用語をざっくり理解する

#### パッケージ

`requests`、`pandas`、`pytest`など、Pythonへ追加して使うライブラリやツール。

#### 仮想環境

プロジェクトごとにパッケージを分離する仕組み。プロジェクトAとBで異なるバージョンの
同じライブラリを使っても衝突しにくくなる。`uv` のプロジェクトでは通常、
`pyproject.toml` と同じ場所の `.venv` に作られる。

#### `pyproject.toml`

プロジェクト名、対応するPythonの範囲、直接利用する依存パッケージなどを記録する
標準的な設定ファイル。`uv add` や `uv remove` によって更新される。

#### `uv.lock`

間接依存も含め、実際に解決したパッケージの正確なバージョンを記録する
`uv` 専用のロックファイル。異なるOS、CPU、Pythonバージョンにまたがる解決結果を
保持できる。手で編集せず、通常はGitへコミットする。

Python標準の解決結果形式`pylock.toml`（PEP 751）も、`uv export -o pylock.toml`、
`uv pip compile ... -o pylock.toml`、`uv pip sync pylock.toml`などで扱える。ただし、
uvのプロジェクト機能には`pylock.toml`で表現できない情報があるため、プロジェクトの
正本は引き続き`uv.lock`である。

`.venv` は各PCで作り直せるため、通常はGitへコミットしない。

### 主な使い道

#### 1. 新しいPythonプロジェクトを管理する

最も基本的な用途である。

現在の`uv init`はパッケージ型アプリを既定とし、`src`レイアウトとコマンド入口を
生成する。1ファイルの`main.py`から始める例では、意図を明確にするため
`--app --no-package`を指定する。ライブラリなら`uv init --lib`を使う。

```powershell
# main.pyを持つ非パッケージ型アプリを新規作成
uv init --app --no-package my-app
cd my-app

# ライブラリを追加
uv add requests

# 開発時だけ使うライブラリを追加
uv add --dev pytest

# プログラムやテストをプロジェクト環境内で実行
uv run python main.py
uv run pytest
```

`uv add` はパッケージをその場で入れるだけでなく、`pyproject.toml` と
`uv.lock` に依存関係を記録する。`uv run` は必要に応じてロックと同期を行い、
`.venv` がなければ作成する。そのため、通常は毎回
`.venv\Scripts\Activate.ps1` を実行しなくてもよい。

既存プロジェクトを取得した側は、次のコマンドでロックファイルに基づく環境を作れる。

```powershell
git clone <repository-url>
cd <repository>
uv sync
uv run python main.py
```

よく使う関連コマンドは次のとおり。

```powershell
uv remove requests  # 依存パッケージを削除
uv tree             # 依存関係をツリー表示
uv lock             # ロックファイルを明示的に更新
uv sync             # 環境をロックファイルに同期
```

#### 2. Python本体をインストール・切り替えする

```powershell
uv python install 3.13
uv python list
uv python pin 3.13
```

`uv python pin 3.13` は通常、カレントディレクトリに `.python-version` を作り、
そのプロジェクトで使うPythonを指定する。対応するPythonが見つからない場合、
設定やコマンドに応じて `uv` が管理対象のPythonをダウンロードできる。

#### 3. 単発のPythonスクリプトを実行する

依存パッケージのないスクリプトなら、次のように実行できる。

```powershell
uv run script.py
```

1ファイルだけで配布したいスクリプトでは、依存情報をファイル内のメタデータへ
追加できる。

```powershell
uv add --script script.py requests
uv run script.py
```

これにより、利用者が仮想環境を手で作って `pip install` する手間を減らせる。

#### 4. RuffやBlackなどのCLIツールを使う

一度だけ、または試しに実行する場合は `uvx` を使う。

```powershell
uvx ruff check .
```

`uvx` は `uv tool run` の短縮形で、プロジェクトの環境とは分離された一時環境で
ツールを実行する。常用するツールはユーザー環境へインストールできる。

```powershell
uv tool install ruff
ruff --version
uv tool list
```

プロジェクトごとにバージョンを固定したい開発ツールは、グローバルな
`uv tool install` より `uv add --dev` と `uv run` を使う方が再現しやすい。

#### 5. 既存のpip中心の手順を高速化する

既存プロジェクトが `requirements.txt` を使っている場合、すぐに
`pyproject.toml` 方式へ移行せず、pip互換インターフェースを使うこともできる。

```powershell
uv venv
uv pip install -r requirements.txt
uv pip freeze
```

ただし `uv pip` は、一般的な `pip` と `pip-tools` のワークフローを置き換えるための
インターフェースであり、`pip` の完全なクローンではない。特殊なオプションや
細かな挙動に依存している場合は、公式の互換性ガイドを確認する。

### Windowsでの導入

公式スタンドアロンインストーラーを使う場合は、PowerShellで次を実行する。

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

WinGetを使う方法もある。

```powershell
winget install --id=astral-sh.uv -e
```

インストール後に新しいPowerShellを開き、確認する。

```powershell
uv --version
uv --help
```

スタンドアロンインストーラーで導入した場合は、次のコマンドで自身を更新できる。
WinGetやpipなど別の方法で導入した場合は、そのパッケージマネージャー側で更新する。

```powershell
uv self update
```

### 最初に試す最小チュートリアル

```powershell
# 1. サンプルプロジェクトを作る
uv init --app --no-package uv-sample
cd uv-sample

# 2. HTTP通信用ライブラリを追加する
uv add requests

# 3. main.pyを編集した後、uv管理環境で実行する
uv run python main.py
```

`main.py` の例:

```python
import requests

response = requests.get("https://example.com", timeout=10)
print(response.status_code)
```

終わった後に確認すると、主に次のファイルとフォルダが作られている。

- `pyproject.toml`: プロジェクト情報と直接依存
- `uv.lock`: 解決された正確な依存バージョン
- `.venv`: このPC上の仮想環境
- `.python-version`: `uv init` の設定やバージョンにより作成されるPython指定

### pipやPoetryとの使い分け

#### pipとの関係

`pip` は主に「現在のPython環境へパッケージをインストールする」ツールである。
一方、`uv` のプロジェクト機能は、仮想環境の作成、依存の追加、ロック、同期、
実行までまとめて扱う。新規プロジェクトなら `uv add` と `uv run` を中心に使い、
`uv pip install` は既存のrequirements方式を維持したい場合に使うと理解しやすい。

#### Poetryとの関係

どちらも `pyproject.toml` を中心に依存関係とプロジェクトを管理できる。
既にPoetryで安定運用しているプロジェクトは、`uv` が存在するという理由だけで
急いで移行する必要はない。新規開発で、Python本体の管理やCLIツールの実行まで
1つの高速なツールにまとめたいなら `uv` が有力な選択肢になる。

### 注意点

- `uv.lock` は `uv` 専用形式であり、他ツールがそのまま利用できるとは限らない。
- 標準形式との受け渡しが必要なら`pylock.toml`への書き出しを検討するが、
  uvプロジェクト内の`uv.lock`を置き換えるものではない。
- `uv.lock` と `pyproject.toml` は原則としてGitへコミットし、`.venv` はしない。
- `uv` 管理プロジェクトの `.venv` を `uv pip install` で直接変更するのではなく、
  プロジェクト依存には `uv add`、一時的な追加には `uvx` または
  `uv run --with` を使うことが公式に推奨されている。
- `uv sync` は環境をロック結果へそろえる操作である。手作業で追加したパッケージは
  管理対象外となり、同期時に削除される可能性がある。
- pip互換インターフェースにも挙動差があるため、複雑な既存環境では段階的に試す。
- 会社のプロキシ、プライベートパッケージ、独自の認証がある環境では、
  インデックスと認証の設定を別途確認する。

### 迷ったときの選び方

- **新しいアプリやライブラリを作る**: `uv init`、`uv add`、`uv run`を使う。
- **単一の`main.py`から始める**: `uv init --app --no-package`を使う。
- **既存のrequirements方式を保つ**: `uv venv`、`uv pip install`から試す。
- **Ruffなどを一度だけ実行する**: `uvx`を使う。
- **Pythonのバージョンもまとめて管理したい**: `uv python install`と
  `uv python pin`を使う。
- **既存のPoetryプロジェクトが問題なく動いている**: 無理に移行せず、
  移行効果とCI・デプロイへの影響を先に検証する。

初心者が最初に覚えるべき中心コマンドは、
`uv init`、`uv add`、`uv run`、`uv sync` の4つである。

## 参考資料

- [uv - An extremely fast Python package and project manager](https://docs.astral.sh/uv/)
  - 参照日: 2026-08-31
- [Features](https://docs.astral.sh/uv/getting-started/features/)
  - 参照日: 2026-08-31
- [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)
  - 参照日: 2026-08-31
- [Working on projects](https://docs.astral.sh/uv/guides/projects/)
  - 参照日: 2026-08-31
- [Project structure and files](https://docs.astral.sh/uv/concepts/projects/layout/)
  - 参照日: 2026-08-31
- [Running scripts](https://docs.astral.sh/uv/guides/scripts/)
  - 参照日: 2026-08-31
- [Using tools](https://docs.astral.sh/uv/guides/tools/)
  - 参照日: 2026-08-31
- [Compatibility with pip and pip-tools](https://docs.astral.sh/uv/pip/compatibility/)
  - 参照日: 2026-08-31
- [uv CLI Reference](https://docs.astral.sh/uv/reference/cli/#uv-init)
  - 参照日: 2026-08-31
- [uv 0.12.7 release](https://github.com/astral-sh/uv/releases/tag/0.12.7)
  - 参照日: 2026-08-31
- [uv - PyPI](https://pypi.org/project/uv/)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、uv 0.12.7、`uv init`の現行既定、PEP 751の`pylock.toml`対応を反映
- 2026-08-26: 初版を作成
