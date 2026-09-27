# MSXライブラリAPI

ELiSEのライブラリは、`Lib/*.asm`に実装されたZ80／MSXランタイムです。

ライブラリの関数宣言はアセンブリ内のコメントから読み取られます。

メモリ配置、BIOSワークエリア、VRAM、カートリッジRAMとの関係は
[MSXメモリ配置とELiSEの対応](msx-memory-layout-and-elise.md)を参照してください。

```asm
; func    function void printIntLn(int value)
```

このため、関数を追加するときは、実装ラベルと`func`宣言を同時に追加してください。

## API一覧

### Array

| 関数 | 用途 |
|---|---|
| `Array.new(int size)` | ワード配列を確保 |
| `Array.deAlloc(Array obj)` | 配列を解放 |
| `Array.count(Array obj)` | 配列要素数を取得 |

```els
var Array values;
values = Array.new(10);
Output.printIntLn(values.count());
values.deAlloc();
```

### String

| 関数 | 用途 |
|---|---|
| `String.new(int address, int length)` | データ領域から文字列オブジェクトを作成 |
| `String.dispose(String obj)` | 文字列を解放 |
| `String.length(String obj)` | 文字列長を取得 |
| `String.charAt(String obj, int index)` | 文字を取得 |

ソース上の文字列リテラルは、通常は直接記述できます。

```els
Output.printStringLn("HELLO");
```

### Memory

| 関数 | 用途 |
|---|---|
| `Memory.alloc(int size)` | ヒープからワード単位で確保 |
| `Memory.deAlloc(Memory obj)` | メモリを解放 |
| `Memory.peek(int address)` | CPUメモリからワード読み出し |
| `Memory.peek8(int address)` | CPUメモリからバイト読み出し |
| `Memory.poke(int address, int value)` | CPUメモリへワード書き込み |
| `Memory.poke8(int address, int value)` | CPUメモリへバイト書き込み |
| `Memory.vpeek(int address)` | VRAMからワード読み出し |
| `Memory.vpeek8(int address)` | VRAMからバイト読み出し |
| `Memory.vpoke(int address, int value)` | VRAMへワード書き込み |
| `Memory.vpoke8(int address, int value)` | VRAMへバイト書き込み |
| `Memory.LDIRMV(int v, int m, int count)` | VRAMからメモリへブロック転送 |
| `Memory.LDIRVM(int m, int v, int count)` | メモリからVRAMへブロック転送 |
| `Memory.fillVRAM(int address, int count, int data)` | VRAMを埋める |
| `Memory.writeVDP(int reg, int value)` | VDPレジスタへ書き込む |

`Memory.alloc()`の単位は、ELiSEの配列モデルに合わせてワードです。必要なバイト数を扱う場合は、用途に応じて`peek8`／`poke8`を使用してください。

### Output

| 関数 | 用途 |
|---|---|
| `Output.printLn()` | 改行 |
| `Output.printInt(int value)` | 10進数表示 |
| `Output.printIntLn(int value)` | 10進数表示＋改行 |
| `Output.printIntHex(int value)` | 16進数表示 |
| `Output.printIntHexLn(int value)` | 16進数表示＋改行 |
| `Output.printString(int value)` | 文字列表示 |
| `Output.printStr255(int value)` | 長さ付き文字列表示 |
| `Output.printStringLn(int value)` | 文字列表示＋改行 |
| `Output.printStr255Ln(int value)` | 長さ付き文字列表示＋改行 |
| `Output.printChar(int value)` | 1文字表示 |

### Screen

| 関数 | 用途 |
|---|---|
| `Screen.cls()` | 画面クリア |
| `Screen.locate(int x, int y)` | カーソル位置変更 |
| `Screen.putch(int value)` | 現在位置へ文字表示 |
| `Screen.mode(int screen, int sprite, boolean click)` | 画面・スプライト・キークリック設定 |
| `Screen.changeMode(int mode_number)` | 画面モード変更 |
| `Screen.color(int foreground, int background, int border)` | 色設定 |
| `Screen.keyoff()` | キークリックを無効化 |
| `Screen.keyon()` | キークリックを有効化 |
| `Screen.vdpScreen(int mode)` | VDP画面設定 |

### Sprite

| 関数 | 用途 |
|---|---|
| `Sprite.init()` | スプライト初期化 |
| `Sprite.config(int value)` | サイズ・拡大率設定（0: 8×8標準、1: 8×8拡大、2: 16×16標準、3: 16×16拡大） |
| `Sprite.put(int x, int y, int table, int color, int number)` | スプライト属性設定 |
| `Sprite.off()` | 全スプライトを非表示 |
| `Sprite.on()` | スプライト表示を有効化 |
| `Sprite.offNum(int table)` | 指定番号以降を非表示 |
| `Sprite.onNum(int table, int y)` | 指定番号までを表示 |

### Keyboard

| 関数 | 用途 |
|---|---|
| `Keyboard.stick(int number)` | ジョイスティック入力 |
| `Keyboard.stick0()` | ジョイスティック0入力 |
| `Keyboard.trigger(int number)` | トリガ入力 |
| `Keyboard.trigger0()` | トリガ0入力 |
| `Keyboard.isStopKey()` | 停止キー判定 |
| `Keyboard.readKey()` | BIOS入力バッファから1文字を取得（入力なしは`0`） |
| `Keyboard.readInt(String text)` | 入力を促して整数を読む |

方向値は、0を無入力、1から8を上方向から時計回りの方向として扱います。
`readKey()`はゲームループを停止させず、`Z`／`X`などの文字キーを扱う場合に使えます。

### MSX

| 関数 | 用途 |
|---|---|
| `MSX.screenInit()` | MSX画面・パターン・色・スプライトを初期化 |
| `MSX.keyClick(int state)` | キークリック設定 |
| `MSX.psgInit()` | PSG初期化 |

### Sound

`Sound`はMSXのPSGを使った汎用の音再生ライブラリです。ゲーム固有の
イベント名や音色プリセットは含めず、呼び出し側が音程・音量・再生時間を
指定します。`play()`はPSGチャンネルA、`playB()`はB、`playC()`はCを使います。
`playAC()`はA/Cを同時に鳴らし、Bを効果音用に残します。`play3()`はA/B/Cを
同時に使用します。各チャンネルは独立しているため、`playB()`で鳴らす効果音は
`playAC()`で再生中のBGMを止めません。

| 関数 | 用途 |
|---|---|
| `Sound.init()` | PSGを初期化し、音を停止 |
| `Sound.play(int period, int volume, int frames)` | チャンネルAで指定した音程・音量を再生 |
| `Sound.playB(int period, int volume, int frames)` | チャンネルBで指定した音程・音量を再生 |
| `Sound.playC(int period, int volume, int frames)` | チャンネルCで指定した音程・音量を再生 |
| `Sound.playAC(int periodA, int volumeA, int periodC, int volumeC, int frames)` | チャンネルA/CでBGM用の同期ノートを再生 |
| `Sound.play3(int periodA, int volumeA, int periodB, int volumeB, int periodC, int volumeC, int frames)` | 3チャンネルを指定した音程・音量で同時に再生 |
| `Sound.update()` | 各チャンネルの再生時間を1フレーム進め、終了したチャンネルだけ消音 |
| `Sound.stop()` | 再生中の音を停止 |

`period`はPSGの12ビット音程周期値、`volume`は0〜15、`frames`はVBlank
フレーム数です。`play3()`の3チャンネルは共通の`frames`で管理されます。
PSGへの書き込みはMSX BIOSの`WRTPSG`を使用します。PSGミキサのI/Oポートは
BIOSのVBlank処理が使う方向のまま保持するため、`Timer.waitFrames()`と併用できます。
`Sound.play()`、`Sound.playB()`、`Sound.playC()`は待ちループを行わないため、ゲームループや
`Timer.waitFrames()`を停止させません。再生中は呼び出し側が毎フレーム
`Sound.update()`を呼び出してください。再生状態はカートリッジROMではなく、
ELiSEが確保するRAMワークエリアに保存されます。

### Math

| 関数 | 用途 |
|---|---|
| `Math.abs(int value)` | 絶対値 |

乗算・除算・剰余は、VM命令では`MSXMath`の直接呼び出しへ変換されます。

| VM上の呼び出し | 用途 |
|---|---|
| `MSXMath.multiply` | 乗算 |
| `MSXMath.divide` | 除算 |
| `MSXMath.modulo` | 剰余 |

### Debug

| 関数 | 用途 |
|---|---|
| `Debug.memDump(int address, int row)` | メモリダンプ |
| `Debug.printStack(int value)` | 値をスタック形式で表示 |
| `Debug.halt()` | システム終了 |
| `Debug.showSP()` | SP表示 |
| `Debug.showSPLn()` | SP表示＋改行 |
| `Debug.showReg()` | レジスタ表示 |
| `Debug.setMemFreeList(int address)` | 空きリスト位置を変更 |
| `Debug.memFreeList()` | 空きリスト位置を取得 |
| `Debug.freeHeap()` | 空きヒープ量を取得 |
| `Debug.heapAddress()` | ヒープ先頭を取得 |

`Debug.asm`は環境の`db`設定が有効な場合にリンクされます。

### Timer

| 関数 | 用途 |
|---|---|
| `Timer.start()` | フレームタイマーを開始 |
| `Timer.stop()` | フレームタイマーを停止 |
| `Timer.ticks()` | BIOSの`JIFFY` VBlankカウンタを読む |
| `Timer.waitFrames(int frames)` | 指定フレーム数だけ待つ |

`Timer.waitFrames()`は標準3.58MHzのMSXで約1/60秒になるZ80待機ループを使います。
割り込み状態や割り込みフックに依存しないため、ゲームループのフレーム待ちに
使用できます。`Timer.ticks()`はBIOSの`JIFFY`カウンタを読みます。

### System

| 関数 | 用途 |
|---|---|
| `Sys.return()` | 起動元へ戻る |

## ライブラリを追加する手順

1. `Lib/NewLibrary.asm`を作成
2. 公開関数ごとに`label`と`func`コメントを追加
3. `func`コメントの型・引数形式をELiSE構文に合わせる
4. `build/`へサンプルをコンパイルして呼び出しを確認
5. 必要なら`test/`に`.els`テストを追加

例:

```asm
; label   NewLibrary.add
; func    function int add(int left, int right)
NewLibrary.add:
    ; ...
    ret
```
