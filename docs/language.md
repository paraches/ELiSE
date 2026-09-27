# ELiSE 言語仕様

この資料は、現在の`Token.py`、`Tokenizer.py`、`Parser.py`と`test/**/*.els`の実装をもとにした仕様です。

## 1. 基本構造

ELiSEのソースはクラス単位で記述します。

```els
class Main {
    function void main() {
        Output.printIntLn(1 + 2 * 3);
        return;
    }
}
```

## 2. クラスと変数

### クラス変数

```els
static int counter;
field int x, y;
```

- `static`: クラスに1つの静的変数
- `field`: オブジェクトごとのフィールド

### ローカル変数

```els
function void main() {
    var int i, sum;
    var Array values;
    return;
}
```

### 型

組み込み型:

- `int`
- `boolean`
- `char`
- `Array`
- `String`
- `void`（戻り値のみ）

識別子も型として扱われるため、ユーザー定義クラスを変数型に使用できます。

```els
var Enemy enemy;
field Player player;
```

## 3. サブルーチン

```els
constructor Enemy new(int x, int y) {
    return this;
}

function int add(int x, int y) {
    return x + y;
}

method void move(int direction) {
    return;
}
```

- `constructor`: `Memory.alloc`でフィールド数分の領域を確保し、`this`を設定
- `function`: オブジェクトに依存しない関数
- `method`: 第0引数を`this`として扱うメソッド

呼び出し方:

```els
Main.add(1, 2);       // クラス関数
enemy.move(1);        // オブジェクトのメソッド
move(1);              // 現在のクラスのメソッド
```

## 4. 文

### 代入

通常の形式:

```els
let value = 10;
```

テストコードでは`let`を省略した形式も使用されています。

```els
value = 10;
```

配列:

```els
values[0] = 10;
values[index] = value + 1;
```

### 呼び出し

```els
do Output.printIntLn(value);
Output.printIntLn(value);
```

現行Parserは識別子で始まる文を呼び出しまたは代入として解釈するため、`do`を省略した形式も受け付けます。新しいコードでは読みやすさのため、戻り値を捨てる呼び出しには`do`を推奨します。

### 条件分岐

```els
if (value == 0) {
    Output.printStringLn("zero");
}
elif (value == 1) {
    Output.printStringLn("one");
}
else {
    Output.printStringLn("other");
}
```

`elif`はELiSEの拡張構文です。

### ループ

```els
while (i < count) {
    i = i + 1;
}
```

### return

```els
return;
return value;
```

## 5. リテラルと定数

```els
1234       // 10進
0xFF       // 16進
0o377      // 8進
0b1010     // 2進
"MSX"      // 文字列
true
false
null
this
```

文字列はVM段階で`String.new`相当の処理に変換され、最終アセンブリのデータ領域へ配置されます。

## 6. 演算子

### 算術・論理

| 優先度 | 演算子 | 備考 |
|---|---|---|
| 高 | `*` `/` `%` | `MSXMath`を呼ぶ演算を含む |
|  | `+` `-` | 左から処理 |
|  | `<<` `>>` | 16ビット論理シフト |
|  | `&` | ビットAND |
|  | `|` | ビットOR |
| 比較 | `<` `>` `==` `<=` `>=` `!=` | 真偽値相当の16ビット値を生成 |
| 単項 | `-` `~` `++` `--` | `++`／`--`は拡張演算 |

例:

```els
result = (a + b) * 2;
if ((x <= 10) & (y != 0)) {
    return;
}
```

`<`、`>`、`==`などはTokenizer内部で専用トークンへ変換されます。

### シフト演算

`<<`と`>>`は16ビット論理シフトです。シフトで空いたビットには`0`が入り、
シフト量が16以上の場合の結果は`0`になります。

```els
let left = value << count;
let right = value >> count;
let masked = value >> 4 & 0x0F;
```

`value >> 4 & 0x0F`は`(value >> 4) & 0x0F`として評価されます。
シフトで失われたビットをELiSEのランタイムへ保存する機能はありません。
右辺が2のべき乗の整数リテラルである乗算は、コンパイラによって定数シフトへ
変換される場合があります。

## 7. データ定義

MSXのROM／データ領域に配置するバイト列を`dat`で定義できます。

```els
function void init() {
    var int font;
    dat font = db 0x00, 0x7E, 0x81, 0x00;
    return;
}
```

ラベルを明示する形式もあります。

```els
dat data = stage_data db 0x01, 0x02, 0x03;
```

現在の実装では`db`、`dw`、`ds`がトークンとして認識されますが、Parserはデータを16進文字列へまとめて配置する処理が中心です。ワード幅や予約領域としての`ds`の厳密な意味は、今後仕様として整理する必要があります。

## 8. コメント

```els
// 行コメント

/*
   ブロックコメント
*/
```

## 9. 配列と文字列のモデル

### 配列

`Array.new(size)`で確保し、要素は16ビットワードとして格納します。

```els
var Array a;
a = Array.new(3);
a[0] = 10;
Output.printIntLn(a[0]);
a.deAlloc();
```

配列添字はアドレス計算時に2倍されます。

### 文字列

```els
var String text;
text = "HELLO";
Output.printStringLn(text);
Output.printIntLn(text.length());
text.dispose();
```

文字列はヒープ上のオブジェクトとして扱われ、使用後は`dispose()`で解放します。

## 10. 命名と実装上の注意

- クラス名とファイル名は一致させる
- エントリポイントは通常`Main.main`
- `method`では暗黙の`this`引数が追加される
- `constructor`は`return this;`で返す
- `Array`、`String`などのランタイムオブジェクトは明示的に解放する
- ライブラリ関数名は`Lib/*.asm`の`func`宣言と一致させる
