# MSXメモリ配置とELiSEライブラリの対応

この文書は、ELiSEのライブラリを変更・追加するときに参照するメモリ配置の
基準をまとめたものです。対象は、現在のELiSEが主に使用しているZ80 CPU、
MSX BIOS、MSX2のVDP、`msxpen`形式、カートリッジ形式です。

## 1. 最初に理解すべきこと

MSXのZ80から見えるアドレス空間は`0x0000`〜`0xFFFF`の64KiBです。しかし、
この64KiBが常に同じ物理メモリを指すわけではありません。CPUアドレス空間は16KiB
単位の4ページに分かれ、各ページにはスロット機構によって異なるROM、RAM、
拡張メモリなどが割り当てられる。

```text
CPUアドレス       ページ       主な用途（典型例）
0x0000-0x3FFF     page 0       BIOS ROM、またはスロット切替後のROM/RAM
0x4000-0x7FFF     page 1       カートリッジROM、プログラム領域
0x8000-0xBFFF     page 2       カートリッジRAM、RAM、拡張メモリなど
0xC000-0xFFFF     page 3       メインRAM、BIOSワークエリアを含むRAM
```

上表は「典型的な見え方」であり、固定的な物理配置ではありません。特に
`0x4000`以降のカートリッジ領域、拡張スロット、メモリマッパーは機種や
カートリッジ形式によって異なる。したがって、ライブラリでは次の2種類を
分けて考える必要があります。

1. BIOSが提供する固定エントリポイントを呼び出します。
2. 現在のスロット構成でCPUから見えているRAM/VRAMを使います。

`0x4000`だから常にカートリッジROM、`0xC000`だから常に自由なRAM、と
決めつけてはいけません。

## 2. BIOS、ワークエリア、フック

### 2.1 BIOSジャンプテーブル

MSX BIOSの先頭には、画面、キーボード、VDP、PSGなどの標準機能を呼び出す
ジャンプテーブルがある。ELiSEは次のように、BIOSエントリを直接呼び出す
ライブラリを持ちます。

| ELiSEで使う機能 | BIOSエントリ |
|---|---:|
| `Screen.putch()` | `CHPUT` `0x00A2` |
| `Screen.cls()` | `CLS` `0x00C3` |
| `Screen.locate()` | `POSIT` `0x00C6` |
| `Screen.changeMode()` | `CHGMOD` `0x005F` |
| `Screen.color()` | `CHGCLR` `0x0062` |
| `Memory.vpeek8()` | `RDVRM` `0x004A` |
| `Memory.vpoke8()` | `WRTVRM` `0x004D` |
| `Memory.LDIRMV()` | `LDIRMV` `0x0059` |
| `Memory.LDIRVM()` | `LDIRVM` `0x005C` |
| `Sound.play()`／`Sound.play3()`内部 | `WRTPSG` `0x0093` |
| `Sprite.init()` | `CLRSPR` `0x0069` |

BIOSエントリを使う場合は、呼び出し規約、入力レジスタ、破壊されるレジスタ、
割り込みとの関係を確認します。特に`WRTPSG`のように、呼び出し後にレジスタが
変化する可能性がある処理では、必要な値を再ロードしてから次のBIOS呼び出しを
行います。

`Sound.play3()`はチャンネルA/B/Cのトーン周期と音量を書き込みます。PSGミキサの
I/Oポート方向はBIOSがVBlank中のキーボード／ジョイスティック処理で使う設定を
維持するため、ELiSEの`Timer.waitFrames()`と併用できます。

### 2.2 BIOSワークエリア

BIOSワークエリアは、BIOSやMSXソフトウェアが共有するRAM領域です。ELiSEも
一部を参照しています。

| アドレス | ELiSEでの用途 | 注意 |
|---:|---|---|
| `0xF3DB` | キークリック設定`CLIKSW` | `Screen.mode()`、`MSX.keyClick()`が使用 |
| `0xF3E0` | 現在のVDPレジスタ1 | スプライトサイズ・拡大率変更前に参照 |
| `0xF3E9` | 前景色 | `Screen.color()`が使用 |
| `0xF3EA` | 背景色 | `Screen.color()`が使用 |
| `0xF3EB` | ボーダー色 | `Screen.color()`が使用 |
| `0xFC9E` | `JIFFY`、VBlankカウンタ | `Timer.ticks()`が使用 |
| `0xFCAF` | 現在の画面モード`SCRMOD` | 色設定時のモード判定に使用 |

ワークエリアは「ELiSE専用のRAM」ではありません。BIOS、BASIC、他の常駐処理も
参照する可能性があるため、未掲載のアドレスを空き領域として利用しません。
新しいライブラリがワークエリアを使う場合は、MSXのワークエリア定義と既存
ライブラリの参照を突き合わせ、使用理由をコメントに残す。

### 2.3 割り込みフック

VBlank割り込みには共有フックが存在します。フックを無断で上書きすると、BIOS、
キーボード、タイマー、他の常駐処理を壊す可能性があります。

現在の`Timer`ライブラリは、割り込みフックを差し替えません。
`Timer.waitFrames()`は割り込み状態に依存しないZ80待機ループを使い、
`Timer.ticks()`だけがBIOSの`JIFFY`を読み取ります。タイマー機能を拡張するときも、
共有フックを変更しない方針を維持します。

## 3. VRAMはCPUメモリとは別物

VDPのVRAMはZ80の通常の`LD (HL),A`では書けません。CPUメモリとVRAMの間は、
BIOSの`RDVRM`、`WRTVRM`、`LDIRVM`、`LDIRMV`、`FILVRM`、またはVDPレジスタを
経由してアクセスします。

そのため、`Memory.poke8(0x2000, value)`はCPUメモリへの書き込みであり、
Screen 2の色テーブルへの書き込みではありません。VRAMへ書くときは
`Memory.vpoke8()`や`Memory.LDIRVM()`を使います。

### 3.1 現在のELiSEのScreen 2前提

`MSX.screenInit()`は、文字パターンを使ったグラフィック画面を初期化し、
Screen 2相当のテーブル配置を前提に、次のVRAM領域へデータを書き込みます。

| VRAMアドレス | 用途 |
|---:|---|
| `0x0000-0x07FF` | パターンジェネレータ1 |
| `0x0800-0x0FFF` | パターンジェネレータ2 |
| `0x1000-0x17FF` | パターンジェネレータ3 |
| `0x1800-0x1AFF` | パターンネームテーブル |
| `0x2000-0x3FFF` | カラーテーブル |

`Lib/MSX.asm`の`PGT1`、`PGT2`、`PGT3`、`PNT`、`COLT`は、この配置を
直接表しています。ライブラリやサンプルがこれらの定数を使う場合、画面モードを
変更した後も同じ配置であるとは限りません。

### 3.2 スプライト

現在の`Sprite`ライブラリは、スプライト属性テーブルをVRAM `0x1B00`に置く
前提です。スプライトパターンの配置は画面モードとVDP設定に依存するため、
スプライトパターンを書き込むサンプルでは、使用するパターンアドレスと
`Sprite.config()`のサイズ設定を同じ構成で確認します。

スプライトの表示位置はCPUメモリ上の座標ではなく、VRAMのスプライト属性
テーブルへ書かれるY、X、パターン番号、色で決まります。文字パターンの消去や
再描画でスプライトが消えるわけではなく、逆も同様です。

## 4. ELiSEのプログラム配置

### 4.1 `msxpen`形式

現在の既定値は次の通りです。

| 項目 | 値 |
|---|---:|
| プログラム開始`org` | `0x8100` |
| 初期スタック`sys_init_sp` | `0xDC60` |
| ヒープサイズ | `0x1000` bytes相当 |
| メディア | `msxpen` |

`msxpen`形式では、コード、ELiSEランタイムのワーク変数、静的データ、文字列、
ヒープが生成アセンブリ内で順に配置されます。`heap_start`が0の場合、ヒープは
絶対アドレス0へ強制配置されず、生成されたワーク領域の後ろに続きます。

したがって、`msxpen`では「ヒープは0x0000から始まる」と理解してはいけません。
最終的な位置は生成されたアセンブリとアセンブラのリストで確認します。

### 4.2 カートリッジ形式

カートリッジ形式では、ELiSEは次の構成を使います。

```text
CPUアドレス       内容
0x4000            カートリッジROM開始、"AB"ヘッダと起動コード
0x4000〜          ELiSEのコードと読み出し専用データ
0x4000+size       カートリッジRAMワークエリアの基準
                 ├─ VMシステム変数
                 ├─ Memoryライブラリの管理変数
                 ├─ Timer/Sound/Spriteの状態変数
                 ├─ static変数
                 └─ heap
0xDC60            初期スタックトップ（現在の既定値）
```

標準の`--cartridge_size`は`0x4000`なので、通常はRAMワークエリアの基準が
`0x8000`になります。`--cartridge_size`を変更すると、ワークエリアの基準も
`org + cartridge_size`へ移動します。

カートリッジの文字列・`dat`データはROM側へ置かれ、実行時に変更するシステム
変数やヒープはRAM側へ置かれます。この分離がないと、ROM上のデータを書き換え
ようとして無効化や誤動作が起きます。

ただし、この配置はELiSEのカートリッジ生成規約であり、すべてのMSXカート
リッジで保証される一般則ではありません。実機・エミュレータ側に、指定した容量と
RAM構成が存在することが前提になります。

### 4.3 スタックとヒープ

ELiSEの起動コードは、起動時のSPを`sys_return`へ保存し、`sys_init_sp`へSPを
移動します。通常の関数呼び出し、VMスタック、ローカル変数、引数はこのスタック
を使用します。

`Memory.alloc()`はワード配列モデルに合わせ、要求要素数を2倍してバイト数に
変換します。各空きブロックにはリンクとサイズの管理情報があり、管理ヘッダは
4バイトです。

```text
低アドレス
  ランタイム変数
  static領域
  heap（上方向へ使用）
       空き領域
  （十分な間隔を確保する）
  stack（高アドレス側から下方向へ使用）
  BIOSワークエリア
高アドレス
```

これは概念図であり、実際の開始位置はメディア、コード長、静的データ量、
`--heap`、`--heap_size`、`--stack`に依存します。ヒープを増やすとスタックや
BIOSワークエリアへ近づくため、メモリ不足の調査では次を確認します。

1. `--heap_size`だけでなく、生成された`heap`ラベルのアドレスを見ます。
2. `sys_init_sp`とヒープ終端の距離を見ます。
3. 文字列、`dat`、static、デバッグ変数が増えていないか確認します。
4. カートリッジではROM容量とRAMワークエリアの両方が足りているか確認します。

## 5. ELiSEライブラリが使用する領域の分類

### 5.1 BIOS・システム共有領域

`0x00xx`のBIOSエントリや`0xFxxx`のBIOSワークエリアは、MSX全体の共有領域
です。ここへ独自の状態を置きません。参照する場合も、既存のBIOS契約に
従います。

### 5.2 ELiSEが生成するRAMワークエリア

`SystemLibrary.py`が実行時に必要なラベルを生成します。

| 領域 | 内容 |
|---|---|
| VMシステム変数 | `sys_SP`、`sys_LOCAL`、`sys_ARGUMENT`、`sys_THIS`など |
| Memory管理変数 | free list、ブロックポインタ、要求サイズ |
| Sprite状態 | `Sprite.off.original` |
| Timer状態 | tick、インストール状態、旧フック保存領域 |
| Sound状態 | active、volume、period、remaining |
| Debug状態 | レジスタ保存領域 |
| static | コンパイル単位の静的変数 |
| heap | `Memory.alloc()`の空き領域 |

ライブラリの状態変数は、アセンブリへ固定アドレスを埋め込むのではなく、
この生成ラベルを使用します。ライブラリを追加するときは、状態変数を
`SystemLibrary.py`のRAMワークエリアへ追加し、ROMデータと混ぜません。

### 5.3 VRAM

画面パターン、色、名前テーブル、スプライト属性・パターンはVRAMに置きます。
VRAMアドレスはCPU RAMのアドレスとは別の名前空間であり、`Memory.vpoke*`や
BIOS転送を介してアクセスします。

## 6. ライブラリ追加時の安全規則

新しいライブラリを追加・変更するときは、次の順で確認します。

1. そのデータがCPU RAM、VRAM、BIOSワークエリアのどれかを決めます。
2. CPU RAMなら、ROMデータか実行時RAMかを決めます。
3. 実行時RAMなら、固定アドレスではなく生成ワークエリアのラベルを使います。
4. VRAMなら、対象画面モードのテーブル配置と衝突しないか確認します。
5. BIOSワークエリアなら、公式の用途と既存ライブラリの参照を確認します。
6. スロット切替、割り込み、BIOS呼び出しでレジスタやマッピングが変わる可能性を確認します。
7. `msxpen`と`cartridge`の両方でアセンブルし、`.lst`でラベル位置を確認します。
8. メモリを使う単体サンプルを作り、値の保持、再起動、解放を確認します。

## 7. 今後のライブラリ作業で優先して見直す箇所

現状のコードから、今後の検討対象は次の通りです。

- `--stack`と実際のスタック／ヒープ衝突を自動検査する仕組み
- カートリッジ容量とRAMワークエリア容量の明示的な分離
- Screen 2以外のVRAMテーブル配置を扱う`Screen`／`Sprite` API
- BIOSワークエリアのアドレス定数を一箇所へ集約する仕組み
- `Timer`の共有フック、`Sound`のPSG状態、`Sprite`のVRAM予約範囲の文書化
- `Memory.deAlloc()`の断片化・再利用を含むヒープ検証

## 8. 参照資料

以下の資料を基準にし、機種依存の挙動はopenMSXと実機で確認します。

- [MSX2 Technical Handbook](https://konamiman.github.io/MSX2-Technical-Handbook/)
- [The Memory - MSX Wiki](https://www.msx.org/wiki/The_Memory)
- [SCREEN 2 - MSX Wiki](https://www.msx.org/wiki/SCREEN_2)
- [Appendix 4: Work area listing](https://konamiman.github.io/MSX2-Technical-Handbook/Appendix4.html)
- [Appendix 5: VRAM map](https://konamiman.github.io/MSX2-Technical-Handbook/Appendix5.html)
- [Appendix 7: Cartridge hardware](https://konamiman.github.io/MSX2-Technical-Handbook/Appendix7.html)
- ELiSEの実装:
  - `src/elise/config.py`
  - `src/elise/cli.py`
  - `src/elise/BootLibrary.py`
  - `src/elise/SystemLibrary.py`
  - `Lib/MSX.asm`
  - `Lib/Memory.asm`
  - `Lib/Screen.asm`
  - `Lib/Sprite.asm`
  - `Lib/Sound.asm`
  - `Lib/Timer.asm`

この文書のアドレス表は、MSX BIOSの標準配置と現在のELiSE実装を対応付けた
ものです。新しいライブラリが別モード、別スロット、メモリマッパー、
MSX2+固有機能を使う場合は、この文書へ前提条件を追記してから実装します。
