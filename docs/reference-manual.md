# ELiSE リファレンスマニュアル

この文書は、ELiSEで`.els`プログラムを書くための構文、型、演算子、
実行時モデルを参照形式でまとめたものです。

ELiSEは、Jackに似たクラスベースの言語をMSX向けのZ80アセンブリへ変換します。
入力ファイルはクラス単位で記述し、通常は`Main.main`がプログラムの入口になります。

このマニュアルは現在のコンパイラ実装を基準にしています。将来仕様として固定する
予定の機能と、実装上の制約がある機能は「注意」として区別しています。

## 1. 最小プログラム

```els
class Main {
    function void main() {
        Output.printIntLn(7);
        return;
    }
}
```

ソースは次の規則で構成します。

- 1つの`.els`ファイルに1つのクラスを定義する
- クラス名とファイル名は一致させる
- クラス本体を`{`と`}`で囲む
- エントリポイントには通常`class Main`の`function void main()`を使う
- 文の終端には`;`を付ける

## 2. 字句

### 2.1 識別子

クラス名、変数名、関数名、メソッド名、ユーザー定義型名には識別子を使います。
ユーザー定義クラス名は型名としても使用できます。

```els
class Enemy {
    field int x;
}

class Main {
    function void main() {
        var Enemy enemy;
        enemy = Enemy.new();
        return;
    }
}
```

識別子は、予約語やリテラルと同じ名前にしないでください。

### 2.2 コメント

行コメントとブロックコメントを使用できます。

```els
// 行末までがコメント

/*
   複数行コメント
*/
```

コメントはコンパイル時に無視されます。

### 2.3 数値リテラル

10進数、16進数、8進数、2進数を使用できます。

```els
let decimal = 255;
let hexadecimal = 0xFF;
let octal = 0o377;
let binary = 0b11111111;
```

数値はELiSEのVM上では16ビット値として扱われます。MSXのアセンブリ出力で
必要なバイト幅や符号の扱いは、使用するライブラリAPIの仕様にも依存します。

### 2.4 文字列リテラル

```els
Output.printStringLn("HELLO, MSX!");
```

文字列リテラルはコンパイル時にデータ領域へ配置され、実行時には`String`として
扱われます。文字列を動的に確保した場合は、使用後に`dispose()`または
`String.dispose()`を呼び出してください。

## 3. クラス

クラスには、クラス変数、フィールド、サブルーチンを定義できます。

```els
class Player {
    static int total;
    field int x, y;

    constructor Player new(int start_x, int start_y) {
        let x = start_x;
        let y = start_y;
        let total = total + 1;
        return this;
    }
}
```

### 3.1 `static`

`static`はクラスに1つだけ存在する変数です。すべてのインスタンスから共有されます。

```els
static int enemy_count;
```

### 3.2 `field`

`field`はオブジェクトごとに存在するフィールドです。

```els
field int x, y;
field boolean active;
```

メソッド内では、フィールド名を直接参照できます。

```els
let x = x + 1;
```

フィールドはコンパイラ内部では`this`を基準にアクセスされます。

## 4. 型と変数

### 4.1 組み込み型

| 型 | 用途 |
|---|---|
| `int` | 整数。通常の数値演算に使用 |
| `boolean` | 真偽値。内部表現は整数値 |
| `char` | 文字または1文字相当の値 |
| `Array` | ヒープ上のワード配列 |
| `String` | 文字列オブジェクト |
| `void` | 戻り値がないサブルーチンの戻り値型 |

`void`は変数型には使用せず、サブルーチンの戻り値にだけ使用します。

### 4.2 ローカル変数

ローカル変数はサブルーチンの先頭で宣言します。

```els
function void main() {
    var int i, sum;
    var Array values;

    let i = 0;
    let sum = 0;
    return;
}
```

現行パーサーでは、ローカル変数宣言はサブルーチン本体の文より前に置く必要があります。

### 4.3 引数

引数はサブルーチン宣言の括弧内に記述します。

```els
function int add(int left, int right) {
    return left + right;
}
```

引数は呼び出し時に値として渡されます。オブジェクト型や配列型の値は、
オブジェクトへの参照値として扱われます。

## 5. サブルーチン

ELiSEには`constructor`、`function`、`method`の3種類があります。

### 5.1 `function`

`function`はオブジェクトの`this`に依存しないサブルーチンです。

```els
function int add(int x, int y) {
    return x + y;
}
```

クラス名を付けて呼び出します。

```els
let result = Math.abs(-10);
let value = Main.add(1, 2);
```

### 5.2 `method`

`method`はオブジェクトに対して呼び出すサブルーチンです。呼び出し時に対象
オブジェクトが暗黙の`this`引数として渡されます。

```els
method void move(int dx, int dy) {
    let x = x + dx;
    let y = y + dy;
    return;
}
```

呼び出し方は次のとおりです。

```els
player.move(1, 0);
move(1, 0);              // 現在のクラスのメソッド
```

### 5.3 `constructor`

`constructor`は`Memory.alloc`を使ってフィールド数分の領域を確保し、
生成したオブジェクトを`this`として初期化します。

```els
constructor Player new(int x0, int y0) {
    let x = x0;
    let y = y0;
    return this;
}
```

コンストラクタは通常、`return this;`でオブジェクトを返します。

### 5.4 宣言形式

```text
constructor ClassName subroutineName(parameter-list) { statements }
function    return-type subroutineName(parameter-list) { statements }
method      return-type subroutineName(parameter-list) { statements }
```

コンストラクタの戻り値型には、生成対象クラス名を記述します。

## 6. サブルーチン呼び出し

### 6.1 クラス関数

```els
let value = Main.add(10, 20);
do Output.printIntLn(value);
```

### 6.2 オブジェクトのメソッド

```els
var Enemy enemy;

let enemy = Enemy.new(10, 20);
do enemy.move(1, 0);
```

### 6.3 戻り値を使わない呼び出し

戻り値を捨てる呼び出しには`do`を付けます。

```els
do Output.printLn();
do Sound.stop();
```

現行パーサーは、識別子で始まる呼び出しについて`do`を省略した形式も受け付けます。
ただし、戻り値を捨てる意図を明確にするため、新しいコードでは`do`を推奨します。

```els
Output.printIntLn(7);
```

### 6.4 関数とメソッドの呼び分け

`ClassName.name(...)`はクラス関数またはライブラリ関数として解決されます。
変数に対する`object.name(...)`は、その変数の型のメソッドとして解決されます。
同一クラスの`function`を呼ぶ場合も、`Main.playNote(...)`のようにクラス名を
明示します。クラス名を省略した呼び出しはメソッド呼び出しとして扱われます。

```els
let result = Math.abs(value);
do player.move(1, 0);
do Main.playNote(190, 254, 762, 6);
```

## 7. 文

### 7.1 代入

基本形は`let`を使う代入です。

```els
let score = 0;
let score = score + 10;
```

現行実装では、`let`を省略した代入も使用できます。

```els
score = score + 1;
```

新しいコードでは、代入であることを明確にするため`let`を推奨します。

### 7.2 配列要素への代入

```els
let values[0] = 10;
let values[index] = value + 1;
```

配列の添字は16ビットワード単位で計算されます。`values[1]`は、
配列先頭から2バイト先の要素を意味します。

### 7.3 条件分岐

```els
if (score < 10) {
    do Output.printStringLn("LOW");
}
elif (score == 10) {
    do Output.printStringLn("TEN");
}
else {
    do Output.printStringLn("HIGH");
}
```

`elif`はELiSEの拡張構文です。複数の`elif`を連続して記述できます。

条件式は、0を偽、0以外を真として扱います。比較演算子は真偽値相当の
16ビット値を生成します。

### 7.4 `while`

```els
let i = 0;
while (i < 10) {
    do Output.printIntLn(i);
    let i = i + 1;
}
```

`while`の条件を毎回評価し、偽になった時点でループを終了します。

### 7.5 `return`

戻り値がない場合:

```els
return;
```

値を返す場合:

```els
return x + y;
```

戻り値型が`void`のサブルーチンでは`return;`を使用します。

## 8. 式と演算子

### 8.1 優先順位

式は次の優先順位で評価されます。優先順位が同じ演算子は左から処理されます。

| 優先順位 | 演算子 |
|---:|---|
| 高 | `*` `/` `%` |
|  | `+` `-` |
|  | `<<` `>>` |
|  | `&` |
|  | `|` |
| 低 | `<` `>` `==` `<=` `>=` `!=` |

括弧を使って評価順を明示できます。

```els
let value = (a + b) * 2;
if ((x <= 10) & (y != 0)) {
    return;
}
```

### 8.2 算術演算

| 演算子 | 意味 |
|---|---|
| `+` | 加算 |
| `-` | 減算 |
| `*` | 乗算 |
| `/` | 除算 |
| `%` | 剰余 |

乗算、除算、剰余は、生成コード上では`MSXMath`ライブラリを呼び出します。
ただし、右辺が2のべき乗の整数リテラルである乗算は、コンパイラが定数シフトへ
変換する場合があります。

```els
let pixel = cell * 8;    // shl_const 3へ変換
```

### 8.3 ビット演算

| 演算子 | 意味 |
|---|---|
| `&` | ビットAND |
| `|` | ビットOR |
| `~` | ビット反転 |

```els
let masked = value & 0x0F;
let flags = flags | 0x01;
let inverted = ~value;
```

### 8.4 比較演算

```els
if (x < limit) { return; }
if (x > limit) { return; }
if (x == limit) { return; }
if (x <= limit) { return; }
if (x >= limit) { return; }
if (x != limit) { return; }
```

### 8.5 単項演算

```els
let negative = -value;
let inverted = ~value;
let i = ++i;
let j = --j;
```

`++`と`--`は、現在の実装では単項演算として扱われます。可読性と互換性の
ため、通常の加減算で書ける場合は次の形式も利用してください。

```els
let i = i + 1;
let j = j - 1;
```

### 8.6 シフト演算

`<<`と`>>`は16ビット値に対する論理シフトです。シフトで空いたビットには
`0`が入り、シフト量が16以上の場合の結果は`0`になります。

```els
let left = value << count;
let right = value >> count;
let masked = value >> 4 & 0x0F;
```

`value >> 4 & 0x0F`は`(value >> 4) & 0x0F`として評価されます。
シフトで失われたビットはELiSEの値として保存・取得されません。
Z80のCフラグを使う演算は、将来の専用`ADC`／`SBC`拡張で扱います。

## 9. 定数

### 9.1 キーワード定数

| 定数 | 意味 |
|---|---|
| `true` | 真。内部値は`-1` |
| `false` | 偽。内部値は`0` |
| `null` | オブジェクト参照なし。内部値は`0` |
| `this` | 現在のオブジェクト |

```els
let running = true;
let object = null;
return this;
```

`true`は論理値としては真ですが、内部表現は16ビット値の`-1`です。
ビット演算や外部ライブラリへ渡す場合は、この点に注意してください。

## 10. 配列と文字列

### 10.1 配列

`Array.new(size)`で配列を確保します。

```els
var Array values;

let values = Array.new(3);
let values[0] = 10;
let values[1] = 20;
let values[2] = values[0] + values[1];

do Output.printIntLn(values.count());
do values.deAlloc();
```

主なAPI:

| 呼び出し | 用途 |
|---|---|
| `Array.new(size)` | `size`個のワード配列を確保 |
| `array.count()` | 配列要素数を取得 |
| `array.deAlloc()` | 配列を解放 |
| `Array.deAlloc(array)` | 配列を解放 |

配列は自動解放されません。所有者が不要になった時点で解放してください。

### 10.2 文字列

```els
var String text;

let text = "HELLO";
do Output.printStringLn(text);
do Output.printIntLn(text.length());
do text.dispose();
```

主なAPI:

| 呼び出し | 用途 |
|---|---|
| `String.new(address, length)` | データ領域から文字列を作成 |
| `text.length()` | 文字列長を取得 |
| `text.charAt(index)` | 指定位置の文字を取得 |
| `text.dispose()` | 文字列を解放 |
| `String.dispose(text)` | 文字列を解放 |

文字列リテラルを出力するだけのコードでは、通常はコンパイラがデータ領域を
管理します。動的な文字列オブジェクトを保持するコードでは、解放漏れに注意してください。

## 11. `dat` データ定義

`dat`は、プログラムのデータ領域へバイト列を配置し、そのラベルを変数へ格納します。

```els
function void init() {
    var int tile_data;

    dat tile_data = db
        0x00, 0x7E, 0x81, 0x00;

    do Memory.LDIRVM(tile_data, 0x0000, 4);
    return;
}
```

ラベル名を明示する形式もあります。

```els
dat stage_data = stage_start db
    0x01, 0x02, 0x03;
```

構文:

```text
dat variable = [label] db|dw|ds value-list;
```

`dat`で指定した変数には、配置データのアドレスが入ります。`Memory.LDIRVM`
などの転送APIへ渡すことで、ROM上のデータをVRAMへコピーできます。

### `dat` の実装上の注意

現行実装は、`db`、`dw`、`ds`を字句上は認識しますが、Parserでは値を
バイト列へ連結する処理が中心です。ワード幅や予約領域としての厳密な意味は
まだ固定されていません。現在のコードでは、データ定義には`db`を使用するのが
最も安全です。

## 12. MSXライブラリの利用

ELiSEのMSX固有機能は、`Lib/*.asm`に実装されたライブラリとして提供されます。
代表的な呼び出しは次のとおりです。

```els
do MSX.screenInit();
do Screen.cls();
do Screen.locate(5, 10);
do Output.printStringLn("READY");

let direction = Keyboard.stick0();
do Sprite.init();
do Sound.init();
do Sound.play3(190, 11, 254, 7, 762, 8, 6);
do Timer.waitFrames(6);
do Sound.stop();
```

詳しい関数一覧は[MSXライブラリAPI](libraries.md)を参照してください。

`Sound.play3()`はPSGチャンネルA/B/Cへ、音程・音量・共通の再生フレーム数を
指定します。`Timer.waitFrames()`で同じフレーム数だけ待ってから`Sound.stop()`
を呼べば、短いノート列を演奏できます。

ライブラリ関数の引数と戻り値は、アセンブリ内の`func`宣言から読み取られます。
関数を追加・変更する場合は、実装ラベルと`func`宣言の型・引数を一致させてください。

## 13. メモリと所有権

ELiSEの実行時メモリには、概念上、次の領域があります。

```text
コード・静的データ・文字列
ELiSEランタイムのワーク領域
static変数
ヒープ（Array、String、オブジェクト）
空き領域
スタック
```

`Array.new()`、コンストラクタ、`String.new()`などで確保したオブジェクトは、
不要になったら対応する解放関数を呼び出します。

- 配列: `deAlloc()`
- 文字列: `dispose()`
- 一般メモリ: `Memory.deAlloc()`
- ユーザー定義オブジェクト: クラス側で解放メソッドを用意する

スタックとヒープの配置は、`msxpen`／`cartridge`、コードサイズ、`--heap_size`
などのビルド設定によって変わります。固定アドレスを前提にせず、必要に応じて
生成された`.lst`とメモリ配置資料を確認してください。

## 14. 推奨するソース構成

小さなプログラム:

```els
class Main {
    function void main() {
        // 変数宣言
        var int value;

        // 初期化
        let value = 7;

        // 処理
        do Output.printIntLn(value);
        return;
    }
}
```

オブジェクトを使うプログラム:

```els
class Main {
    function void main() {
        var Player player;

        let player = Player.new(10, 8);
        do player.run();
        do player.dispose();
        return;
    }
}
```

実装上の互換性を高めるため、次の書き方を推奨します。

- 代入には`let`を付ける
- 戻り値を使わない呼び出しには`do`を付ける
- メソッドは対象オブジェクトを明示して呼び出す
- 配列、文字列、オブジェクトを不要になった時点で解放する
- `dat`では当面`db`を使用する
- `<<`、`>>`は二項演算子として使用する

## 15. コンパイル

プロジェクトルートで、ディレクトリを指定してコンパイルします。

```bash
python elise.py examples/Hello -VB 0
```

通常の出力先は`build/<program>/`です。アセンブルまで行う場合:

```bash
python elise.py examples/Hello --assemble -VB 0
```

カートリッジ形式で実行する場合:

```bash
python elise.py examples/Hello \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    -VB 0
```

主なCLIオプション:

| オプション | 意味 |
|---|---|
| `-O`, `--org` | プログラム開始アドレス |
| `-S`, `--stack` | 初期スタックポインタ |
| `-H`, `--heap` | ヒープ開始アドレス |
| `-HS`, `--heap_size` | ヒープサイズ |
| `-A`, `--assemble` | zasmでアセンブル |
| `--run` | openMSXで実行 |
| `--machine` | openMSXの機種名 |
| `-MD`, `--media` | `msxpen`または`cartridge` |
| `-CS`, `--cartridge_size` | カートリッジ容量 |
| `--breakpoint` | 関数ブレークポイント。複数指定可 |
| `-VB`, `--verbose` | メッセージ出力レベル |

デフォルトの`msxpen`形式は`org=0x8100`、スタック初期値は`0xDC60`です。
`cartridge`形式では、明示的に上書きしない限り`org=0x4000`が使われます。

## 16. エラーになりやすい例

### クラス名とファイル名が異なる

```text
Enemy.els -> class Enemy
```

クラス名とファイル名を揃えてください。

### `function`をオブジェクトなしで呼び出せない

クラス関数はクラス名を付けて呼び出します。

```els
let value = Main.add(1, 2);
```

### メソッドの`this`がない

メソッド呼び出しには対象オブジェクトが必要です。

```els
do enemy.move(1);
```

### 配列を解放しない

```els
let values = Array.new(100);
// 使用後:
do values.deAlloc();
```

### VRAMへCPUメモリAPIで書き込む

`Memory.poke*`はCPUメモリ用です。VRAMへ書く場合は`Memory.vpoke*`または
`Memory.LDIRVM`を使用します。

## 17. 関連資料

- [言語仕様の概要](language.md)
- [MSXライブラリAPI](libraries.md)
- [現場利用マニュアル](usage.md)
- [MSXメモリ配置とELiSEの対応](msx-memory-layout-and-elise.md)
- [ブロック崩しチュートリアル](breakout-tutorial.md)
