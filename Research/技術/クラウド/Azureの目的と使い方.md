---
作成日: 2026-09-10
更新日: 2026-09-10
タグ:
  - Azure
  - クラウド
  - クラウドコンピューティング
  - Bicep
  - Azure CLI
状態: 完了
---

# Azureの目的と使い方

## 概要

Microsoft Azureが何のために作られ、何に使われるサービスなのかを整理する。
Azure自体をプログラミング言語と誤解しやすいため、利用できる代表的な言語と、
Azureのリソースを操作・定義する構文も区別して説明する。

## 結論

Azureは、Microsoftが提供する**クラウドコンピューティング基盤**である。
データセンターのサーバー、ストレージ、ネットワーク、データベース、AIなどを
必要な分だけ利用し、アプリケーションを開発、公開、運用するために作られた。

Azureはプログラミング言語ではない。そのため「有名な言語で何に似ているか」に
対する答えは、対象によって異なる。

- Azure上のアプリは、Python、JavaScript/TypeScript、Java、C#などで作れる。
- Azure CLIは、BashやPowerShellから実行するコマンドラインツールに近い。
- Azure PowerShellは、PowerShellのコマンドレットを使う管理ツールである。
- ARMテンプレートはJSON形式の宣言的な構成ファイルである。
- BicepはAzureリソースを宣言的に記述する、Azure Resource Manager用のDSLである。
  一般的な命令型言語より、TerraformなどのIaC（Infrastructure as Code）記述に近い。

## 詳細

### 何のために作られたか

Azureの目的は、利用者が自分で物理サーバーやデータセンターを用意せずに、
コンピューティング資源や各種マネージドサービスを使えるようにすることである。
代表的な効果は次のとおり。

- 必要なときに仮想マシンやアプリ実行環境を作成・削除できる。
- 利用量や負荷に応じて、計算資源や保存容量を増減しやすい。
- 複数の地域にアプリやデータを配置し、可用性や利用地域を考慮した構成を作れる。
- OS更新、バックアップ、データベース運用などの一部をマネージドサービスに任せられる。
- 認証、監視、ネットワーク、セキュリティ、AIなどを組み合わせてシステムを構築できる。

ただし、可用性、セキュリティ、コスト、データ所在地が自動的に最適化されるわけではない。
サービスの選択、権限設計、監視、バックアップ、料金管理は利用者の責任範囲として
検討が必要である。

### 何に使うか

| 分野 | Azureで使う代表例 | 用途 |
| --- | --- | --- |
| アプリ実行 | Virtual Machines、App Service、Azure Functions、コンテナー | Webアプリ、API、バッチ、イベント処理 |
| 保存 | Blob Storage、Disk Storage、Azure Files | ファイル、画像、バックアップ、仮想ディスク |
| データベース | Azure SQL Database、Cosmos DBなど | リレーショナルデータ、NoSQLデータ |
| ネットワーク | Virtual Network、Load Balancer、各種接続サービス | 通信経路の分離、負荷分散、拠点接続 |
| 分析とAI | 分析サービス、AzureのAI関連サービス | データ分析、機械学習、生成AIアプリ |
| 運用 | Azure Monitor、Microsoft Entra ID、Resource Manager | 監視、認証・認可、リソース管理 |

例えば、会社のWebシステムなら、App ServiceでWeb/APIを動かし、Azure SQL
Databaseに業務データを保存し、Blob Storageに画像を置き、Microsoft Entra IDで
利用者を認証する、といった構成にできる。

### Azureはどの言語に似ているか

Azure全体に対応する「似たプログラミング言語」はない。比較対象は操作方法や
構成定義の種類ごとに考える必要がある。

| 対象 | 似ているもの | 説明 |
| --- | --- | --- |
| Azure CLI | Bash、PowerShell、cmdのコマンド実行 | `az`から始まるコマンドを端末やスクリプトで実行する |
| Azure PowerShell | PowerShell | `New-AzResourceGroup`のような動詞-名詞型のコマンドレットを使う |
| ARMテンプレート | JSON、宣言的な設定ファイル | 作りたいリソースと設定をJSONで記述する |
| Bicep | IaC用DSL、Terraformの記述 | リソースの状態を宣言し、Azure Resource Managerへデプロイする |
| Azure SDK | 利用する言語そのもの | PythonならPython、C#ならC#の文法でAzure APIを呼び出す |

したがって、アプリケーション開発者は既存の得意な言語を使い、インフラ管理者は
CLI、PowerShell、Bicep、ARMテンプレートなどを選ぶ、という使い分けが基本になる。
Microsoftの開発者向け資料では、.NET、Python、JavaScript、Java、Go、C++、Rustの
SDKや開発者向け資料が案内されている。

### 代表的な構文

#### Azure CLI

Azure CLIは端末からAzureリソースを操作するコマンドラインツールである。基本形は
「参照名 - コマンド - パラメーター - 値」で、シェルの文法（変数、パイプ、条件分岐
など）は実行するBashやPowerShellに従う。

```bash
az login
az group create --name myResourceGroup --location japaneast
az account list --output table
```

`az`の後に操作対象（`group`など）、操作（`create`など）、オプションを並べる。
JSONが標準出力形式で、`--output table`のように形式を変更できる。

#### Azure PowerShell

Azure PowerShellはPowerShellからAzureを操作するためのモジュールである。
PowerShellのパイプやオブジェクト処理を使える。

```powershell
Connect-AzAccount
New-AzResourceGroup -Name myResourceGroup -Location japaneast
Get-AzResourceGroup
```

#### Bicep

BicepはAzureリソースを宣言するDSLで、BicepファイルをAzure Resource Managerへ
デプロイする。変数、パラメーター、リソース、モジュール、出力などを記述できる。
命令を上から実行するというより、最終的に必要なリソースの状態を表す。

```bicep
param location string = resourceGroup().location

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'examplestorage12345'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}
```

リソース名、リソースの種類とAPIバージョン、リージョン、SKUなどを記述する。
実際に利用するAPIバージョン、名前の制約、リージョンでの提供状況は対象サービスの
公式ドキュメントで確認する必要がある。

#### ARMテンプレート

ARMテンプレートは、Azure Resource Managerが解釈するJSON形式のテンプレートである。
`parameters`、`variables`、`resources`、`outputs`などを使って、再利用可能な
デプロイ定義を作れる。BicepはARMテンプレートJSONより簡潔に書け、デプロイ時には
ARMテンプレートに変換される。

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": []
}
```

空の`resources`は例示用であり、実運用では対象リソースの種類、APIバージョン、
名前、場所、プロパティなどを定義する。

## 参考資料

- [What is Azure? - Microsoft Azure](https://azure.microsoft.com/en-us/resources/cloud-computing-dictionary/what-is-azure)
  - 参照日: 2026-09-10
- [Azure developer documentation - Microsoft Learn](https://learn.microsoft.com/en-us/azure/developer/)
  - 参照日: 2026-09-10
- [What is the Azure CLI? - Microsoft Learn](https://learn.microsoft.com/en-us/cli/azure/what-is-azure-cli)
  - 参照日: 2026-09-10
- [What is Azure Resource Manager? - Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)
  - 参照日: 2026-09-10
- [What is Bicep? - Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview)
  - 参照日: 2026-09-10
- [Templates overview - Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/overview)
  - 参照日: 2026-09-10

## 更新履歴

- 2026-09-10: Azureの目的、用途、対応言語、Azure CLI・PowerShell・Bicep・ARMテンプレートの構文を初版作成
