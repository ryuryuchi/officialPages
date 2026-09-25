---
作成日: 2026-09-08
更新日: 2026-09-08
タグ:
  - Git
  - リモート
  - origin
  - SSH
  - HTTPS
状態: 完了
---

# Gitのリモート接続先を変更する方法

## 概要

ローカルリポジトリに設定済みの Git リモートを、別のリポジトリまたは別の接続方式
（HTTPS / SSH）へ安全に切り替える方法を整理する。

## 結論

現在使っているリモート（通常は `origin`）を別の接続先に置き換えるには、対象リポジトリ
のディレクトリで、`git remote -v` に表示された実際のリモート名を使って次を実行する。

```powershell
git remote -v
git remote set-url <remote-name> <新しいURL>
git remote -v
git ls-remote <remote-name>
```

`git remote set-url` は既存リモートの fetch URL を変更する。個別の push URL が未設定なら
push にもその URL が使われる。以前の接続先を残しておきたい場合は、置換せず
`git remote add <名前> <URL>` で別名のリモートを追加する。

URL と接続先リポジトリを誤ると、次の `git push` の送信先も変わる。切替直後は、まず
`git ls-remote <remote-name>` で読み取り接続を確認してから、意図したブランチだけを明示して
push する。

`git ls-remote` が GitHub の `Repository not found` で失敗したときは、URLが誤っている、
対象リポジトリが未作成・削除済み、または現在の認証情報に非公開リポジトリへの権限がない、
のいずれかである。GitHub は非公開リポジトリの存在を隠すため、未存在と権限不足を同じ
メッセージで返すことがある。

## 詳細

### 1. 現在の設定を確認する

対象のローカルリポジトリへ移動して、リモート名と fetch / push の URL を確認する。

```powershell
Set-Location <ローカルリポジトリのパス>
git remote -v
```

一般的なリモート名は `origin` だが、実際に表示された名前を後続のコマンドで使用する。
`origin`、ブランチ名の `main` や `master` は、リモート名ではない。たとえば表示が
`Research  https://github.com/ryuryuchi/Research.git` であれば、対象名は `Research` である。
存在しない名前で `git remote set-url` を実行すると `No such remote` で失敗する。

### 2. 既存の接続先を置き換える

同じリモート名の接続先だけを変更する場合は、次のように実行する。

```powershell
# HTTPS の例。remote-name は git remote -v で確認した名前に置き換える
git remote set-url <remote-name> https://github.com/OWNER/NEW-REPOSITORY.git

# SSH の例
git remote set-url <remote-name> git@github.com:OWNER/NEW-REPOSITORY.git
```

このコマンドは指定したリモートの fetch URL を変更する。個別の push URL が設定されていない通常の
構成では、push にも新しい fetch URL が使われる。一方、個別の push URL がすでにある場合は
変更されないため、変更後は両方の設定値と実際の読み取り接続を確認する。

```powershell
git remote get-url <remote-name>
git remote get-url --push <remote-name>
git ls-remote <remote-name>
```

`git ls-remote <remote-name>` が成功すれば、認証とネットワークを含むリモートへの読み取り接続を
確認できる。push 前には、送信するブランチを明示する。

```powershell
git push -u <remote-name> <ローカルブランチ名>
```

既存のローカルブランチが旧リモートの追跡ブランチを upstream としている場合は、切替後に
新しいリモートへ設定し直す。

```powershell
git branch --set-upstream-to=<remote-name>/<リモートブランチ名> <ローカルブランチ名>
```

新しいリモートに対象ブランチがまだない場合は、上記の `git push -u` が push と upstream の
設定を同時に行う。

### 3. `Repository not found` の切り分けと復旧

次の順に確認する。

```powershell
# 1. 設定値を確認する
git remote -v
git remote get-url <remote-name>

# 2. 読み取り接続を確認する
git ls-remote <remote-name>
```

- 事実: `git ls-remote <remote-name>` が `Repository not found` なら、GitHub はそのURLへの
  アクセスを許可していない。
- 確認: ブラウザーで `https://github.com/OWNER/REPOSITORY` を開き、意図した所有者・リポジトリ名
  で作成済みか確認する。自分の非公開リポジトリなら、Git Credential Manager の認証アカウントが
  そのリポジトリにアクセスできるアカウントであることも確認する。ブラウザーで確認するときは、
  Git接続用の末尾 `.git` を除いたURLを使う。
- 判断: 新URLが未作成または権限不足で、元の接続先で作業を継続する場合は、成功を確認済みの旧URLへ
  直ちに戻す。新しいGitHubアカウントへ移行する目的なら、先にそのアカウントで空のリポジトリを作成し、
  認証を済ませてから再設定する。

```powershell
# 旧URLへ戻す例
git remote set-url <remote-name> https://github.com/OLD-OWNER/REPOSITORY.git
git ls-remote <remote-name>
```

### 4. 古い接続先を残して併用する

移行中などで旧リモートも保持したい場合は、既存のリモートを変更せず、新しいリモートを
追加する。

```powershell
git remote add new-origin https://github.com/OWNER/NEW-REPOSITORY.git
git remote -v
git ls-remote new-origin
git push -u new-origin <ローカルブランチ名>
```

必要に応じて、名前を付け替えて新しい接続先を `origin` にできる。これは、リモート名を
標準的な `origin` に統一したい場合だけ行う。

```powershell
git remote rename origin old-origin
git remote rename new-origin origin
git remote -v
```

不要になった旧リモートを削除する場合は、接続先と upstream 設定を確認してから実行する。
削除すると、そのリモートの設定とリモート追跡ブランチが削除される。

```powershell
git remote remove old-origin
```

### 5. fetch と push の接続先を分ける場合

`git remote set-url --push origin <push用URL>` は push URL だけを変更できる。
ただし Git の公式仕様では、同一リモートに設定する fetch URL と push URL は同じ場所を指す
べきとされる。上流を fetch し、自分のフォークへ push する用途では、`upstream` と `origin`
のように別々のリモートを作成する。

```powershell
git remote add upstream https://github.com/ORIGINAL-OWNER/REPOSITORY.git
git remote set-url origin https://github.com/MY-ACCOUNT/REPOSITORY.git
git fetch upstream
git push origin <ローカルブランチ名>
```

### 注意点

- HTTPS から SSH へ変更するには、SSH 公開鍵をホスティングサービス側へ登録し、SSH 接続を
  利用できる状態にしておく。HTTPS では、サービスに応じてパスワードではなくトークンや
  credential helper が必要になる。
- `set-url` はリモート名を変更しないため、普段の `git pull` や `git push` が向かう先を
  確認してから実行する。
- 切替先に既存履歴と異なるブランチがある場合、push が拒否されることがある。強制 push は
  他者の履歴を失わせ得るため、履歴とブランチ保護を確認するまで使用しない。
- 旧リモートの追跡ブランチ表示が残った場合は、切替先を fetch して内容を確認した後に
  `git remote prune <リモート名>` を検討する。これは古いリモート追跡参照を削除する操作である。

## 参考資料

- [Git - git-remote Documentation](https://git-scm.com/docs/git-remote)
  - `set-url`、`add`、`rename`、`remove`、`prune` の公式仕様
  - 参照日: 2026-09-08
- [Managing remote repositories - GitHub Docs](https://docs.github.com/en/get-started/git-basics/managing-remote-repositories)
  - リモートの追加、URL変更、名前変更、削除の公式手順
  - 参照日: 2026-09-08
- [Git - git-branch Documentation](https://git-scm.com/docs/git-branch)
  - ブランチの upstream 表示と設定に関する公式仕様
  - 参照日: 2026-09-08

## 更新履歴

- 2026-09-08: GitHub のブラウザー表示でも `Page not found` となるURLの確認方法を追記
- 2026-09-08: `Repository not found` の原因、リモート名とブランチ名の違い、旧URLへの復旧手順を追記
- 2026-09-08: 初版を作成
