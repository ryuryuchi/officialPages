---
作成日: 2026-09-08
更新日: 2026-09-08
タグ:
  - Groq
  - API
  - 生成AI
  - LLM
  - 音声AI
状態: 完了
---

# Groq APIの使い方と利用可能な機能

## 概要

GroqCloudのAPIを利用するためのAPIキー取得手順、最小の呼び出し方、2026-09-08時点で公式ドキュメントに掲載されている主な機能を整理する。

## 結論

Groq APIは、`https://api.groq.com/openai/v1` をベースURLとするOpenAI互換APIである。Groq Consoleでプロジェクトを選択してAPIキーを生成し、キーを`GROQ_API_KEY`環境変数に保存してから、公式のPython/JavaScript SDK、OpenAI SDK、またはHTTPで呼び出す。

基本用途はテキスト生成だが、対応モデルを選べば画像理解、音声文字起こし・英訳、音声合成、関数呼び出し、JSON Schemaに従う構造化出力、組み込みツールを用いるエージェント機能、非同期バッチ処理も利用できる。利用可否、モデルID、料金、レート制限は変更されるため、実装時にはConsoleのModelsとLimitsを確認する。

## 詳細

### APIキーの取得

1. [Groq Console](https://console.groq.com/)へサインインする。
2. 複数の用途・環境を分ける場合は、Consoleの**Projects**でプロジェクトを作成して選択する。APIキー、利用状況、ログ、プロジェクトごとのレート制限は選択中のプロジェクトに紐付く。
3. [API Keys画面](https://console.groq.com/keys)でキーを作成する。生成後の秘密値は安全な場所へ保存し、ソースコード、Git履歴、ブラウザー向けJavaScript、ログには含めない。
4. ローカル開発では環境変数に設定する。PowerShellでは、現在のプロセスだけに設定する例は次のとおり。

```powershell
$env:GROQ_API_KEY = "作成したAPIキー"
```

永続的な環境変数、CI/CDのシークレット、またはシークレット管理サービスを用途に応じて使う。漏えいが疑われるキーはConsoleで直ちに無効化し、新しいキーへ置き換える。

### 最小の呼び出し例

公式Python SDKをインストールし、環境変数からキーを読む例である。

```powershell
pip install groq
```

```python
from groq import Groq

client = Groq()
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "日本の首都を一文で答えてください。"}
    ],
)
print(response.choices[0].message.content)
```

SDKは既定で`GROQ_API_KEY`を参照する。HTTPを直接使う場合は、`Authorization: Bearer <APIキー>`ヘッダーを付けて、`POST https://api.groq.com/openai/v1/chat/completions`へ送信する。既存のOpenAI SDKでも、APIキーとこのベースURLを指定すればOpenAI互換のインターフェースで利用できる。

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "短い挨拶を返してください。"}],
)
print(response.choices[0].message.content)
```

利用前に`GET https://api.groq.com/openai/v1/models`で、自分のアカウントで有効なモデルIDを取得できる。上記モデルIDは公式ドキュメントの例であり、モデルの提供終了や権限によって利用できない場合がある。

### 使える主な機能

| 機能 | 内容 | 主なAPI・注意点 |
| --- | --- | --- |
| テキスト会話・生成 | system/user/assistantメッセージによる会話、ストリーミング、複数ターンの文脈送信 | `chat/completions`。モデルごとのコンテキスト長、ツール、推論対応をModelsで確認する。 |
| Responses API | OpenAI Responses API互換のテキスト・画像入力、テキスト出力、関数呼び出し | `POST /responses`。公式文書ではベータであり、状態保持型会話は未対応のため履歴をアプリ側で送る。 |
| 画像理解 | 画像URLまたはBase64 data URLとテキストをモデルへ渡し、説明、OCR、視覚的な質問応答を行う | 対応するVisionモデルが必要。画像URL入力はリクエスト全体20 MB以下、画像枚数にはモデル別上限がある。 |
| 音声文字起こし・英訳 | 音声ファイルまたはURLをテキストへ変換し、対応モデルでは英語へ翻訳する | `POST /audio/transcriptions`、`POST /audio/translations`。対応形式・ファイルサイズ・翻訳対応はモデルと利用プランを確認する。 |
| 音声合成 | テキストから音声を生成する | `POST /audio/speech`。公式文書掲載のOrpheusモデルでは英語・アラビア語の音声を提供する。 |
| 関数呼び出し（Tool Use） | アプリがJSON Schemaで定義した関数候補をモデルが選び、引数を返す | 関数を実行するのはアプリ側。引数を検証し、危険な操作は許可制にする。対応モデルに限定される。 |
| 構造化出力 | JSON Object ModeまたはJSON Schemaに沿う応答を得る | 対応モデルでは`response_format`を使う。`strict: true`は制約付きデコードでスキーマ準拠を保証するが、公式文書掲載時点ではGPT-OSS 20B/120Bに限定される。 |
| 推論 | 複雑な問題向けに推論量を指定できるモデルを使う | `reasoning_effort`またはResponses APIの`reasoning.effort`を使う。許容値はモデル別で、未対応値は400となる。 |
| Groq Compound | Web検索、Webページ訪問、コード実行、Wolfram Alphaをサーバー側で自動利用するシステム | `groq/compound`と`groq/compound-mini`。Compoundではカスタムのユーザー定義ツールは未対応。機密・個人情報を外部ツールへ送らない設計が必要。 |
| Responses APIの組み込みツール | コード実行、ブラウザー検索などをResponses APIから使う | ベータ機能。利用可能なモデルとツールは公式ドキュメントで確認する。 |
| Batch API | 大量のリクエストを非同期でまとめて実行する | 標準レート制限に影響せず、公式文書では50%低コスト、処理時間は24時間から7日間とされる。即時応答が必要な用途には不向き。 |

### 運用時の確認事項

- レート制限は組織単位で適用される。RPM、RPD、TPM、TPD、音声秒数などの上限のうち、先に到達したものが制限になる。正確な上限は[Limits画面](https://console.groq.com/settings/limits)を確認する。
- 制限超過時は`429 Too Many Requests`が返る。`retry-after`と`x-ratelimit-*`レスポンスヘッダーを読み、指数バックオフを実装する。
- APIキーはフロントエンドに置かず、信頼できるバックエンド経由で呼び出す。HTTPS/TLSの検証を無効化しない。
- モデルの一覧、価格、提供状態、対応機能は固定ではない。実装・更新時に[Models](https://console.groq.com/docs/models)、[料金](https://console.groq.com/pricing)、各機能のモデル対応表を確認する。

## 参考資料

- [Groq API Quickstart](https://console.groq.com/docs/quickstart)
  - 参照日: 2026-09-08
- [Groq API Libraries](https://console.groq.com/docs/libraries)
  - 参照日: 2026-09-08
- [Projects](https://console.groq.com/docs/projects)
  - 参照日: 2026-09-08
- [Groq API Reference](https://console.groq.com/docs/api-reference)
  - 参照日: 2026-09-08
- [Models](https://console.groq.com/docs/models)
  - 参照日: 2026-09-08
- [Vision](https://console.groq.com/docs/vision)
  - 参照日: 2026-09-08
- [Speech to Text](https://console.groq.com/docs/speech-to-text)
  - 参照日: 2026-09-08
- [Text to Speech](https://console.groq.com/docs/text-to-speech)
  - 参照日: 2026-09-08
- [Tool Use](https://console.groq.com/docs/tool-use)
  - 参照日: 2026-09-08
- [Structured Outputs](https://console.groq.com/docs/structured-outputs)
  - 参照日: 2026-09-08
- [Responses API](https://console.groq.com/docs/responses-api)
  - 参照日: 2026-09-08
- [Groq Compound](https://console.groq.com/docs/compound)
  - 参照日: 2026-09-08
- [Batch Processing](https://console.groq.com/docs/batch)
  - 参照日: 2026-09-08
- [Rate Limits](https://console.groq.com/docs/rate-limits)
  - 参照日: 2026-09-08
- [Security Onboarding](https://console.groq.com/docs/production-readiness/security-onboarding)
  - 参照日: 2026-09-08

## 更新履歴

- 2026-09-08: 初版を作成。APIキー取得、基本利用、主要機能、運用上の注意を整理。
