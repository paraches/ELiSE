# SoundProbe

ELiSEの`Sound`ライブラリを使って、MSXのPSGから3和音を再生するサンプルです。
`Timer`と同時に使用しても、BIOSのVBlank処理を妨げないことを確認します。

## なぜ作成したか

効果音をBreakoutへ組み込む前に、次の機能を単体で確認するために作成しました。

- `Sound.init()`によるPSG初期化
- `Sound.play3(periodA, volumeA, periodB, volumeB, periodC, volumeC, frames)`による3チャンネル再生
- `Sound.stop()`による停止
- `Timer.waitFrames()`との併用

SoundProbeでは、ELiSEのコンパイラと`Lib/Sound.asm`を経由した場合に、
PSGのチャンネルA/B/Cを同時に再生できることを確認します。

## 動作内容

1. Screen 2を初期化する
2. `Sound.init()`を呼び出す
3. PSGチャンネルA/B/Cで周期値`254`、`320`、`381`、音量`10`の3和音を180フレーム再生する
4. `Sound.stop()`で停止する
5. 画面に`DONE`を表示する

`Timer.waitFrames(180)`を使っているため、映像規格に応じて約3秒間再生します。
PSGのミキサはI/OポートBを出力のまま保つため、VBlank中のBIOSキーボード／
ジョイスティック処理とも共存します。

## ビルド

プロジェクトルートで実行します。

```sh
.venv/bin/python elise.py examples/SoundProbe \
  --media cartridge \
  --assemble \
  -VB 0
```

## 起動

```sh
openmsx -machine 'C-BIOS_MSX2+' \
  -carta build/SoundProbe/SoundProbe.rom
```

画面に`PSG 3CH + TIMER`が表示されている間に3和音が鳴り、終了後に`DONE`が
表示されれば、PSG 3チャンネルとタイマの併用を確認できます。
