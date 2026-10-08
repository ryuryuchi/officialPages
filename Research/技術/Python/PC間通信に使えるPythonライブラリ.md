---
作成日: 2026-10-07
更新日: 2026-10-07
タグ:
  - Python
  - PC間通信
  - ネットワーク
  - ライブラリ
状態: 完了
---

# PC間通信に使えるPythonライブラリ

## 概要

Pythonで別々のPC間にデータを送受信する方法を、初めて実用的な通信機能を
作る場合の難易度順に整理する。難易度は、導入と基本的な実装に必要な知識を
基準にした目安であり、通信頻度や運用要件によって変わる。

## 結論

一般的なPC間の要求・応答には、HTTP APIをFastAPIで作り、呼び出し側から
HTTPXまたはRequestsで接続する方法が最初の候補となる。双方向の即時通信には
WebSocket、複数の送受信者へイベントを配信する用途にはMQTTが適する。

低レベルで独自の通信方式を実装する必要がなければ、最初から`socket`を使う
よりも、HTTPやWebSocketなど上位の仕組みを使う方が実装しやすい。別PCから
接続するには、ライブラリ選定とは別に、サーバーPCの待受設定、IPアドレス、
ファイアウォールの許可が必要である。

## 詳細

### 難易度順の比較

以下は、LAN内のPC間通信を小規模に実装する場合の大まかな順序である。

| 順位 | 方式・ライブラリ | 通信の形 | 向いている用途 | 難しい点 |
| --- | --- | --- | --- | --- |
| 1 | HTTP API（FastAPI + HTTPX / Requests） | 要求と応答 | データ照会、操作指示、ファイル送受信 | サーバーとクライアントを分けて作る |
| 2 | WebSocket（`websockets`、またはFastAPI） | 接続を保つ双方向通信 | チャット、状態表示、連続した操作 | 接続の開始・切断や非同期処理 |
| 3 | MQTT（Eclipse Paho MQTT） | ブローカー経由の配信 | センサー値、イベント、複数PCへの通知 | MQTTブローカーの用意と管理 |
| 4 | ZeroMQ（PyZMQ） | 要求・応答、配信など複数のパターン | プロセス間・PC間のメッセージング | 通信パターンと接続構成の選択 |
| 5 | gRPC（gRPC Python） | 定義した手続きの呼び出し | 型付きのAPI、サービス間通信 | Protocol Buffersとコード生成 |
| 6 | `socket`（Python標準ライブラリ） | TCPまたはUDPの低レベル通信 | 独自プロトコル、通信の仕組みの学習 | メッセージ境界、再接続、エラー処理などを自分で設計 |

難易度は一律ではない。たとえば、MQTTはクライアント側の送受信コードは比較的
単純だが、ブローカーを別途準備する分、運用開始までの作業が増える。`socket`は
追加パッケージなしで始められる一方、受信データの分割・結合や複数接続の管理を
自分で扱う必要がある。

### 各方式の概要

#### 1. HTTP API: FastAPIとHTTPXまたはRequests

- サーバーPCでFastAPIのAPIを動かし、別PCからHTTPクライアントでアクセスする。
- 要求を送って応答を受け取る形式に向く。JSONのほか、HTTP経由でファイルも
  送受信できる。
- ブローカーやコード生成ツールは不要。APIの形を決めれば、別の言語の
  クライアントからも利用しやすい。
- クライアント側は同期処理ならRequests、同期・非同期の両方を使いたい場合は
  HTTPXが候補となる。
- 常時接続やサーバーからの即時プッシュが不要な業務ツール、PC操作、データ取得の
  最初の実装に向く。

#### 2. WebSocket: `websockets`またはFastAPI

- TCP上の接続を維持し、同じ接続で双方がメッセージを送受信する。
- チャット、ライブ更新、遠隔操作のように、サーバーからも継続的に通知したい
  場合に向く。
- 通常のHTTP要求・応答に比べて、接続状態、切断、再接続などの扱いが増える。
- FastAPIにはWebSocket用のエンドポイント機能がある。`websockets`はWebSocket
  サーバーとクライアントの機能を提供する。

#### 3. MQTT: Eclipse Paho MQTT

- Python側にはEclipse Paho MQTTを使い、別途MQTTブローカーを動かす。
- 送信側はトピックにメッセージを発行し、受信側はトピックを購読する。
  送受信側が互いの接続先を直接管理しなくてもブローカーを介して配信できる。
- PCが複数ある場合の状態通知、機器データ、イベント配信に向く。
- PCが2台だけで単純にAPIを呼び合いたい場合は、ブローカーの運用が余分になる
  可能性がある。

#### 4. ZeroMQ: PyZMQ

- PyZMQはØMQをPythonから利用するためのバインディングで、要求・応答や
  Publish/Subscribeなど複数のメッセージングパターンを選べる。
- 基本的な構成で専用のブローカーを必須としない。構成によっては中継役を設ける。
- HTTP APIよりも通信の構成を意識して選ぶ必要があるため、複数プロセスや
  メッセージ配送を設計する経験がある場合に向く。

#### 5. gRPC: gRPC Python

- Protocol Buffersでサービスとデータ形式を定義し、クライアント・サーバー用の
  Pythonコードを生成して利用する。
- APIの型や契約を明確に保ちたい、複数のサービスから同じAPIを使いたい場合に
  向く。
- 単純な2台間のデータ送受信には準備が多くなりやすい。`.proto`ファイルと
  コード生成ツールの管理も必要になる。

#### 6. `socket`: Python標準ライブラリ

- 標準ライブラリだけでTCPまたはUDP通信を行える。
- TCPは接続型で順序を保ったバイト列のやり取りに使われる。UDPはデータグラムを
  送受信し、到達保証や順序保証はTCPと同じ形では提供されない。
- TCPを使っても、1回の`recv()`がアプリケーションの1メッセージ全体に一致する
  とは限らない。長さ情報や区切り文字など、メッセージ境界を設計する必要がある。
- 通信の仕組みを学ぶ場合や独自プロトコルが必要な場合には有効だが、一般的な
  アプリではHTTPなどの上位方式を先に検討する。

### 用途別の選び方

| やりたいこと | まず検討する方式 |
| --- | --- |
| PCから別PCへ指示やデータを送り、結果を受け取る | FastAPI + HTTPX / Requests |
| 画面をリアルタイムに更新する、双方向に連続送受信する | WebSocket |
| 複数のPCや機器へイベントを配信する | MQTT + Eclipse Paho |
| 独自のメッセージ配送パターンを組み合わせる | PyZMQ |
| スキーマを共有したサービス間通信を行う | gRPC |
| TCP/UDPの仕組みや独自プロトコルを扱う | `socket` |

LAN内で相手PCを手動で指定したくない場合、`zeroconf`はmDNS/DNS-SDを使った
サービスの登録・発見に利用できる。ただし、これはデータを送受信する通信方式の
代わりではなく、接続先を見つける補助である。

### PC間接続で確認すること

1. サーバー側のアプリを起動し、接続を受け付けるネットワークインターフェースと
   ポートを設定する。`localhost`または`127.0.0.1`だけで待ち受ける設定では、
   別PCから接続できない。
2. クライアント側からサーバーPCのLAN内IPアドレスとポートへ接続する。
3. Windowsファイアウォールで必要な受信通信を許可する。Wi-Fiのゲストネットワーク
   など、端末間通信が遮断されるネットワークも確認する。
4. インターネット越しに接続する場合は、NATやファイアウォール、認証、暗号化も
   考慮する。LAN内の接続例をそのままインターネットに公開しない。

## 参考資料

- [FastAPI Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/)
  - 参照日: 2026-10-07
- [HTTPX QuickStart](https://www.python-httpx.org/quickstart/)
  - 参照日: 2026-10-07
- [WebSockets - FastAPI](https://fastapi.tiangolo.com/advanced/websockets/)
  - 参照日: 2026-10-07
- [Getting started - websockets](https://websockets.readthedocs.io/en/stable/intro/index.html)
  - 参照日: 2026-10-07
- [Eclipse Paho MQTT Python Client](https://eclipse.dev/paho/files/paho.mqtt.python/html/index.html)
  - 参照日: 2026-10-07
- [PyZMQ Documentation](https://pyzmq.readthedocs.io/en/latest/)
  - 参照日: 2026-10-07
- [ZeroMQ Guide - Basics](https://zguide.zeromq.org/docs/chapter1/)
  - 参照日: 2026-10-07
- [gRPC Python Quickstart](https://grpc.io/docs/languages/python/quickstart/)
  - 参照日: 2026-10-07
- [socket — Low-level networking interface](https://docs.python.org/3/library/socket.html)
  - 参照日: 2026-10-07
- [Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
  - 参照日: 2026-10-07
- [python-zeroconf documentation](https://python-zeroconf.readthedocs.io/en/latest/)
  - 参照日: 2026-10-07

## 更新履歴

- 2026-10-07: 初版を作成
