---
作成日: 2026-09-03
更新日: 2026-09-03
タグ:
  - MACアドレス
  - OUI
  - IEEE
  - ネットワーク
状態: 完了
---

# MACアドレスのOUI

## 概要

MACアドレスに関連して使われるOUIの意味、アドレス内での位置、用途と判別上の注意点を調べた。

## 結論

OUI（Organizationally Unique Identifier、組織固有識別子）は、IEEE Registration Authorityが組織へ割り当てる24ビット（3オクテット）の識別子である。

一般的な48ビットのMACアドレス（EUI-48）をMA-L割り当てから作る場合、先頭24ビットがOUI、後半24ビットが割り当てを受けた組織の管理部分になる。このため、グローバルに管理されたMACアドレスでは、先頭6桁の16進数から登録組織を調べられることが多い。

ただし、ローカル管理アドレスやWi-Fiなどで使われるランダム化MACアドレスは、先頭部分が機器メーカーのOUIとは限らない。OUI検索の結果だけで、実際の機器メーカーや機種を必ず特定できるわけではない。

## 詳細

### OUIの位置

MACアドレスは通常、次のように12桁の16進数で表す。

```text
00:1A:2B:3C:4D:5E
└─ OUI ─┘└ 組織が管理する部分 ┘
```

- `00:1A:2B`：先頭24ビット、すなわち6桁の16進数に相当するOUI
- `3C:4D:5E`：後半24ビット。割り当てを受けた組織が機器ごとに管理する部分

上の値は構造を説明するための例であり、特定組織の登録情報を示すものではない。

IEEEでは、従来OUI割り当てと呼ばれていた大規模なMACアドレス割り当てをMA-L（MAC Address Block Large）と呼んでいる。MA-LにはOUIが含まれ、OUIへ組織管理の24ビットを付加するとEUI-48を生成できる。後半24ビットには理論上、約1,677万通りの値がある。

### 何のためにあるか

OUIは、異なる組織が生成する識別子の重複を避けるための名前空間になる。主な用途は次のとおり。

- EthernetやWi-Fiで使うEUI-48形式のMACアドレスを生成する
- EUI-64など、ほかの拡張識別子を生成する
- 一部のプロトコルで会社識別子として使用する
- IEEEの公開登録一覧から割り当て先の組織を確認する

### OUIから分かることと分からないこと

IEEEの公開登録情報を検索すれば、OUIの割り当てを受けた組織名を確認できる。ただし、確認できるのは基本的に「その番号範囲の登録先」である。

次の理由から、OUIだけで端末の正確なメーカー、製品名、利用者を断定することはできない。

- 委託製造や部品供給により、登録組織名と製品ブランドが異なる場合がある
- 仮想マシンやソフトウェアがMACアドレスを設定する場合がある
- ローカル管理アドレスは、組織へ割り当てられたOUIを前提としない
- プライバシー保護のため、端末がランダム化したMACアドレスを使う場合がある
- MACアドレスは技術的に変更または偽装できる

したがって、OUI検索はネットワーク調査の手掛かりにはなるが、機器の本人確認に相当する証拠にはならない。

### 現在の割り当て区分

IEEEは必要なアドレス数に応じて、MACアドレスブロックを次の3種類で提供している。

- MA-L（Large）
- MA-M（Medium）
- MA-S（Small）

日常的に「OUI」と呼ぶ場合は、特にMA-Lに含まれる24ビットのOUIを指すことが多い。MA-MやMA-Sは割り当て範囲の大きさと境界が異なるため、すべてのMACアドレスについて「先頭24ビットがメーカー固有のOUI」と単純化するのは正確ではない。

## 参考資料

- [IEEE SA - MA-L](https://standards.ieee.org/products-programs/regauth/oui/)
  - 参照日: 2026-09-03
- [IEEE SA - MAC Addresses](https://standards.ieee.org/products-programs/regauth/mac/)
  - 参照日: 2026-09-03
- [IEEE Standards Support - MAC address options](https://standards-support.ieee.org/hc/en-us/articles/25905790346260-MAC-address-options)
  - 参照日: 2026-09-03
- [IEEE Standards Support - Guidelines for Use of Extended Unique Identifier, Organizationally Unique Identifier, and Company ID](https://standards-support.ieee.org/hc/en-us/articles/4888705676564-Guidelines-for-Use-of-Extended-Unique-Identifier-EUI-Organizationally-Unique-Identifier-OUI-and-Company-ID-CID)
  - 参照日: 2026-09-03

## 更新履歴

- 2026-09-03: 初版を作成
