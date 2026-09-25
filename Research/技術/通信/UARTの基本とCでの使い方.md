---
作成日: 2026-09-10
更新日: 2026-09-10
タグ:
  - UART
  - シリアル通信
  - C言語
  - マイコン
状態: 完了
---

# UARTの基本とCでの使い方

## 概要

UARTが何をする仕組みなのか、また「CでUARTを使う」とは具体的に何を意味するのかを、組み込み開発の初心者向けに整理した。

## 結論

UART（Universal Asynchronous Receiver/Transmitter）は、マイコンやセンサーなどの機器間で、データを1ビットずつ送受信する非同期シリアル通信の仕組みである。

UARTはC言語の機能ではない。Cプログラムから、マイコン内蔵UARTのレジスターや、メーカー提供のドライバー・HAL（Hardware Abstraction Layer）を操作して利用する。したがって、実際のCコードはマイコンやOSによって異なる。

最初に試す設定としては、両端を同じ通信条件（例えば `115200 baud、8データビット、パリティなし、ストップビット1`、略して `115200 8N1`）にし、送信側のTXを受信側のRXへ、RXをTXへ、GNDをGNDへ接続する。

## 詳細

### UARTの基本

- **非同期**：クロック線を別に送らないため、送受信側で通信速度などの条件を事前に合わせる。
- **TX**：送信線（Transmit）
- **RX**：受信線（Receive）
- **baud rate**：1秒あたりの通信速度。UARTでは通常、1シンボルが1ビットなのでビット毎秒の意味で使われることが多い。
- **全二重**：TXとRXが別線なので、送信と受信を同時に行える。

1バイトの送信では、通常、アイドル状態の後にスタートビット、データビット、任意のパリティビット、ストップビットを付ける。よく使われる `8N1` は「データ8ビット、パリティなし、ストップビット1」を表す。データビットは一般に最下位ビット（LSB）から送られる。

### 配線と規格の注意

UARTは論理的な通信方式であり、電圧レベルやコネクター形状まで一意に決めるものではない。TTL/CMOSレベルのUART、RS-232、RS-485、USB-シリアル変換器などは、電気的な仕様や信号の扱いが異なる。

そのため、機器の仕様書で電圧レベルを確認せずに接続してはいけない。特に、マイコンの3.3 V UART信号をRS-232ポートへ直接接続することはできない。PCと接続する場合は、適切なUSB-UART変換器などを使用する。

### Cで使うときの考え方

Cの標準ライブラリだけでUARTを直接開くことはできない。典型的な処理は次の順序になる。

1. UART番号とTX/RXピンを選ぶ。
2. baud rate、データ長、パリティ、ストップビットを設定する。
3. UARTドライバーを初期化する。
4. 送信関数でバイト列を送り、受信関数または受信割り込みでデータを読む。
5. 必要に応じてタイムアウト、リングバッファ、割り込み、DMAを扱う。

例えば、メーカーSDKを使うコードは次のような形になる。関数名や型はSDKごとに異なるため、そのまま別のマイコンへ移植できるコードではない。

```c
uart_config_t config = {
    .baud_rate = 115200,
    .data_bits = UART_DATA_8_BITS,
    .parity = UART_PARITY_DISABLE,
    .stop_bits = UART_STOP_BITS_1
};

uart_param_config(UART_NUM_1, &config);
uart_set_pin(UART_NUM_1, TX_PIN, RX_PIN,
             UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
uart_driver_install(UART_NUM_1, 1024, 1024, 0, NULL, 0);
```

送受信処理は、単純な確認ならポーリング、他の処理と並行して受信するなら割り込み、連続した大量データならDMAを選ぶことが多い。

### よくあるつまずき

- 送受信側のbaud rateや `8N1` などの条件が一致していない
- TX同士、RX同士を接続している（基本はTX-RX、RX-TX）
- GNDを共通にしていない
- UARTの電圧レベルが合っていない
- 改行コード（LF/CRLF）や文字コードの前提が違う
- 受信処理が遅く、バッファーがあふれている

## 参考資料

- [Analog Devices: UART: A Hardware Communication Protocol Understanding the Basics](https://www.analog.com/en/resources/analog-dialogue/articles/uart-a-hardware-communication-protocol.html)
  - 参照日: 2026-09-10
- [Espressif ESP-IDF Programming Guide: Universal Asynchronous Receiver/Transmitter (UART)](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/uart.html)
  - 参照日: 2026-09-10

## 更新履歴

- 2026-09-10: UARTの役割、通信フレーム、配線上の注意、Cでの利用方法を初版として整理
