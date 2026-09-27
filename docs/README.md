# ELiSE ドキュメント

## 利用者向け

- [プロジェクト概要](../README.md)
- [ELiSEリファレンスマニュアル](reference-manual.md)
- [ELiSE言語仕様](language.md)
- [MSXライブラリAPI](libraries.md)
- [ブロック崩しチュートリアル](breakout-tutorial.md)
- [デバッグ手順](debugging.md)
- [現場利用マニュアル](usage.md)
- [開発・テスト手順](development.md)

## 実装者向け

- [アーキテクチャ](architecture.md)
- [MSXメモリ配置とELiSEライブラリの対応](msx-memory-layout-and-elise.md)

## 音声サンプル

- [SoundProbe：PSG 3チャンネルとTimerの併用確認](../examples/SoundProbe/README.md)
- [SoundSample：3チャンネルのオリジナル8bitテーマ](../examples/SoundSample/README.md)

## ゲームサンプル

- [Breakout2：PSG A/Cの2音BGMとBチャンネル効果音](../examples/Breakout2/README.md)

## 読み方

最初にプロジェクト概要を読み、次に言語仕様とライブラリAPIを確認してください。

コンパイラ本体を変更する場合は、アーキテクチャで処理段階と責務を確認し、開発・テスト手順で検証方法を確認します。

このドキュメント群は、公開しているELiSE-originalの実装を説明するものです。
仕様として固定されていない挙動や、まだテストが不足している機能は、各資料で明記します。
