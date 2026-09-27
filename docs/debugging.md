# ELiSE デバッグ手順

この資料は、ELiSEで作成したMSXプログラムをopenMSXでデバッグするための
実作業手順と、Breakoutで実際に発生した性能問題の調査記録です。

## 1. 基本方針

デバッグは次の順序で行います。

```text
.elsの動作
  ↓
VM出力
  ↓
生成ASM
  ↓
zasmのlisting
  ↓
openMSXのCPU・メモリ・画面
```

画面の症状だけで判断せず、まず「どの処理が実行される条件で症状が出るか」を
特定します。今回のBreakoutでは、球がブロック領域に入った時だけ処理が重くなる
ことが重要な手掛かりになりました。

## 2. 再ビルドとopenMSX起動

古いROMを実行しないように、openMSXの起動中インスタンスを終了してから、
プロジェクトルートで次を実行します。

```bash
source .venv/bin/activate

python elise.py examples/Breakout \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    -VB 0
```

ROMだけを作る場合:

```bash
python elise.py examples/Breakout --assemble -VB 0
```

成果物は次の場所に生成されます。

```text
build/Breakout/Breakout.rom
build/Breakout/Breakout.asm
build/Breakout/Breakout.lst
build/Breakout/Breakout.symbols.json
build/Breakout/logs/emulator.log
```

## 3. 関数ブレークポイント

特定のELiSE関数で停止させる場合は、関数名を指定します。

```bash
python elise.py examples/Breakout \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    --breakpoint Breakout.updateBall \
    -VB 0
```

複数指定もできます。

```bash
--breakpoint Breakout.updateBall \
--breakpoint Breakout.restoreCell
```

生成された`.tcl`には、`symbols.json`から解決した実アドレスの
openMSXブレークポイントが記録されます。

## 4. symbols.jsonとlistingの使い分け

`symbols.json`はELiSEのソース、VM、ASM、アセンブル後のアドレスを結びつけます。

```bash
python -m json.tool build/Breakout/Breakout.symbols.json | less
```

`*.lst`はzasmが確定した機械語とアドレスを確認するために使います。

```bash
rg -n "Breakout.updateBall|Breakout.restoreCell" \
    build/Breakout/Breakout.lst
```

調査対象の対応は次のように追います。

```text
Breakout.elsの行
  → build/Breakout/Main.vm または Breakout.vm
  → build/Breakout/Breakout.asmのsourceコメント
  → Breakout.lstの実アドレスと機械語
```

## 5. openMSX制御インターフェース

PythonからopenMSXを起動して、CPUレジスタ、メモリ、停止状態を読むこともできます。

```python
from elise.OpenMSXControl import OpenMSXControlSession

session = OpenMSXControlSession.launch(
    "build/Breakout/Breakout.rom",
    machine="C-BIOS_MSX2+",
)

print(session.debug_breaked().text.strip())
print(session.debug_registers())
session.debug_break()
print(session.debug_read_memory(0x8000, 32))
session.close()
```

実行時のメモリを読む場合は、`symbols.json`のランタイムラベルを使います。
カートリッジ形式では、`sys_*`や`heap`などのランタイム領域がRAM側に割り当てられます。

## 6. Breakoutの性能問題を調査する手順

### 6.1 症状を条件に分解する

次のように、症状が発生する条件を分けます。

- 球がブロック領域の外にいる時
- 球がブロック領域に入った時
- ブロックを消す瞬間
- 消えたブロックの場所を球が通過する時
- 枠やパドルに当たった時

今回の症状は「ブロック領域内でだけ、1回進んで止まり、数回進んで止まる」
というものだった。これは入力処理や衝突判定の結果というより、フレーム内の
処理時間が場所によって変わっている可能性を示していました。

### 6.2 VBlank待ちとの関係

現在のゲームループは次の順序です。

```els
do readInput();
do updateBall();
do draw();
do Timer.waitFrames(1);
```

`Timer.waitFrames(1)`は標準MSXで約1/60秒待つ。したがって、
`updateBall()`や`draw()`に時間がかかって複数のVBlankをまたぐと、処理は
次のようになります。

```text
重いフレーム処理
  → 2〜3回のVBlankを消費
  → Timer.waitFrames(1)でさらに1回待つ
  → 球が数フレーム分まとめて止まったように見える
```

このため、症状が「VBlank待ちで停止している」ように見えても、実際には
VBlank待ちそのものではなく、待ちに到達する前の処理が重い場合があります。

### 6.3 高コスト処理を探す

ELiSEでは乗算演算子`*`が、通常のZ80命令ではなく`MSXMath.multiply`への
呼び出しになります。

```bash
rg -n "MSXMath.multiply|multiply" \
    build/Breakout/Breakout.asm \
    build/Breakout/Breakout.lst
```

今回の元コードには、次の処理がありました。

```els
let brick_index = (next_y - brick_top) * 26;
```

これは次の2箇所で実行されていました。

- `updateBall()`の衝突判定
- `restoreCell()`の古い球をブロックへ戻す処理

つまり、ブロック領域に入った時だけ乗算ライブラリ呼び出しが発生していました。
その結果、球がブロック領域にいる間だけフレーム処理がVBlankをまたいでいました。

### 6.4 実施した修正

ブロックは4行固定なので、行ごとのオフセットを条件分岐で計算するようにしました。

```els
let brick_index = next_x - brick_left;
if (next_y == brick_top + 1) {
    let brick_index = brick_index + 26;
}
elif (next_y == brick_top + 2) {
    let brick_index = brick_index + 52;
}
elif (next_y == brick_top + 3) {
    let brick_index = brick_index + 78;
}
```

同じ変更を`restoreCell()`にも適用しました。

修正後は次のコマンドで、Breakout専用の乗算呼び出しがないことを確認します。

```bash
if rg -q "MSXMath.multiply" build/Breakout/Breakout.asm; then
    echo "multiply call remains"
else
    echo "no Breakout multiply call"
fi
```

## 7. Timerを疑う時の確認

Timerは`H.TIMI`を書き換えません。`Timer.waitFrames()`は割り込み状態に依存しない
Z80待機ループを使い、`Timer.ticks()`だけがBIOSの`JIFFY (0xFC9E)`を読みます。

確認用サンプル:

```bash
python elise.py examples/TimerProbe \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    -VB 0
```

Timer実装を変更した場合は、次を確認します。

- `Timer.ticks()`の値が進む
- `Timer.waitFrames(1)`が約1/60秒で復帰する
- 50Hz/60Hzの差を秒数ではなくフレーム数として扱える
- H.TIMIを上書きしていない

## 8. よくある症状と切り分け

| 症状 | 最初に確認すること |
|---|---|
| 起動直後に止まる | `Timer.waitFrames()`、ROMの再生成 |
| 特定の場所だけ遅い | 条件分岐内の乗算、文字列出力、`Screen.locate` |
| 画面だけ更新されない | `draw()`、`restoreCell()`、VRAM書き込み |
| ブロック消去後に表示が戻る | `bricks[index]`と添字計算 |
| ブレークポイントで止まらない | 関数名、symbols.json、最新ROMかどうか |
| openMSXがカートリッジを認識しない | `--media cartridge`、ROMヘッダ、起動中インスタンス |

## 9. 検証チェックリスト

```bash
python elise.py examples/Breakout --assemble -VB 0
cd test
PYTHONPATH=../src ../.venv/bin/python \
    -m unittest discover -s . -p 'test_*.py'
cd ..
git diff --check
```

最後に、古いROMを実行していないことを確認してopenMSXで2ゲーム程度プレイします。
特定の領域だけ遅い場合は、画面の見た目ではなく、その領域でだけ実行される
ソース行と生成ASMのライブラリ呼び出しを比較します。
