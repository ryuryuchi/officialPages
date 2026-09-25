---
作成日: 2026-08-27
更新日: 2026-08-31
タグ:
  - IEC
  - ISO
  - EMC
  - 国際規格
状態: 完了
---

# TC 77・SC 77AとICS 33.100.10

## 概要

規格情報に記載された「TC 77/SC 77A」と「ICS 33.100.10」が何を示すか、
および両者の違いと関係を確認した。

## 結論

- `TC 77/SC 77A`は、IEC（国際電気標準会議）で規格を審議・作成する組織を示す。
  - `TC 77`: Technical Committee 77（第77技術委員会）
    「Electromagnetic compatibility（電磁両立性、EMC）」
  - `SC 77A`: TC 77のSubcommittee 77A（第77A分科委員会）
    「EMC - Low frequency phenomena（EMC―低周波現象）」
    主な対象周波数は概ね9 kHz以下（現象又は機器に応じて上限を上げ得る）。
- `ICS 33.100.10`は、規格を主題別に整理する国際規格分類
  （International Classification for Standards）のコードで、
  「Emission（エミッション）」を示す。
- したがって、この2項目が同じ規格に記載されている場合は、概ね
  「IECのEMC・低周波現象を担当するSC 77Aが扱う規格で、内容分類はEMCの
  エミッションに属する」という意味である。

## 詳細

### TC 77/SC 77A

`TC`はTechnical Committee（技術委員会）、`SC`はSubcommittee
（分科委員会）の略である。IECの公式委員会ページでは、TC 77の名称を
「Electromagnetic compatibility」、その配下のSC 77Aの名称を
「EMC - Low frequency phenomena」としている。

これは「誰が規格を担当するか」を表す組織上の識別子である。
`TC 77/SC 77A`という表記は、TC 77に属するSC 77Aを意味する。

2026年8月31日時点のIEC公式Scopeでは、TC 77は製品委員会が横断利用する
EMC規格・技術報告書を作成し、全周波数範囲のイミュニティ、9 kHz以下の
エミッション、CISPRの範囲外にある9 kHz超のエミッション等を扱う。
SC 77Aは低周波現象（概ね9 kHz以下）を担当する。委員会名称・所属の変更は
確認されなかった。

### ICS 33.100.10

ICSは規格文書を主題別に検索・整理するための階層的な分類コードである。
コードの階層は次のとおり。

- `33`: Telecommunications. Audio and video engineering
  （電気通信、音響・映像工学）
- `33.100`: Electromagnetic compatibility (EMC)
  （電磁両立性。無線妨害を含む）
- `33.100.10`: Emission（エミッション）

EMCにおけるエミッションは、機器などから外部へ出る電磁妨害を指す。
ただし、ICSコード自体は担当委員会を示すものではなく、同じICS分類に
複数の委員会や標準化機関の規格が含まれ得る。

### 両者の読み分け

| 表記 | 示すもの | この場合の意味 |
| --- | --- | --- |
| `TC 77/SC 77A` | 規格を担当するIECの委員会 | EMCのうち低周波現象を扱う分科委員会 |
| `ICS 33.100.10` | 規格の主題分類 | EMCのエミッション |

この情報だけでは具体的な規格番号や要求事項までは特定できない。規格番号
（例: `IEC 61000-...`）が併記されている場合は、その番号を確認することで、
対象機器、試験方法、限度値などをさらに特定できる。

## 参考資料

- [IEC TC 77 Dashboard](https://www.iec.ch/ords/f?p=103:7:0::::FSP_ORG_ID:1265)
  - 参照日: 2026-08-31
- [IEC TC 77/SC 77A Dashboard](https://www.iec.ch/ords/f?p=103:7:0::::FSP_ORG_ID:1384)
  - 参照日: 2026-08-31
- [ISO ICS 33](https://www.iso.org/ics/33/x/)
  - 参照日: 2026-08-31
- [ISO ICS 33.100](https://www.iso.org/ics/33.100/x/)
  - 参照日: 2026-08-31
- [ISO ICS 33.100.10](https://www.iso.org/ics/33.100.10/x/)
  - 参照日: 2026-08-31

## 更新履歴

- 2026-08-31: 全参考URLを再確認し、IEC Dashboardを現行URLへ更新してTC 77・SC 77AのScopeを追記
- 2026-08-27: 初版を作成
