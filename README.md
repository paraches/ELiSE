# ELiSE

ELiSE（Easy Language in Small Environment）は、8bitの歴史あるパーソナルコンピュータであるMSXのような小さな実行環境で動作する、シンプルな言語を目指して設計されています。

Nand2Tetrisの学習過程でPythonを使って実装した`Jack`を出発点に、その言語でMSXのマシン語を動かしてみたいと考えたことが、ELiSEを作り始めたきっかけです。現在は、Jackに似たクラスベース言語をMSX向けのZ80アセンブリへ変換するクロスコンパイラとして実装されています。

入力した`.els`ソースは、いったんELiSE独自のVM命令へ変換され、その後Z80/MSXアセンブリへ変換・リンクされます。生成されたZ80アセンブリコードは`zasm`でアセンブルし、生成されたROMをopenMSXで実行できます。

サンプルとしてブロック崩し（Breakout、Breakout2）のコードもあります。

```text
.els
  -> Tokenizer
  -> SymbolTableCreator
  -> Parser / Analyzer
  -> build/<program>/*.vm
  -> ASMTranslator / AsmWriter
  -> build/<program>/*.asm
```

## クイックスタート

プロジェクトルートで仮想環境を作成します。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

サンプルをカートリッジ形式でアセンブルします。

```bash
python elise.py examples/Hello \
    --media cartridge \
    --assemble \
    -VB 0
```

成果物は `build/Hello/` に作成されます。

```text
build/Hello/Main.vm
build/Hello/Hello.asm
build/Hello/Hello.rom
build/Hello/Hello.lst
build/Hello/Hello.symbols.json
```

テストを実行する場合は、現在のテストコードが `../Lib` という相対パスを使用するため、`test/` をカレントディレクトリにします。

```bash
cd test
PYTHONPATH=../src ../.venv/bin/python -m unittest discover -s . -p 'test_*.py'
```

## リポジトリ構成

```text
ELiSE/
├── elise.py             # ルートCLIエントリポイント
├── src/elise/           # コンパイラ本体パッケージ
├── examples/             # 利用者向けサンプル
├── Lib/                  # MSXランタイムライブラリ
├── test/                 # .elsのテスト入力とPythonテスト
├── build/                # コンパイル成果物（Git管理外）
├── docs/                 # 詳細ドキュメント
└── .vscode/              # VS Code設定
```

## ドキュメント

- [ドキュメント一覧](docs/README.md)
- [ELiSEリファレンスマニュアル](docs/reference-manual.md)
- [アーキテクチャ](docs/architecture.md)
- [ELiSE言語仕様](docs/language.md)
- [MSXライブラリAPI](docs/libraries.md)
- [ブロック崩しチュートリアル](docs/breakout-tutorial.md)
- [デバッグ手順](docs/debugging.md)
- [現場利用マニュアル](docs/usage.md)
- [開発・テスト手順](docs/development.md)

## 現在の範囲

実装済みの主な範囲は次の通りです。

- クラス、`static`、`field`
- `constructor`、`function`、`method`
- ローカル変数、引数、配列、文字列
- if / elif / else、while、return
- MSX向けメモリ、画面、キーボード、スプライト、文字列ライブラリ
- PSG 3チャンネル再生とBIOS VBlankタイマを併用するSoundライブラリ
- PSG A/Cの2音BGMとBチャンネル効果音を併用するBreakout2サンプル
- MSXPen用とカートリッジ用の出力環境

ELiSEは`.asm`生成、zasmによるROM生成、openMSXの起動までを自動化できます。実機での動作確認と、openMSX上での詳細なデバッグは別工程です。
