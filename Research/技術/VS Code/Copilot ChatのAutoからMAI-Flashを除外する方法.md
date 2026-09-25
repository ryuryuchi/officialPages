---
作成日: 2026-08-27
更新日: 2026-08-31
タグ:
  - VS Code
  - GitHub Copilot
  - Copilot Chat
  - AIモデル
  - MAI-Flash
状態: 完了
---

# Copilot ChatのAutoからMAI-Flashを除外する方法

## 概要

VS Code の GitHub Copilot Chat でモデルを `Auto` にした場合、Microsoft の
MAI-Code-1-Flash または MAI-Code-1.1-Flash（以下、MAI-Flash）を選択対象から
除外できるかを調査した。

## 結論

**個人ユーザーが VS Code の設定画面や `settings.json` で、Auto の候補から
MAI-Flash だけを除外する設定はない。**

Copilot Business または Copilot Enterprise では、組織または Enterprise の管理者が
GitHub のモデルアクセス設定で MAI-Flash を **Disabled** にできる。Auto は管理者
ポリシーで除外されたモデルを選ばないため、この方法で除外できる。

管理者権限がない個人利用では、MAI-Flash を避けるには `Auto` を使わず、利用可能な
別のモデルをモデルピッカーで明示的に選ぶ。Copilot Free と Copilot Student は
Auto モデル選択のみを利用できるため、この回避策は使えない。

## 詳細

### Autoの選択対象

事実として、Copilot Chat の Auto は、タスクの複雑さ、モデルの稼働状況・可用性、
プラン、およびポリシーを基にモデルを選ぶ。Auto の候補は固定ではなく、利用可能な
モデルは変更され得る。

2026-08-31 時点の GitHub 公式の対応モデル一覧では、MAI-Code-1-Flash と
MAI-Code-1.1-Flash はいずれも GA の Copilot モデルである。また、公式の
Auto モデル選択テーブルでは MAI-Code-1.1-Flash が Copilot Chat の対象に
含まれている。

Auto は次のモデルを選ばない。

- 利用中の Copilot プランで使えないモデル
- 管理者ポリシーで除外されたモデル
- データレジデンシーまたは FedRAMP 準拠ポリシーで除外されたモデル
- 評価モデルを制限するポリシーで除外されたモデル

個人プランで利用者が無効化できると公式に案内されているのは「評価モデル」のみで
ある。MAI-Flash は GA モデルであり、この評価モデルの無効化機能の対象ではない。
したがって、評価モデルの設定を使って MAI-Flash を除外できるとは判断できない。

### 組織・Enterpriseで除外する手順

組織または Enterprise の所有者は、GitHub.com の Copilot モデル設定で
MAI-Code-1-Flash と MAI-Code-1.1-Flash を無効化できる。組織で操作する場合は、
次の手順である。

1. GitHub.com で対象組織を開き、**Settings** を開く。
2. **Code, planning, and automation** の **Copilot** を開く。
3. **Models** を開く。
4. 対象の MAI-Flash モデルのドロップダウンで **Disabled** を選ぶ。

Enterprise に属する組織では、Enterprise 所有者がモデル設定を強制している場合が
ある。この場合、組織側で変更できないため、Enterprise 所有者に無効化を依頼する。

### 個人利用での選択肢

Copilot Pro、Pro+など、モデルを手動選択できる有料個人プランでは、チャット入力欄の
モデルピッカーで `Auto` 以外のモデルを選ぶ。これは MAI-Flash を Auto の候補から
除外する設定ではなく、そのチャットで Auto による自動選択を使わない運用である。

Copilot Free と Copilot Student は公式に Auto モデル選択のみを利用可能とされる。
そのため、これらのプランでは MAI-Flash だけを避けながら Auto を使い続ける利用者
側の設定手段はない。

## 参考資料

- [About Copilot auto model selection - GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)
  - 参照日: 2026-08-31
- [Configuring access to AI models in GitHub Copilot - GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-access-to-ai-models)
  - 参照日: 2026-08-31
- [Managing the availability of models in an organization - GitHub Docs](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-default-models)
  - 参照日: 2026-08-31
- [Supported AI models in GitHub Copilot - GitHub Docs](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
  - 参照日: 2026-08-31
- [Language models - Visual Studio Code](https://code.visualstudio.com/docs/agents/concepts/language-models)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLとモデル一覧、Auto対象、プラン制約、組織のモデル管理手順を
  再確認し、現行の有料個人プラン表記へ修正
- 2026-08-27: 初版を作成
