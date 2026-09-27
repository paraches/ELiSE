# Breakout2

Breakoutを元にした、BGMと効果音を独立再生するブロック崩しです。
ゲーム操作と画面表示はBreakoutと同じです。

## 効果音の割り当て

| イベント | PSGチャンネル | 関数 |
|---|---|---|
| パドル・ブロック・壁・天井に当たる | B | `Sound.playB()` |
| ボールを落とす | B | `Sound.playB()` |

## BGMの割り当て

| PSGチャンネル | 役割 | 音量 |
|---|---|---|
| A | 主旋律 | 10 |
| C | 低音 | 8 |

`Sound.playAC()`でA/CのBGMを同時に鳴らします。Bチャンネルの効果音は
BGMを中断せず、以前の単音BGMより大きい音量で再生されます。

## 操作

| キー | 操作 |
|---|---|
| ← / → | パドル移動 |
| STOP | 終了 |

## ビルド

```sh
.venv/bin/python elise.py examples/Breakout2 \
  --media cartridge \
  --assemble \
  -VB 0
```

## 起動

```sh
openmsx -machine 'C-BIOS_MSX2+' \
  -carta build/Breakout2/Breakout2.rom
```

## 32K ROM

既定の16K版を残したまま32K ROMを作るには、容量と出力先を指定します。

```sh
.venv/bin/python elise.py examples/Breakout2 \
  --media cartridge \
  --cartridge_size 32768 \
  --build build/Breakout2-32K \
  --assemble \
  -VB 0
```

生成先は`build/Breakout2-32K/Breakout2/Breakout2.rom`です。32K版ではROMが
`0x4000`から`0xBFFF`を使い、実行時ワークエリアは`0xC000`から確保されます。

```sh
openmsx -machine 'C-BIOS_MSX2+' \
  -carta build/Breakout2-32K/Breakout2/Breakout2.rom
```
