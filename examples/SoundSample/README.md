# SoundSample

`Sound.play3()`と`Timer.waitFrames()`を使う、オリジナルの短い8bit戦闘風テーマです。
既存のゲーム曲の旋律は使用していません。

## チャンネル構成

| PSGチャンネル | 役割 | 音量 |
|---|---|---|
| A | 主旋律 | 11 |
| B | 和音 | 7 |
| C | 低音 | 8 |

各ノートは`Main.playNote()`でPSGへ書き込み、指定フレーム数だけ
`Timer.waitFrames()`で待機します。60Hz環境では6フレームがおよそ0.1秒です。

## ビルド

```sh
.venv/bin/python elise.py examples/SoundSample \
  --media cartridge \
  --assemble \
  -VB 0
```

## 起動

```sh
openmsx -machine 'C-BIOS_MSX2+' \
  -carta build/SoundSample/SoundSample.rom
```

画面に`ORIGINAL BATTLE THEME`が表示されている間に演奏され、終わると`DONE`を表示します。
