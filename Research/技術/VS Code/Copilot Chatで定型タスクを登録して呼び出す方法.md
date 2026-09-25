---
作成日: 2026-08-31
更新日: 2026-09-25
タグ:
  - VS Code
  - GitHub Copilot
  - Prompt files
  - Agent Skills
  - Automation
状態: 完了
---

# Copilot Chatで定型タスクを登録して呼び出す方法

## 概要

VS Code の GitHub Copilot に定型タスクを保存して実行する方法を調査した。
Prompt files や Agent Skills による手動実行と、Agents window の Automations による
定期実行を区別し、Custom agents やカスタム指示との使い分けも整理する。

## 結論

Agents window の **Automations** から、保存したプロンプトを手動または時間指定で
エージェントに実行させられる。毎時・毎日・毎週の定期実行ができるため、
繰り返し行う変更要約、Issue のトリアージ、バグ候補の確認などに使える。
イベント発生時に起動する汎用トリガーではなく、指定したスケジュールで
エージェントセッションを開始する機能である。

チャットから定型タスクを名前で呼び出す最も直接的な機能は、**Prompt files**
（プロンプトファイル、カスタムスラッシュコマンド）である。
`.prompt.md` ファイルへ手順を保存し、Copilot Chat で
`/ファイル名` または front matter の `name` を入力して実行できる。

例えば `.github/prompts/review-and-test.prompt.md` を作ると、通常は
`/review-and-test` で呼び出せる。ファイル変更やテスト実行まで任せる場合は、
front matter の `agent: agent` を指定する。

選択の目安は次のとおりである。

| やりたいこと | 適した機能 |
| --- | --- |
| Agents windowで定型プロンプトを手動・定期実行する | Agent Automations |
| 保存した1つの定型タスクを名前で実行する | Prompt file |
| 手順、スクリプト、テンプレートをまとめ、必要時の自動選択もさせる | Agent Skill |
| レビュー担当など、役割、モデル、使用可能ツールを切り替える | Custom agent |
| すべての依頼で常に守る規約を設定する | Custom instructions、`AGENTS.md` |
| 特定イベントでコマンドを必ず実行する | Hooks |

Prompt files や Agent Skills の指示はモデルが解釈して実行するため、通常の
プログラムのように毎回同一結果になる保証はない。絶対に実行させる検証や禁止処理は、
CI、権限設定、Hooks なども併用する。

ただし、Agent Host上のCopilotハーネスはPrompt filesを使用しない。現行の
Agent Host、Copilot CLI、Copilot cloud agentを対象にする場合はAgent Skillを選ぶ。
VS CodeはPrompt fileからSkillへの1回限りの移行機能も実験的に提供している。

## 詳細

### 最短の作成手順

1. VS Code で GitHub Copilot Chat を開く。
2. チャット欄に `/prompts` と入力し、Prompt files の設定画面を開く。
3. **New Prompt (Workspace)** または **New Prompt (User)** を選ぶ。
   - Workspace: 現在のリポジトリだけで使用し、チームと共有できる。
   - User: 自分の複数ワークスペースで使用できる。
4. 例として `review-and-test.prompt.md` を作成する。
5. 次のように定型手順を書く。

```markdown
---
name: review-and-test
description: 変更内容をレビューし、関連テストを実行して問題を修正する
argument-hint: "[対象ファイルまたは機能]"
agent: agent
---

対象: ${input:target:対象ファイルまたは機能を指定してください}

次の順序で作業してください。

1. 対象と関連コードを確認する。
2. バグ、型エラー、既存規約との不一致を確認する。
3. 必要な修正を行う。
4. 既存の最小範囲のテスト、lint、型チェックを実行する。
5. 変更内容と検証結果を簡潔に報告する。

無関係なファイルは変更しないでください。
テストが失敗したまま完了扱いにしないでください。
```

Workspace の既定保存先は `.github/prompts` である。手作業で作る場合は、
`.github/prompts/review-and-test.prompt.md` という配置にする。

コマンドパレットから **Chat: New Prompt File** を実行して作成する方法もある。
また、チャットで `/create-prompt` に続けて作りたいタスクを説明すると、AI に
Prompt file のひな型を生成させられる。既存の会話から「この手順を再利用可能な
prompt にして」と依頼する方法も公式に案内されている。

### 呼び出し方

Copilot Chat の入力欄で次のように入力する。

```text
/review-and-test
```

追加条件を後ろへ続けることもできる。

```text
/review-and-test src/auth のログイン処理
```

ほかに次の実行方法がある。

- コマンドパレットの **Chat: Run Prompt** から選ぶ。
- `.prompt.md` をエディターで開き、右上の再生ボタンを押す。
- チャット欄で `/` を入力し、一覧から選ぶ。

`name` を省略した場合はファイル名がコマンド名になる。`description` は一覧の説明、
`argument-hint` は入力候補、`agent` は実行するエージェントを指定する。
必要に応じて `model` や `tools` も front matter で指定できるが、利用できる
モデル名やツール名は環境に依存するため、必要になるまで省略する方が保守しやすい。

### WorkspaceとUserの選び方

| 保存先 | 既定位置 | 向いている用途 |
| --- | --- | --- |
| Workspace | `.github/prompts` | リポジトリ固有のビルド、レビュー、リリース手順をチーム共有 |
| User | VS Code のユーザープロファイル | 自分だけの汎用的な説明、要約、調査手順 |

User Prompt file は UI から作成するのが確実である。Settings Sync の
**Prompts and Instructions** を有効にすると、複数端末へ同期できる。

### Agents windowでAutomationを作成する

Agent Automation は、保存したプロンプト、セッション設定、スケジュールを組み合わせ、
エージェントの作業を繰り返し実行する機能である。Prompt fileのように毎回チャットへ
コマンドを入力しなくても、Agents windowから手動実行したり、定期実行したりできる。

1. VS Codeの設定で `chat.automations.enabled` を有効にする。
2. **Chat: Open Agents window** を開き、サイドバーの **Automations** を選ぶ。
3. **Create Automation** を選ぶ。変更の要約、Issueのトリアージ、バグ発見などの
   テンプレートから始めることもできる。
4. 名前とプロンプトを設定し、対象のWorkspace（または **No workspace**）、
   利用するAgent、Model、権限などのセッション設定を選ぶ。
5. 最初は **Manual** にして **Create** し、**Run now** で結果を確認する。
6. 問題がないことを確認してからAutomationを編集し、必要なScheduleを選んで保存する。

Scheduleは **Manual**（Run nowを押したときのみ）、**Hourly**（毎時）、
**Daily**（指定時刻に毎日）、**Weekly**（指定曜日・時刻に毎週）である。
DailyとWeeklyの時刻はローカルタイムゾーンを使う。同じAutomationの実行は一度に
1セッションであり、前の実行中に次の予定時刻が来ても並列起動しない。

例として、次のようなプロンプトを設定できる。スケジュール登録前に、対象や出力形式、
ファイル変更の可否を具体的に書く。

```text
現在のブランチで直近24時間のコミットを確認し、機能追加・修正・保守に分類して
要約してください。コミットへの参照を付け、ドキュメント更新が必要そうな変更を
指摘してください。ファイルは変更しないでください。
```

Automationsは通常のスクリプトやイベントフックと同じものではない。プロンプトを
エージェントが解釈して実行するため、結果は変動し得る。保存しただけで権限確認や
組織ポリシーを回避できるわけではなく、実行時に承認が必要になる場合がある。
エージェントの権限に応じて、ファイルの読み取り、コマンド実行、ファイル変更も
起こり得るため、特に無人の定期実行では権限と指示を確認する。

スケジュール実行には、実行するマシンが起動していてスリープしておらず、
エージェントが利用可能である必要がある。Agent Hostを使うスケジュールでは
Agent Hostプロセスが実行中であること、その他ではVS Codeウィンドウが実行中である
ことが必要であり、アプリを終了した後も動き続ける常時稼働サービスではない。
停止中に逃した予定が後からcatch-up実行されることはあるが、すべての未実行分が
必ず再実行される保証はない。実行ごとに選択したAgentとModelを使うため、
定期実行の利用量にも注意する。

Automationは `.automation.md` ファイルへエクスポートし、別環境でインポートできる。
共有ファイルに含まれるのは名前、プロンプト、スケジュールなどの移植可能な情報で、
Workspace、Provider、Model、権限、有効状態、実行履歴は含まれない。インポート側で
実行設定を選び直す。保存済みAutomationはAgents windowの **Automations** から
編集、有効・無効の切替、複製、実行履歴の確認、停止、削除ができる。

### Prompt file以外を選ぶ場合

#### Agent Skills

Agent Skill は `SKILL.md` と、任意のスクリプト、テンプレート、例を1フォルダーに
まとめる仕組みである。VS Code、Copilot CLI、Copilot cloud agentで利用できる
オープン標準であり、複数ファイルや実行用スクリプトを含む、比較的複雑で
持ち運び可能な定型処理に向く。

プロジェクト用は次のいずれかに保存する。

- `.github/skills/`
- `.claude/skills/`
- `.agents/skills/`

個人用は `~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/` に
保存できる。追加のプロジェクト内保存先は、VS Code設定
`chat.agentSkillsLocations`で指定できる。

最小構成は次のとおりである。フォルダー名と`name`は一致させる。

```text
.github/
└─ skills/
   └─ release-check/
      └─ SKILL.md
```

```markdown
---
name: release-check
description: リリース前の確認を行う。リリース準備を依頼されたときに使う。
argument-hint: "[対象バージョン]"
disable-model-invocation: true
---

# Release check

1. 変更履歴を確認する。
2. テストとビルドを実行する。
3. リリース対象の差分と未解決事項を報告する。
```

`name`と`description`は必須である。`name`は小文字、数字、ハイフンだけを使い、
最大64文字にする。`description`には「何をするか」だけでなく「いつ使うか」も
具体的に書く。名前が不正、または親フォルダー名と一致しない場合、Skillは
読み込まれない。

作成方法は次のいずれかである。

1. チャット欄で`/skills`を入力し、**Configure Skills**を開く。
2. **New Skill (Workspace)**または**New Skill (User)**を選ぶ。
3. 保存先と名前を選び、生成された`SKILL.md`へ手順を書く。

コマンドパレットの**Chat: Open Customizations**から**Skills**タブを開いてもよい。
チャットで`/create-skill`に続けて用途を説明すれば、AIにひな型を生成させられる。

呼び出すときは、チャット欄で`/`を入力して一覧から選ぶか、次のように直接入力する。

```text
/release-check v1.4.0
```

既定では、Skillはスラッシュコマンドとして手動実行でき、依頼内容と
`description`が一致するとCopilotから自動選択される。呼び出し方はfront matterで
次のように制御できる。

| 設定 | 手動呼び出し | 自動選択 | 用途 |
| --- | --- | --- | --- |
| 両方省略 | できる | される | 一般的なSkill |
| `user-invocable: false` | できない | される | 自動選択専用 |
| `disable-model-invocation: true` | できる | されない | 手動実行専用 |
| 両方を設定 | できない | されない | 実質的に無効 |

スクリプトやテンプレートを含める場合はSkillフォルダー内へ置き、`SKILL.md`から
相対リンクで明示する。参照されていない追加ファイルは自動では読み込まれない。

```text
.github/skills/release-check/
├─ SKILL.md
└─ scripts/
   └─ Test-Release.ps1
```

```markdown
必要な検証では[リリース確認スクリプト](./scripts/Test-Release.ps1)を実行する。
```

このワークスペースの実例は
`.github/skills/refresh-research-knowledge/SKILL.md`である。チャットで
`/refresh-research-knowledge`と入力するか、「全調査メモの知識を更新して」のように
`description`へ合う依頼をすると選択対象になる。このSkillは
`scripts/New-ResearchRefreshPlan.ps1`を呼び出し、メモ数に応じた分担計画を作る。

Skillが一覧へ出ない場合は、次を確認する。

1. `SKILL.md`という正確なファイル名でSkillフォルダー直下にあるか。
2. YAML front matterに`name`と`description`があるか。
3. `name`が親フォルダー名と一致し、使用可能な文字だけで構成されているか。
4. `user-invocable: false`を指定していないか。
5. 独自保存先なら`chat.agentSkillsLocations`へ登録しているか。

共有Skillは実行前に内容と同梱スクリプトを確認する。Skillが指示したコマンドも
通常の権限確認や自動承認設定の対象であり、Skill自体が承認を回避することはない。

大きなSkillでは、実験的な`context: fork`を指定すると、専用のサブエージェントで
実行し、最終結果だけを元の会話へ返せる。この機能には
`github.copilot.chat.skillTool.enabled`の有効化が必要である。

#### Custom agents

Custom agent は `.agent.md` に役割、指示、モデル、利用可能なツールを定義する。
Workspace の既定保存先は `.github/agents`、個人用は `~/.copilot/agents` である。
「定型タスクを1回実行する」というより、「読み取り専用のレビュー担当」
「実装担当」のような作業人格をチャットのエージェント選択欄から切り替える用途に向く。
Prompt file の `agent` から Custom agent 名を指定して組み合わせることもできる。

#### Custom instructionsとAGENTS.md

`.github/copilot-instructions.md` やルートの `AGENTS.md` は、原則として各チャット
要求へ自動的に加えられる。コーディング規約、使用技術、毎回の完了条件などを
覚えさせる用途には向くが、名前を入力して特定タスクを開始する機能ではない。
詳細は [Copilot ChatにおけるAGENTS.mdの役割](./Copilot%20ChatにおけるAGENTS.mdの役割.md)
を参照する。

### 注意点

- GitHub の公式資料では、Prompt files は2026年8月31日時点で Public Preview
  とされており、仕様が変わる可能性がある。
- VS Code の Agent Host 上で動くエージェントは Prompt files を使用しない。
  Agent Host や Copilot cloud agent でも再利用したい処理は Agent Skill へ
  移行する。ローカルの VS Code extension host で動くエージェントでは
  Prompt files を利用できる。
- Agent Automations はAgents windowの機能で、VS Code 1.137でPreviewとして
  導入され、1.138のリリースノートでは既定で有効になったと案内されている。
  ただし公式ガイドは段階的な提供のためStableで設定が無効な場合があるとしている。
  Automationsが見当たらない場合は、VS Codeを更新し、設定
  `chat.automations.enabled` を確認する。
- Prompt file が一覧に出ない場合は、保存先、拡張子 `.prompt.md`、YAML 構文を
  確認し、チャットメニューの **Show Agent Debug Logs** で検出エラーを確認する。
- ファイル変更やコマンド実行には Agent モードと適切な権限が必要である。
  Prompt file 自体が権限確認を回避することはない。
- パスワード、API キー、トークンなどを Prompt file や Skill に記載しない。

## 参考資料

- [Use prompt files in VS Code - Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/prompt-files)
  - 参照日: 2026-08-31
- [Your first prompt file - GitHub Docs](https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files/your-first-prompt-file)
  - 参照日: 2026-08-31
- [Agent customization - Visual Studio Code](https://code.visualstudio.com/docs/agents/concepts/customization)
  - 参照日: 2026-08-31
- [Use Agent Skills in VS Code - Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
  - 参照日: 2026-08-31
- [Custom agents in VS Code - Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-agents)
  - 参照日: 2026-08-31
- [Use custom instructions in VS Code - Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
  - 参照日: 2026-08-31
- [Hooks in Visual Studio Code](https://code.visualstudio.com/docs/agent-customization/hooks)
  - 参照日: 2026-08-31
- [Create and manage agent automations - Visual Studio Code](https://code.visualstudio.com/docs/agents/run/automations)
  - 参照日: 2026-09-25
- [Visual Studio Code 1.137 Release Notes](https://code.visualstudio.com/updates/v1_137)
  - 参照日: 2026-09-25
- [Visual Studio Code 1.138 Release Notes](https://code.visualstudio.com/updates/v1_138)
  - 参照日: 2026-09-25

## 更新履歴

- 2026-09-25: Agents windowのAutomationsについて作成方法、定期実行の範囲、
  実行条件・権限・共有方法を追記し、Prompt filesやSkillsとの使い分けを更新
- 2026-08-31: Agent Skillsの保存先、必須項目、作成・呼び出し方法、
  スクリプト参照、呼び出し制御、診断方法、ワークスペース内の実例を追記
- 2026-08-31: 全参考URLと現行仕様を再確認し、Agent HostではPrompt filesを
  使用しない制約、Skill移行、`user-invocable`、Hooks公式資料を反映
- 2026-08-31: 初版を作成
