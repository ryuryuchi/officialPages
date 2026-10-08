---
作成日: 2026-10-06
更新日: 2026-10-08
タグ:
  - GitHub Copilot
  - VS Code
  - 進捗表示
状態: 完了
---

# VS Code Copilotの思考中メッセージの仕組み

## 概要

VS CodeのCopilot Chatで処理中に表示される「ハムスターに賄賂を渡しています」のような文言について、生成元と選ばれ方を公式ソースコードから調べた。

## 結論

- Copilotの処理中に出る文言を日本語にするには、VS Codeの設定 `chat.agent.thinking.phrases` を使い、`mode` を `replace` にして日本語の文言を指定する。
- VS Codeの表示言語を日本語にする設定とは別である。表示言語はメニューなどのUIを切り替えるが、処理中の文言を確実に日本語へ統一するには独自フレーズを設定する。
- この文言はCopilotのAIモデルがその場で考えて出力した文章ではなく、VS Codeの画面側にあらかじめ用意された表示用メッセージである。
- 英語のソース文字列は `Bribing the hamster`。VS Codeのソースコードでは、こうした文言を「Easter-egg loading messages」と明記している。
- 表示するかどうかは処理中の表示を更新する際に抽選で決まり、通常は約50回に1回の割合でイースターエッグ文言を選ぶ。表示する場合は、登録済みの複数の文言からランダムに1つ選ぶ。
- ハムスターという比喩を選んだ個別の由来や作成者は、確認した公式ソースでは説明されていない。

## 詳細

### 文言の出どころ

VS Codeのチャット表示コードには `funWorkingMessages` という配列があり、処理中のイースターエッグ文言が文字列として定義されている。調査時点のソースには一般向け10件、Minecraft関連3件、Microsoft関連1件の計14件が登録されていた。

各文言はローカライズ用の関数を通して表示されるため、英語のソース文字列が日本語UIでは翻訳された形で見えることがある。

### イースターエッグ文言一覧

次の表は調査時点のソースコードに定義されていた一覧である。「意味の目安」は英語の文言を説明するための意訳であり、実際の日本語UI表示と一致するとは限らない。

| 分類 | 英語のソース文言 | 意味の目安（意訳） |
| --- | --- | --- |
| 一般 | `Bribing the hamster` | ハムスターに賄賂を渡しています |
| 一般 | `Reticulating splines` | スプラインを調整しています |
| 一般 | `Untangling the spaghetti` | スパゲッティをほどいています |
| 一般 | `Communing with the codebase` | コードベースと交信しています |
| 一般 | `Letting it cook` | じっくり仕上げています |
| 一般 | `Thanking all the fish` | 魚たちに感謝しています |
| 一般 | `Stabilizing the wormhole` | ワームホールを安定させています |
| 一般 | `Baking the ideas` | アイデアを焼き上げています |
| 一般 | `Consulting the oracle` | 神託に相談しています |
| 一般 | `Stirring the solution` | 解決策をかき混ぜています |
| Minecraft | `Mining diamonds` | ダイヤモンドを採掘しています |
| Minecraft | `Digging straight down` | 真下に掘っています |
| Minecraft | `Mining at night` | 夜に採掘しています |
| Microsoft | `Summoning Clippy` | Clippyを呼び出しています |

### 表示の決まり方

ソースコードの `maybePickFunWorkingMessage` は乱数を使い、`FUN_WORKING_MESSAGE_RATE = 50` に対して1回の抽選が当たったときだけ、配列から文言を1つ返す。したがって「常にハムスターの処理をしている」という意味ではなく、待ち時間に表示する遊び心のある表示である。

この抽選は処理状況の更新ごとに呼び出されるため、「1セッションにつき50回に1回」や「処理時間の2%」という意味ではない。表示頻度は処理中表示の更新回数にも左右される。

### 処理中の文言を日本語にする

1. VS Codeで `Ctrl+Shift+P` を押し、`User Settings (JSON)` を開くコマンドを実行する。英語UIでのコマンド名は `Preferences: Open User Settings (JSON)`。
2. 次の設定を追加して保存する。既に設定がある場合は、既存のJSONにプロパティを追加する。

```json
"chat.agent.thinking.phrases": {
  "mode": "replace",
  "phrases": [
    "考え中です",
    "回答を組み立てています",
    "必要な情報を確認しています"
  ]
}
```

`mode` は `replace`（既定のフレーズを置き換える）または `append`（既定のフレーズに追加する）を指定する。日本語だけを表示したい場合は `replace` にする。`append` では既定の英語フレーズも引き続き選ばれる。

この設定はVS Code 1.110（2026年2月リリース）で案内された。設定項目が見つからない場合は、VS Codeを更新する。

この設定は、考え中の表示のほか、作業中、ターミナル、ツール操作中のローディング文言を対象とする。設定できるのは画面に出る進捗用メッセージであり、モデルの内部推論や回答内容を翻訳・表示する設定ではない。

VS Codeのメニューなども日本語にしたい場合は、コマンドパレットから `Configure Display Language` を実行し、日本語 (`ja`) を選ぶ。必要な言語パックがなければインストール後、再起動する。これはUIの表示言語を切り替える設定であり、上記の独自フレーズ設定とは別である。

### 表示文言のカスタマイズ

独自フレーズは複数登録でき、処理中にその中から表示される。既定のイースターエッグ文言も含めて独自文言に置き換えたい場合は `replace`、既定文言を残して候補を増やしたい場合は `append` を使う。

### 分かっていることと分からないこと

「イースターエッグ」であること、文言がVS CodeのUIコードに定義されていること、乱数で選ばれることはソースコードで確認できる。一方、「なぜハムスターに賄賂を渡す表現にしたのか」や、誰が最初に考案したかまでは、確認した公式情報からは特定できない。

## 参考資料

- [VS Code: chatThinkingContentPart.ts（メッセージ一覧と抽選処理）](https://github.com/microsoft/vscode/blob/62d758930fb1642067e32d745ab961a471b1d27a/src/vs/workbench/contrib/chat/browser/widget/chatContentParts/chatThinkingContentPart.ts#L269-L320)
  - 参照日: 2026-10-06
- [VS Code: chatProgressContentPart.ts（処理中表示での呼び出し）](https://github.com/microsoft/vscode/blob/62d758930fb1642067e32d745ab961a471b1d27a/src/vs/workbench/contrib/chat/browser/widget/chatContentParts/chatProgressContentPart.ts)
  - 参照日: 2026-10-06
- [Custom thinking phrases - Visual Studio Code February 2026 Release Notes](https://code.visualstudio.com/updates/v1_110)
  - 推論中やツール呼び出し中に表示するローディング文言をカスタマイズできる機能を案内
  - 参照日: 2026-10-07
- [VS Code Copilot extension CHANGELOG](https://github.com/microsoft/vscode/blob/main/extensions/copilot/CHANGELOG.md)
  - `chat.agent.thinking.phrases` によるローディング文言のカスタマイズを案内
  - 参照日: 2026-10-07
- [VS Code: chat.shared.contribution.ts（chat.agent.thinking.phrases設定の定義）](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/browser/chat.shared.contribution.ts)
  - `mode` の `replace` / `append` と、独自フレーズの設定を定義
  - 参照日: 2026-10-07
- [Display Language - Visual Studio Code](https://code.visualstudio.com/docs/configure/locales)
  - `Configure Display Language` コマンドと日本語 (`ja`) の選択方法を案内
  - 参照日: 2026-10-07

## 更新履歴

- 2026-10-08: yomiyasuの原則に基づき本文を推敲

- 2026-10-07: `chat.agent.thinking.phrases` を使った日本語化手順と、表示言語設定との違いを追記
- 2026-10-06: ソースコードにあるイースターエッグ文言14件を分類・意訳付きの表に追加
- 2026-10-06: 初版を作成
