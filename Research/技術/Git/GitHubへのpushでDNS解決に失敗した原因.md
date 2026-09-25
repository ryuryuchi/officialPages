---
作成日: 2026-08-25
更新日: 2026-08-31
タグ:
  - Git
  - GitHub
  - DNS
  - push
状態: 完了
---

# GitHubへのpushでDNS解決に失敗した原因

## 概要

`git push` 実行時に `Could not resolve host: github.com` が発生した事象について、
GitHub の接続先、DNS、HTTPS、プロキシ設定を確認し、原因の範囲を整理する。

## 結論

障害時のエラーは、Git の HTTPS 通信が始まる前に `github.com` の IP アドレスを
名前解決できなかったことを示す。このため、その時点では DNS リゾルバー、ネットワーク
接続、または一時的な名前解決経路に問題があった。

2026-08-25の再確認では `github.com` がIPv4アドレス `20.27.177.113` に解決され、
HTTPSの応答、`git ls-remote`、`git push` が成功した。2026-08-31にも同じIPv4アドレス
への名前解決とHTTPSの`200`応答を確認し、Gitのプロキシ設定はなく、WinHTTPも直接接続
だった。したがって、リモートURL、リポジトリ、恒久的なプロキシ設定が原因であった
証拠はなく、**一時的なDNS名前解決失敗**と判断する。

ただし、障害発生時のDNS応答やネットワークログは残っていないため、端末、VPN、
組織ネットワーク、ISP、DNSリゾルバーのどこで失敗したかは特定できない。現在の
`github.com`のIPアドレスも恒久値ではなく、GitHubはIP範囲を変更し得るとしているため、
固定値として設定しない。

## 詳細

### 失敗時に分かること

失敗した Git のメッセージは次のとおりであった。

```text
fatal: unable to access 'https://github.com/ryuryuchi/Research.git/':
Could not resolve host: github.com
```

これは認証失敗、リポジトリ不存在、書き込み権限不足ではなく、ホスト名を IP アドレスへ
変換する DNS の段階で失敗したことを示す。HTTP 接続や GitHub の認証より前の段階なので、
このメッセージだけから GitHub 側の障害とは断定できない。

### 再確認時の観測結果

2026-08-25と2026-08-31に再確認した結果は次のとおり。

| 確認項目 | 結果 | 判断 |
| --- | --- | --- |
| `Resolve-DnsName github.com -Type A -DnsOnly` | 両日とも`20.27.177.113`を返した | DNSは再び応答している |
| `Resolve-DnsName github.com -Type AAAA -DnsOnly` | 2026-08-31はAAAA応答なし | IPv6レコードがなくてもIPv4で接続可能 |
| `curl.exe -I https://github.com` | 両日とも`200` | TLS/HTTPSでGitHubに到達できる |
| `git config --show-origin --get-regexp ...proxy` | 両日とも設定なし | Git固有のプロキシ設定は検出されない |
| `netsh winhttp show proxy` | 両日とも直接接続 | WinHTTPの明示プロキシはない |
| `git ls-remote` | 2026-08-25に成功 | 当日のGitリモート読み取りができた |
| `git push` | 2026-08-25に`Everything up-to-date` | 当日の書き込み経路も利用できた |

これらは再確認時の状態であり、失敗時の DNS 応答を復元するものではない。
GitHub Statusの公開履歴もGitHub側の障害を調べる手掛かりになるが、DNSエラーだけで
GitHub側の障害とは判断できない。

### 再発時の確認順序

再発した場合は、push を繰り返す前に次を確認する。

1. `Resolve-DnsName github.com -Type A -DnsOnly` を実行し、DNS応答、使用したDNS
   サーバー、時刻、エラーを保存する。必要なら`-Server`で組織指定のDNSと別の
   許可済みDNSを比較する。
2. `curl.exe -I https://github.com` を実行し、DNS 後の HTTPS 到達性を確認する。
3. `git config --show-origin --get-regexp "^(http|https)\..*proxy$|^remote\..*\.proxy$"` と
   `netsh winhttp show proxy` でプロキシ設定を確認する。
4. DNSだけが失敗する場合は、他のドメインも失敗するか、VPN・社内ネットワーク・
   ファイアウォール・名前解決キャッシュ・DNSサーバーの状態を確認する。DNSサーバーを
   恒久的に変更する前に、組織の
   ネットワーク方針を確認する。
5. DNS と HTTPS が成功してから `git ls-remote`、続いて `git push` を実行する。

GitHub公式資料では、接続問題の主因としてファイアウォール、プロキシ、組織ネットワーク
なども挙げている。またGitHubのIPアドレス一覧はMeta APIで取得できるが、完全な一覧では
なく変更もあるため、単一IPの固定登録は避ける。

## 参考資料

- [Git - git-config Documentation](https://git-scm.com/docs/git-config)
  - HTTP プロキシを含む Git 設定の確認方法
  - 参照日: 2026-08-31
- [Resolve-DnsName](https://learn.microsoft.com/ja-jp/powershell/module/dnsclient/resolve-dnsname)
  - Windows PowerShell で DNS 名前解決を確認するコマンドレット
  - 参照日: 2026-08-31
- [GitHub Status](https://www.githubstatus.com/)
  - GitHub サービスの稼働状況を確認する公式ステータスページ
  - 参照日: 2026-08-31
- [Troubleshooting connectivity problems - GitHub Docs](https://docs.github.com/en/get-started/using-github/troubleshooting-connectivity-problems)
  - 接続問題で確認すべきファイアウォール、プロキシ、組織ネットワークの公式案内
  - 参照日: 2026-08-31
- [About GitHub's IP addresses - GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses)
  - GitHubのIP範囲が変更され得ることとMeta APIの制約
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、DNS・HTTPS・プロキシを再検証。IP固定を避ける注意とGitHub公式の接続切り分けを追加
- 2026-08-25: 初版を作成
