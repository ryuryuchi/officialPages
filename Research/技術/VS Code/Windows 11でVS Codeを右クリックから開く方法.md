---
作成日: 2026-09-14
更新日: 2026-09-14
タグ:
  - VS Code
  - Windows 11
  - コンテキストメニュー
  - インストール
状態: 完了
---

# Windows 11でVS Codeを右クリックから開く方法

## 概要

Windows 11のエクスプローラーで、ファイルやフォルダーを右クリックしたときに
Visual Studio Code（VS Code）で開く項目を表示する手順を整理する。VS Codeをすでに
インストール済みで、インストール時の選択を忘れた場合の復旧方法も対象にする。

## 結論

初回インストール時は、セットアップの追加タスクで次の2項目を選択する。

- `Add "Open with Code" action to Windows Explorer file context menu`
- `Add "Open with Code" action to Windows Explorer directory context menu`

すでにインストール済みの場合は、アンインストールせず、最初に使ったものと同じ
User setupまたはSystem setupの公式インストーラーをもう一度実行し、上記の項目を
選択して上書きインストールする。設定や拡張機能を消すためのアンインストールは
通常必要ない。

Windows 11の新しい右クリックメニューに表示されない場合は、右クリック後に
「その他のオプションを表示」を選ぶ。`Shift+F10`でも従来のコンテキストメニューを
表示できる。

## 詳細

### 1. これからVS Codeをインストールする場合

1. [VS Code公式Windowsセットアップ](https://code.visualstudio.com/docs/setup/windows)から
   User setupまたはSystem setupをダウンロードする。
2. インストーラーを起動し、通常どおりインストール先などを進める。
3. 追加タスクの画面で、次の2項目にチェックを入れる。
   - `Add "Open with Code" action to Windows Explorer file context menu`
   - `Add "Open with Code" action to Windows Explorer directory context menu`
4. 必要に応じて`Add to PATH`も選択する。これは右クリックメニューとは別に、
   ターミナルで`code .`を使うための設定である。
5. インストールを完了する。
6. エクスプローラーでファイルまたはフォルダーを右クリックし、`Open with Code`を
   選ぶ。Windows 11で見当たらなければ「その他のオプションを表示」を開く。

### 2. すでにVS Codeをインストール済みの場合

1. VS Codeで`ヘルプ` > `バージョン情報`を開き、現在のインストール形態を確認する。
   判断できない場合は、既存のインストール先を確認する。
   - User setupの標準的な場所: `%LOCALAPPDATA%\Programs\Microsoft VS Code`
   - System setupの標準的な場所: `C:\Program Files\Microsoft VS Code`
2. [VS Code公式ダウンロードページ](https://code.visualstudio.com/download)から、
   既存の形態に合うUser setupまたはSystem setupを入手する。
3. VS Codeを終了して、ダウンロードしたインストーラーを実行する。
4. 追加タスクで、ファイル用とフォルダー用の`Open with Code`を両方選択する。
5. セットアップを完了し、エクスプローラーで右クリックメニューを確認する。

既存のインストールと異なる形態のインストーラーを選ぶと、別の場所へインストール
することがある。そのため、User setupを使っていたならUser setup、System setupを
使っていたならSystem setupを再実行する。うまく反映されない場合は、エクスプローラー
を再起動するか、Windowsへサインインし直してから確認する。

### 3. 表示されない場合の確認順

1. ファイルとフォルダーの両方の追加タスクを選んだか確認する。
2. 右クリックメニューの「その他のオプションを表示」を確認する。
3. `Shift+F10`で従来のメニューを開いて確認する。
4. User setupとSystem setupを取り違えていないか確認する。
5. エクスプローラーを再起動し、必要ならWindowsを再起動する。
6. 公式インストーラーを最新版に更新して、同じ手順を再実行する。

レジストリを直接編集する方法もあるが、VS Codeのインストーラーが登録する内容と
食い違う可能性があり、通常の復旧方法としては推奨しない。

### 4. User setupとSystem setupの違い

User setupは通常、管理者権限なしでユーザー単位にインストールでき、標準のインストール
先は`%LOCALAPPDATA%\Programs\Microsoft VS Code`である。System setupは全ユーザー向け
で、管理者権限が必要になり、標準のインストール先は`Program Files`である。

右クリックメニューを使うだけなら、どちらでも追加タスクを選択すればよい。会社PCなどで
全ユーザーに同じ設定を適用したい場合はSystem setupが候補になるが、管理者権限が必要で
ある。

## 参考資料

- [Installing Visual Studio Code on Windows](https://code.visualstudio.com/docs/setup/windows)
  - 参照日: 2026-09-14
- [Download Visual Studio Code](https://code.visualstudio.com/download)
  - 参照日: 2026-09-14
- [VS Code Windows installer definition](https://raw.githubusercontent.com/microsoft/vscode/main/build/win32/code.iss)
  - 参照日: 2026-09-14
- [File Explorer in Windows](https://support.microsoft.com/en-au/windows/experience/fileexplorer/file-explorer-in-windows)
  - 参照日: 2026-09-14

## 更新履歴

- 2026-09-14: Windows 11の右クリックメニュー、初回インストール、既存インストールへの
  上書き適用、User setupとSystem setupの違いを公式資料で整理
