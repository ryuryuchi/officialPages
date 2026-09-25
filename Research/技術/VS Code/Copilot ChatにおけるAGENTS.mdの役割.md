---
作成日: 2026-08-26
更新日: 2026-08-31
タグ:
  - VS Code
  - GitHub Copilot
  - Copilot Chat
  - AGENTS.md
状態: 完了
---

# Copilot ChatにおけるAGENTS.mdの役割

## 概要

VS Code の GitHub Copilot Chat が `AGENTS.md` をどのように扱うのか、用途、適用範囲、他のカスタム指示ファイルとの違い、利用時の注意点を調査した。

## 結論

`AGENTS.md` は、AI コーディングエージェントへプロジェクト固有の作業方法を伝えるための Markdown ファイルである。「エージェント向けの README」と考えると分かりやすい。ビルド・テスト手順、コーディング規約、構成上の制約、変更後の確認項目などを記載すると、同じ説明をチャットごとに繰り返さずに済む。

VS Code はワークスペースのルートにある `AGENTS.md` を検出し、その内容をワークスペース内のすべてのチャット要求へ自動的に加える。対応は既定で有効であり、`chat.useAgentsMdFile` で切り替えられる。これは Copilot Chat の応答やエージェント作業を誘導する指示であり、ルールを機械的に強制する仕組みではない。

複数の AI エージェントで同じ指示を共有したい場合は `AGENTS.md` が適している。Copilot 専用の全体指示だけでよければ `.github/copilot-instructions.md`、ファイルやフォルダーごとに明確な条件を指定したければ `.github/instructions/*.instructions.md` も選択肢になる。

## 詳細

### 基本的な役割

`AGENTS.md` は、公開されたシンプルな共通形式であり、特定製品だけに閉じた設定ファイルではない。一般の README が主に人間へプロジェクトを説明するのに対し、`AGENTS.md` はコーディングエージェントへ、作業時に守るべき情報を予測可能な場所で提供する。

VS Code の公式ドキュメントでは、ルートの `AGENTS.md` は「常時適用される指示」に分類される。Copilot Chat はファイルを単に参考資料として表示するのではなく、その内容をチャットのコンテキストへ追加して応答生成に利用する。

適した内容は次のとおりである。

- セットアップ、ビルド、テスト、lint、型チェックの正しいコマンドと実行順序
- 採用技術、主要ディレクトリ、アーキテクチャ上の境界
- 命名、書式、エラー処理、依存関係の追加などに関する規約
- 変更してはいけないファイルや、避けるべき実装方法
- 変更後に必ず実施する検証と、作業の完了条件

指示は自然言語の Markdown で記載できる。曖昧な理念よりも、実際に検証したコマンド、具体的なパス、明確な禁止事項を短く記載する方が有効である。

### VS Codeでの適用範囲

ワークスペースのルートに置いた `AGENTS.md` は、そのワークスペース内のすべてのチャット要求へ自動適用される。設定は次の2つである。

| 設定 | 役割 |
| --- | --- |
| `chat.useAgentsMdFile` | `AGENTS.md` 対応全体の有効・無効を切り替える。対応は既定で有効 |
| `chat.useNestedAgentsMdFiles` | サブフォルダー内の複数の `AGENTS.md` を利用する実験的機能を切り替える |

ネストした `AGENTS.md` の対応は、2026年8月31日時点でも実験的であり、既定では
無効である。有効にすると、VS Code はワークスペースのサブフォルダーを再帰的に
検索し、見つけた各ファイルと相対パスをチャットのコンテキストへ追加する。
その後、エージェントが編集中のファイルに応じて利用する指示を判断する。

GitHub の一般向けドキュメントには「ディレクトリツリー内で最も近い `AGENTS.md` が優先される」とある。一方、VS Code のドキュメントは、ネスト版について「相対パスをコンテキストへ加え、エージェントが使用する指示を判断する」と説明している。また、複数の指示ファイルを結合する場合の順序は保証されない。したがって、VS Code では親子の指示に矛盾を作らず、「近いファイルが必ず機械的に上書きする」とは想定しない方が安全である。

### 他のカスタム指示との違い

| ファイル | 主な用途 | 適用方法 |
| --- | --- | --- |
| `AGENTS.md` | 複数の AI コーディングエージェントで共有できるプロジェクト指示 | ルート版は全チャット要求。ネスト版は実験的 |
| `.github/copilot-instructions.md` | GitHub Copilot 向けのプロジェクト全体指示 | 全チャット要求へ常時適用 |
| `.github/instructions/NAME.instructions.md` | 言語、ファイル種別、フォルダー、タスク別の指示 | `applyTo`のglobまたは説明との意味的な一致に基づき適用 |
| `CLAUDE.md` | Claude系ツールとも共有する常時適用の指示 | ルート、`.claude`、ホームなどから検出 |

これらは排他的ではなく、複数が同じ要求へ同時に加えられる場合がある。VS Code は
複数ファイルの特定の結合順序を保証していないため、同じ事項を異なる表現で
重複させたり、相反する命令を書いたりしないことが重要である。
なお、Custom instructionsは入力中のインライン候補には適用されない。

選択の目安は次のとおりである。

1. 複数の AI ツールで共通利用するなら、ルートの `AGENTS.md` を基本にする。
2. Copilot だけで使う全体規約なら、`.github/copilot-instructions.md` でもよい。
3. フロントエンドとバックエンドなど適用対象を明示的に分けるなら、安定した `applyTo` を持つ `.instructions.md` を優先する。
4. モノレポでネストした `AGENTS.md` を使う場合は、実験的設定を有効にし、親子間で矛盾しないようにする。

### できることとできないこと

`AGENTS.md` により期待できる効果は、エージェントの探索量やコマンド試行錯誤を減らし、生成コードと検証手順をプロジェクトの方針へ近づけることである。

ただし、次の点には注意が必要である。

- 指示は言語モデルへのコンテキストであり、アクセス制御、ポリシーエンジン、CI の代替ではない。
- 指示に書いただけでコマンドやテストが自動実行されるわけではない。
- 内容が長すぎる、曖昧、古い、または他の指示と矛盾する場合は、応答品質が下がり得る。
- VS Code 公式資料が保証している対象はチャット要求であり、通常のインラインコード補完へ同じように適用されるとは限らない。

重要な制約は、CI、lint、型チェック、権限設定などでも別途強制する必要がある。`AGENTS.md` は、それらをエージェントが正しく実行するための案内として使う。

### 最小例

```markdown
# Project instructions

## Setup
- Use Node.js 22 and run `npm ci` before the first build.

## Implementation
- Keep domain logic under `src/domain`.
- Do not import database adapters from domain modules.

## Validation
- Run `npm run lint`, `npm run typecheck`, and `npm test` after changes.
- Do not report completion while any of these commands fail.
```

実際のファイルには、そのリポジトリで確認済みの内容だけを記載し、コマンドや構成が変わった際に更新する。

## 参考資料

- [Use custom instructions in VS Code - Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
  - 参照日: 2026-08-31
- [Adding repository custom instructions for GitHub Copilot in your IDE - GitHub Docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide)
  - 参照日: 2026-08-31
- [Adding repository custom instructions for GitHub Copilot - GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
  - 参照日: 2026-08-31
- [AGENTS.md - agentsmd/agents.md](https://github.com/agentsmd/agents.md)
  - 参照日: 2026-08-31
- [VS Code Copilot extension CHANGELOG - microsoft/vscode](https://github.com/microsoft/vscode/blob/main/extensions/copilot/CHANGELOG.md)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、ネスト対応が引き続き実験的であること、
  `CLAUDE.md`対応、インライン候補への非適用を反映
- 2026-08-26: 初版を作成
