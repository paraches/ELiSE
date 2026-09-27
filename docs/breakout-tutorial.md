# ELiSEチュートリアル: ブロック崩しを作る

このチュートリアルでは、ELiSEで小さなブロック崩しを作ります。

完成したサンプルは次の場所にあります。

```text
examples/Breakout/
├── Main.els
└── Breakout.els
```

## 1. 完成版を動かす

プロジェクトルートで実行します。

```bash
python elise.py examples/Breakout \
    --assemble \
    -VB 0
```

カートリッジ形式でopenMSXを起動する場合は、次のコマンドです。

```bash
python elise.py examples/Breakout \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    -VB 0
```

方向キーまたはジョイスティックの左右でパドルを動かします。
`STOP`キーでゲームループを停止できます。

盤面、壁、ブロック、状態表示には32×24文字画面を使い、
ボールとパドルにはスプライトを使います。そのため、画像データを
準備しなくても、ゲームループ、入力、配列、衝突判定を学習できます。

## 2. ELiSEプログラムの基本形

ELiSEのプログラムはクラスから始まり、通常は`Main.main`がエントリポイントです。

```els
class Main {
    function void main() {
        var Breakout game;

        game = Breakout.new();
        game.run();
        return;
    }
}
```

`var Breakout game;`でユーザー定義クラスの変数を宣言し、
`Breakout.new()`でコンストラクタを呼び出しています。

`Main.els`と`Breakout.els`のクラス名は一致させます。

## 3. ゲームの状態をフィールドで持つ

```els
class Breakout {
    field int field_left, field_right, field_top, field_bottom;
    field int brick_left, brick_right, brick_top, brick_bottom;
    field int paddle_width;
    field Array bricks;
    field int paddle_x;
    field int ball_x, ball_y;
    field int ball_dx, ball_dy;
    field int score, lives;
    field boolean running;
```

`field`はゲームオブジェクトが持つ状態です。

- `bricks`: ブロックが残っているかを格納する配列
- `paddle_x`: パドルの左端
- `ball_x`, `ball_y`: ボールの位置
- `ball_dx`, `ball_dy`: 1フレームごとの移動量
- `score`, `lives`: スコアと残機
- `running`: ゲームループの継続状態

画面の固定値も`field`にしています。このサンプルはゲームオブジェクトを
1つだけ作るため、ゲームの状態を同じオブジェクトへまとめています。
ブロックは4行×26列なので、配列の要素数は104です。

## 4. コンストラクタで初期化する

```els
constructor Breakout new() {
    var int i;

    let bricks = Array.new(104);
    let i = 0;
    while (i < 104) {
        let bricks[i] = 1;
        let i = i + 1;
    }

    let paddle_x = 13;
    let score = 0;
    let lives = 3;
    let running = true;

    do resetBall();
    do initScreen();
    return this;
}
```

`Array.new(104)`でワード配列を確保します。
配列の添字は次のように使います。

```els
let bricks[index] = 1;
if (bricks[index] == 1) {
    // ブロックが残っている
}
```

コンストラクタの最後は`return this;`にします。

## 5. MSX画面を初期化する

```els
method void initScreen() {
    do MSX.screenInit();
    do MSX.keyClick(false);
    do Screen.color(15, 1, 1);
    do Screen.cls();
    return;
}
```

`MSX.screenInit()`はMSXの画面とVDPを初期化します。
このサンプルでは、文字を配置するために`Screen.locate`と
`Screen.putch`を使います。

```els
method void putCell(int x, int y, int value) {
    do Screen.locate(x, y);
    do Screen.putch(value);
    return;
}
```

`value`にはASCIIコードを渡します。

- `35`: `#`、ブロック
- `61`: `=`、パドル
- `111`: `o`、ボール
- `124`: `|`、左右の壁
- `45`: `-`、上下の壁

## 6. ゲームループを作る

```els
method void run() {
    do Timer.start();

    while (running) {
        do readInput();
        do updateBall();
        do draw();
        do Sound.update();
        do Timer.waitFrames(1);

        if (Keyboard.isStopKey()) {
            let running = false;
        }
    }

    do Timer.stop();
    do Sound.stop();
    do showGameOver();
    do bricks.deAlloc();
    return;
}
```

ゲームループは、入力、状態更新、描画、ウェイトの順に実行します。
`while (running)`と`boolean`を組み合わせることで、停止条件を明確にできます。

## 7. キーボード入力でパドルを動かす

```els
method void readInput() {
    var int direction;

    let direction = Keyboard.stick0();

    if (direction == 7) {
        let paddle_x = paddle_x - 1;
    }
    elif (direction == 3) {
        let paddle_x = paddle_x + 1;
    }

    if (paddle_x < brick_left) {
        let paddle_x = brick_left;
    }
    if (paddle_x > brick_right - paddle_width + 1) {
        let paddle_x = brick_right - paddle_width + 1;
    }
    return;
}
```

`Keyboard.stick0()`の方向値は、ELiSEのライブラリ仕様では
右が`3`、左が`7`です。

画面端を越えないように、最後にパドル位置を範囲内へ戻しています。
このような処理をクランプと呼びます。

## 8. ボールとブロックの衝突判定

ボールの次の位置を先に計算します。

```els
let next_x = ball_x + ball_dx;
let next_y = ball_y + ball_dy;
```

左右の壁に当たったら、X方向の速度を反転します。

```els
if (next_x <= field_left) {
    let ball_dx = 1;
    let next_x = field_left;
}
elif (next_x >= field_right) {
    let ball_dx = -1;
    let next_x = field_right;
}
```

ブロックの配列番号は、画面上の行と列から計算します。

```els
let brick_index = (next_y - brick_top) * 26;
let brick_index = brick_index + next_x - brick_left;
```

ブロックが残っていれば`0`に変更し、スコアを加算してボールを反転します。

```els
if (bricks[brick_index] == 1) {
    let bricks[brick_index] = 0;
    let score = score + 10;
    let ball_dy = -ball_dy;
}
```

## 9. パドル・ミス・残機

ボールがパドルの範囲に入ったら、下向きの移動を上向きに反転します。

```els
if ((next_y == field_bottom - 2) &
    (next_x >= paddle_x) &
    (next_x < paddle_x + paddle_width)) {
    let ball_dy = -1;
}
```

ボールが画面下端を越えたら残機を減らします。

```els
elif (next_y >= field_bottom) {
    let lives = lives - 1;
    if (lives == 0) {
        let running = false;
    }
    else {
        do resetBall();
        return;
    }
}
```

このサンプルでは、角度計算や速度の小数化は行っていません。
ボールは1フレームに1セル動くため、最初の教材として衝突判定を追いやすくしています。

## 10. 初回描画と差分描画

画面全体の再描画は、文字セルを使うMSXプログラムでは非常に遅くなります。
そのため、現在のサンプルは初回だけ盤面全体を描画し、ゲームループ中は変更されたセルだけを描画します。

初回の盤面描画では、次の順番で描画します。

```els
method void drawBoard() {
    var int row, col;

    do drawBorder();

    let row = brick_top;
    while (row <= brick_bottom) {
        let col = brick_left;
        while (col <= brick_right) {
            do putCell(col, row, 35);
            let col = col + 1;
        }
        let row = row + 1;
    }

    do drawPaddle();
    do putCell(ball_x, ball_y, 111);
    return;
}
```

ゲームループ内の`draw()`では、前のボールとパドルだけを消し、新しい位置へ描画します。

```els
method void draw() {
    var int col;

    do restoreCell(drawn_ball_x, drawn_ball_y);

    let col = 0;
    while (col < paddle_width) {
        do putCell(drawn_paddle_x + col, field_bottom - 1, 32);
        let col = col + 1;
    }

    do drawPaddle();
    do putCell(ball_x, ball_y, 111);
    do drawStatus();

    let drawn_paddle_x = paddle_x;
    let drawn_ball_x = ball_x;
    let drawn_ball_y = ball_y;
    return;
}
```

`restoreCell()`は、前のボール位置がまだブロックなら`#`を戻し、それ以外なら空白を書きます。
これにより、ボールの移動でブロックや枠を誤って消さずに済みます。

この方式では、毎フレームの描画回数が「盤面全体の数百セル」から「ボール、パドル、ステータスなどの変更箇所」へ減ります。
文字単位の`Screen.locate()`と`Screen.putch()`を使う構成でも、ゲームとして操作できる速度になります。

## 11. フレームウェイト

現在のランタイムには`Timer.waitFrames()`があり、標準MSXでフレーム単位に
相当する待機ができます。現行のBreakoutサンプルでは、
ゲームループごとに次の呼び出しを行います。

```els
do Timer.waitFrames(1);
```

空ループで待つ方式と異なり、実行環境のCPU速度に依存しにくい方法です。

## 12. スプライトを使う

現行の実装では、ボールを8×8スプライト1個、
パドルを8×8スプライト4個で表示します。
壁、ブロック、スコア、残機は文字画面に残します。

スプライトはパターンデータをVRAMへ転送してから、
`Sprite.put(x, y, table, color, number)` で属性を更新します。
Breakoutでは論理座標と表示用ピクセル座標を分け、移動時に表示座標を
8ピクセルずつ更新します。描画フレームごとの乗算を避けるためです。

ブロックをすべてスプライトにすると同時表示数の制約にかかるため、
次の段階で背景タイルへの移行を検討します。

## 13. 次の発展

このサンプルを動かした後は、次の順で拡張できます。

1. ブロックを16×16パターンまたは背景タイルで描画する
2. ボールの角度をパドルの当たった位置で変える
3. ステージデータを`dat`で定義する
4. スコアや残機を独自フォントで表示する

この順序にすると、ELiSEの基本構文を確認してから、
MSX固有のVRAM・スプライト・データ定義へ進めます。
