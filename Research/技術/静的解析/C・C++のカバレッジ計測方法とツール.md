---
作成日: 2026-09-29
更新日: 2026-10-08
タグ:
  - C言語
  - C++
  - カバレッジ
  - テスト
  - ツール
状態: 完了
---

# C・C++のカバレッジ計測方法とツール

## 概要

「C系統のソース」はC/C++のソースコードを指すものとして、カバレッジを
実際に計測してレポートに出力する手順を調べた。GCC、Clang、Visual Studioなどの
開発環境別の方法と、一般的なツールの役割・選び方を整理する。

## 結論

- C/C++のカバレッジは、概ね「計測用オプション付きでビルド → テストや
  対象プログラムを実行 → 収集データからレポート生成」の3段階で出す。
- LinuxやGCC中心のプロジェクトでは、GCCの`gcov`で計測し、`gcovr`で
  テキストやHTML等のレポートにする方法が手軽である。`lcov`と`genhtml`も
  広く使われるHTMLレポート手段である。
- Clangを使う場合は、Clangのソースベース計測（`llvm-profdata`と`llvm-cov`）
  を選ぶとよい。これはGCC互換のgcov形式とは別の計測方式である。
- WindowsのMSVCではVisual Studioのコードカバレッジ機能を候補にする。
  Visual Studio以外や既存のPDB対応環境では選択肢が異なるため、コンパイラ、
  IDE、CIで採用済みの方式に合わせる。
- 新規導入では、既に保守終了・アーカイブ済みのOpenCppCoverageを標準選択に
  しない。組み込み等の特殊なコンパイラではBullseyeCoverageのような商用製品も
  候補になる。
- SonarQubeなどの品質基盤は、通常カバレッジを自分で計測するのではなく、
  対応形式の外部レポートを取り込む。

## 詳細

### 1. 計測からレポートまでの流れ

1. カバレッジ計測に対応したコンパイラとレポートツールを決める。
2. 対象となる製品コードとテストコードを、計測オプション付きでビルドし直す。
3. テストプログラムまたは対象アプリケーションを実行し、計測データを出す。
4. `gcovr`、`llvm-cov`などで行・分岐の集計やHTML/XML等のレポートを作る。
5. 未実行箇所を確認し、必要なテストを追加する。

テストを実行するだけでは計測できない。通常のビルド済みバイナリには
カバレッジ計測コードが入っていないため、原則として対象の翻訳単位を計測
オプション付きで再コンパイルする。実行データが前回分と混ざらないよう、
専用のビルドディレクトリを使い、測定前にそのビルドを作り直す運用が安全である。

### 2. GCCとgcovrでHTMLレポートを出す例

次の例では、`src/discount.c`を`tests/test_discount.c`から呼び出す簡単な
テスト実行ファイルがあるものとする。以下はLinuxやMinGW等のGCC系コマンドの
例であり、実プロジェクトでは既存のMakefileやCMakeのビルド設定に計測フラグを
加える。

```sh
mkdir -p build-cov
cd build-cov

gcc --coverage -O0 -g -I../src \
  -c ../src/discount.c -o discount.o
gcc --coverage -O0 -g -I../src \
  -c ../tests/test_discount.c -o test_discount.o
gcc --coverage -o test_discount discount.o test_discount.o

./test_discount
gcovr --root .. --html-details coverage.html
```

`coverage.html`をブラウザーで開くと、ファイルや行ごとの実行状態を確認できる。
コマンドラインに概要を出すだけなら、最後の行を`gcovr --root ..`にする。

主な役割は次の通り。

- `--coverage`: GCCで計測用コードを有効にするコンパイル・リンクオプション。
  `-fprofile-arcs -ftest-coverage`の組み合わせに相当する。
- `-O0`: 最適化による行や制御フローの変化を抑え、ソース上で読みやすい結果を
  得やすくするための例。実運用の最適化済みビルドとの結果は同一とは限らない。
- `-g`: デバッグ情報を付ける例。
- `gcovr`: GCCのカバレッジデータを集め、テキスト、HTML、XML等の形式に整える。
- `gcov`: GCCが生成する実行データを解析する基本ツール。`gcovr`が内部で呼び出す。

`.gcno`はコンパイル時に作られる計測対象の情報、`.gcda`は計測付きプログラムを
実行したときに作られる実行回数データである。これらは通常、対応するオブジェクト
ファイルと関連付いた場所に出力される。ソースとビルドディレクトリを分けた場合は、
ビルドディレクトリから`gcovr --root <ソースルート>`を実行する。

複数の`.c`/`.cpp`ファイルや静的ライブラリに分かれている場合、測定したい各翻訳
単位を計測付きで再ビルドする必要がある。フラグを追加しただけで古いオブジェクト
ファイルが残っていると、その古いコードはカバレッジ対象にならないことがある。

### 3. Clangとllvm-covでレポートを出す例

Clangのソースベース計測では、計測用オプション付きでバイナリをビルドし、
実行時に`.profraw`を出力する。その後`llvm-profdata`でデータをまとめ、
`llvm-cov`でHTMLレポートを作る。

```sh
mkdir -p build-cov
clang -fprofile-instr-generate -fcoverage-mapping -O0 -g \
  src/discount.c tests/test_discount.c -o build-cov/test_discount

LLVM_PROFILE_FILE="build-cov/coverage-%p.profraw" \
  ./build-cov/test_discount

llvm-profdata merge -sparse build-cov/coverage-*.profraw \
  -o build-cov/coverage.profdata
llvm-cov show build-cov/test_discount \
  -instr-profile=build-cov/coverage.profdata \
  --format=html --output-dir=build-cov/html
```

生成された`build-cov/html/index.html`を開いて確認する。複数プロセスや複数の
テスト実行で`.profraw`が衝突しないよう、例では`%p`（プロセスID）をファイル名に
含めている。Clangのバージョンに対応した`llvm-profdata`と`llvm-cov`を使う。

Clangには別にGCC互換のgcov形式で計測する方法もある。GCC向けの`--coverage`を
使う方式と、上記のソースベース方式を混在させるのではなく、選んだ方式に応じた
データ形式とレポートツールを揃える。

組み込みや安全性重視の開発でMC/DCを測る要件がある場合、Clangのソースベース
計測では`-fcoverage-mcdc`が用意されている。ただし、採用可能なコンパイラ版や
対象環境、レポートツールの対応を個別に確認する。

### 4. Windows・Visual Studioでの計測

MSVCを使うWindowsネイティブC++プロジェクトでは、Visual Studioの
**Analyze Code Coverage**機能、またはMicrosoftの`Microsoft.CodeCoverage.Console`
を候補にする。IDE上のテストを対象にする方法と、コマンドラインで実行ファイルを
計測する方法があり、CIに組み込むときは対象プロジェクトの種類に合った手順を選ぶ。

Visual Studioの版・エディションや計測方式により、対応条件と操作が異なる。
実行ファイルだけでなく、対象ライブラリ、シンボル（PDB）、リンク設定などが
正しく揃っているか公式手順で確認する。レポートをSonarQubeに取り込む場合は、
Visual Studio Coverage XML用の設定を使用する。

Microsoftのコンソール計測ツールは、ネイティブコードも対象にできる
`dotnet-coverage`の拡張として提供されている。具体的なオプションや設定は
Visual Studioの版とシナリオに合わせて公式手順を確認する。

MSVCを使わないWindows環境では、Clang/LLVMのWindows対応状況、MinGWのGCCと
gcovr、既存のCI製品に合わせて選ぶ。古いPDBベースの計測ツールは、OSやVisual
Studioの更新との互換性を別途確認する。

### 5. よく使われるツールの比較

| ツール | 主な役割・環境 | 向いているケース・注意点 |
| --- | --- | --- |
| `gcov` | GCCの計測データを解析する | GCC標準の基本ツール。直接の出力は主に行単位のテキスト |
| `gcovr` | gcov等のデータをまとめてレポート化する | GCC系で導入しやすい。HTMLやCobertura等に加え、SonarQube向け出力形式も選べる |
| `lcov` / `genhtml` | gcov系等のデータを収集・加工し、HTML表示する | ブラウザーで閲覧しやすい。`.info`形式の中間ファイルやフィルターを活用できる |
| `llvm-profdata` / `llvm-cov` | Clang/LLVMのプロファイルを統合・表示する | Clangのソースベース計測やLLVM環境で有力。GCC互換gcovモードとは区別する |
| Visual Studio Code Coverage | MSVCネイティブC++等の計測とIDE/CI表示 | WindowsとVisual Studioを中心に開発している場合に便利。版ごとの要件を確認する |
| OpenCppCoverage | Windows向けのPDBベースC++計測 | 既存環境との互換性を確認する用途。公式リポジトリが保守終了・アーカイブ済みのため、新規採用は慎重にする |
| BullseyeCoverage | 商用のC/C++計測ツール | 多様な組み込みコンパイラやターゲットの対応が必要な場合に候補。ライセンス費用と対象版を確認する |
| Xcode Coverage | Apple開発環境のテストカバレッジ表示 | macOS/iOS等のXcodeプロジェクトで標準のビルド・テスト環境に沿って使う |
| SonarQube | 外部レポートの取り込みと品質分析 | 計測器そのものではない。レポート形式と解析設定を一致させる |

`gcovr`からSonarQube向けレポートを出す場合は、`gcovr --sonarqube coverage.xml`
を使い、SonarQube側でそのレポートを取り込む。Cobertura形式など別形式を設定する
前に、C/C++解析でサポートされる形式と対応パラメーターを確認する。

### 6. 環境に応じた選び方

- **GCCを使うLinux・組み込みLinux**: まず`gcovr`を検討する。HTMLレポートや
  CI用XMLが必要なら、既存CIが要求する出力形式を確認する。
- **Clang/LLVMを使うLinuxやmacOS**: `llvm-profdata`と`llvm-cov`による
  ソースベース計測を検討する。XcodeプロジェクトではXcode標準のカバレッジ機能も
  候補になる。
- **MSVCを使うWindows**: Visual Studio標準のカバレッジ機能を先に確認する。
  IDEでの確認を優先するか、コマンドラインのCIレポートを必要とするかで運用を決める。
- **独自の組み込みコンパイラ・実機ターゲット**: コンパイラの計測ランタイム、
  ターゲット上でのデータ保存・回収可否、ホスト側レポート変換を確認する。
  GCC/Clangのオプションをそのまま適用できるとは限らない。BullseyeCoverage等の
  対応表も選定材料になる。
- **複数言語を一つの品質基盤で管理**: 言語別の計測ツールで測り、基盤側の
  対応フォーマットへ変換して取り込む。基盤が表示する総合値だけを見て、元の
  カバレッジデータやテスト結果を捨てない。

### 7. よくあるつまずき

- **計測フラグ付きで全対象を再ビルドしていない**: 対象翻訳単位の一部が
  未計測となる。カバレッジ専用のクリーンなビルドディレクトリを作る。
- **コンパイラと解析ツールの組み合わせが違う**: GCCのデータを別バージョンの
  `gcov`や不一致のLLVMツールで読むと、解析に失敗したり不完全になったりする。
- **前回の実行データが残っている**: GCCの`.gcda`は既存データへ実行回数を
  追加し得る。再現可能な比較のため、測定条件とデータの初期化方法を統一する。
- **対象外コードの除外が広すぎる**: テスト不足を隠す結果になる。生成コード等を
  除外する場合も、対象・理由・ルールを記録する。
- **集計値だけを見て品質とみなす**: カバレッジはテスト対象の実行度であり、
  期待結果を検証するアサーションの質や仕様の網羅性とは別である。一般的な指標の
  違いや限界は[開発におけるカバレッジの意味](./開発におけるカバレッジの意味.md)
  を参照する。

## 参考資料

- [Gcov - Using the GNU Compiler Collection (GCC)](https://gcc.gnu.org/onlinedocs/gcc/Gcov.html)
  - 参照日: 2026-09-29
- [Getting Started - gcovr](https://gcovr.com/en/stable/getting-started.html)
  - 参照日: 2026-09-29
- [Compiling for Coverage - gcovr](https://gcovr.com/en/stable/guide/compiling.html)
  - 参照日: 2026-09-29
- [Source-based Code Coverage - Clang](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html)
  - 参照日: 2026-09-29
- [llvm-cov - LLVM Command Guide](https://llvm.org/docs/CommandGuide/llvm-cov.html)
  - 参照日: 2026-09-29
- [Determine code testing coverage - Visual Studio | Microsoft Learn](https://learn.microsoft.com/en-us/visualstudio/test/using-code-coverage-to-determine-how-much-code-is-being-tested?view=visualstudio)
  - 参照日: 2026-09-29
- [Microsoft.CodeCoverage.Console tool - Visual Studio | Microsoft Learn](https://learn.microsoft.com/en-us/visualstudio/test/microsoft-code-coverage-console-tool)
  - 参照日: 2026-09-29
- [Microsoft code coverage tools](https://github.com/microsoft/codecoverage)
  - 参照日: 2026-09-29
- [C / C++ / Objective-C test coverage - SonarQube Server](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/test-coverage/c-family-test-coverage)
  - 参照日: 2026-09-29
- [LCOV - Linux Test Project](https://github.com/linux-test-project/lcov)
  - 参照日: 2026-09-29
- [OpenCppCoverage repository](https://github.com/OpenCppCoverage/OpenCppCoverage)
  - 参照日: 2026-09-29
- [Supported Platforms and Tools - BullseyeCoverage](https://www.bullseye.com/platform.html)
  - 参照日: 2026-09-29

## 更新履歴

- 2026-10-08: yomiyasuの原則に基づき本文を推敲
- 2026-09-29: C/C++の計測手順、環境別ツール、レポート出力と注意点を公式資料に基づいて初版作成
