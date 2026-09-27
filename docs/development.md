# ELiSE 開発・テスト手順

## 1. 開発環境

ELiSEはPythonで実装されています。現在、プロジェクト内の`.venv`を使用します。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

外部Pythonパッケージを前提とするコードは現在ありません。依存関係を追加した場合は、`requirements.txt`などの管理ファイルを追加してください。

## 2. コンパイル

プロジェクトルートから実行します。

```bash
python elise.py test/Seven
```

主なオプション:

| オプション | 内容 |
|---|---|
| `-N`, `--asm_name` | 最終アセンブリ名 |
| `-O`, `--org` | アセンブリ開始アドレス |
| `-S`, `--stack` | 初期スタック位置 |
| `-H`, `--heap` | ヒープ開始位置 |
| `-HS`, `--heap_size` | ヒープサイズ |
| `-L`, `--lib` | ライブラリディレクトリ |
| `-B`, `--build` | 成果物の出力先 |
| `-C`, `--clean` | コンパイル後に`.vm`を削除するか |
| `-DB`, `--db` | Debugライブラリをリンクするか |
| `-VB`, `--verbose` | ログレベル |
| `-A`, `--assemble` | 生成した`.asm`をzasmでアセンブル |
| `--assembler` | 使用するアセンブラ実行ファイル |
| `--run` | 生成したROMをopenMSXで起動 |
| `--openmsx` | openMSX実行ファイル |
| `--machine` | openMSXのマシン名 |
| `--breakpoint` | 関数名を指定してopenMSXブレークポイントを生成（複数指定可） |
| `-MD`, `--media` | `msxpen`または`cartridge` |
| `-CS`, `--cartridge_size` | カートリッジ領域サイズ |

zasmがPATHにある場合は、コンパイルとROM／リスト生成を一度に実行できます。

```bash
python elise.py test/Seven --assemble
```

生成物は`build/Seven/Seven.rom`と`build/Seven/Seven.lst`です。アセンブラ実行ファイルは`--assembler`で指定できます。

openMSXをPATHから起動できる環境では、アセンブルと実行を続けて行えます。

```bash
python elise.py test/Seven --run
```

openMSXの場所を明示する場合:

```bash
python elise.py test/Seven --run --openmsx /path/to/openmsx
```

エミュレータのログは`build/Seven/logs/emulator.log`に保存されます。

外部制御をPythonから利用する場合は、コンパイル後のROMに対して次のように接続できます。

```python
from elise.OpenMSXControl import OpenMSXControlSession

session = OpenMSXControlSession.launch(
    "build/Seven/Seven.rom",
    machine="C-BIOS_MSX2+",
)
print(session.debug_list().text)
print(session.debug_breaked().text)
session.debug_break()
print(session.debug_registers())
session.close()
```

`OpenMSXControlSession`では、`debug_step()`、`debug_continue()`、`debug_read()`も利用できます。

スタック、ヒープ、レジスタをまとめて取得する場合:

```python
snapshot = session.runtime_snapshot(
    "build/Seven/Seven.symbols.json",
)
print(snapshot["registers"])
print(snapshot["stack"])
print(snapshot.get("heap"))
```

関数名を指定すると、アセンブル後にopenMSX用のTclスクリプトを生成できます。`--run`と併用すると起動時に読み込まれます。

```bash
python elise.py test/Seven --run \
    --machine 'C-BIOS_MSX2+' \
    --breakpoint Main.main
```

カートリッジ用の例:

```bash
python elise.py test/Seven \
    --media cartridge \
    --org 16384 \
    --build build/cartridge
```

現在のCLIは数値オプションをPythonの`int`として処理するため、アドレスは10進数で指定します。`0x4000`を指定したい場合は、CLIの数値変換処理を`int(value, 0)`へ変更する必要があります。

## 3. テスト

公開版の主なコンパイルテストは`test/test_code.py`にあります。
メモリ管理のPythonテストは`test/Memory_Leak/test_memory_python.py`にあります。

```bash
cd test
PYTHONPATH=../src ../.venv/bin/python -m unittest discover -s . -p 'test_*.py'
```

成功例:

```text
Ran 17 tests ... OK
```

テストは主に、次の処理が例外なく完了することを確認します。

- `.els`の読み込み
- シンボル表作成
- `.vm`生成
- `.asm`生成
- MSXPen環境とカートリッジ環境

MSX実機・エミュレータでの出力比較は別途必要です。

## 4. 成果物

成果物は`build/`に置かれます。

```text
build/
└── Seven/
    ├── Main.vm
    ├── Seven.asm
    ├── Seven.rom
    ├── Seven.lst
    └── Seven.symbols.json
```

`build/`はGit管理外です。テスト入力は`test/`に置き、生成物をそこへ戻さないでください。

ROMやLSTを外部アセンブラが生成する場合も、可能なら同じプログラムのbuildディレクトリへ置きます。

`*.symbols.json`には、ソースのサブルーチン宣言、VMの`function`命令、アセンブリ上の関数ラベルと行番号の対応を記録します。さらに、生成された各VM命令について、ソース行・VM行・ASM行・アセンブル後の実アドレスの対応を`locations`へ記録します。

## 5. ソース変更の確認

Pythonの構文確認:

```bash
.venv/bin/python -m py_compile src/elise/Compiler.py elise.py
```

Git差分の空白確認:

```bash
git diff --check
```

生成物の位置確認:

```bash
find test -type f \( -name '*.vm' -o -name '*.asm' -o -name '*.rom' -o -name '*.lst' \)
find build -maxdepth 2 -type f
```

最初のコマンドは原則として何も出力しない状態が望ましいです。

## 6. 新しいサンプルを追加する場合

1. `test/<Name>/`を作成
2. `.els`入力を配置
3. `test/test_code.py`にコンパイルテストを追加
4. テストを実行
5. `build/<Name>/`の成果物を確認
6. 成果物はコミットせず、入力ソースと必要な説明だけをコミット

ゲームや長いデモなど、自動テストよりもサンプルとしての意味が強いものは、
`examples/`に配置します。

## 7. ライブラリ変更

ライブラリのアセンブリを変更した場合は、次を確認します。

1. `; func`宣言と実装ラベルが一致している
2. 引数の順序とワード幅が一致している
3. 呼び出し後にスタックが期待状態へ戻る
4. 必要なら`Debug`を有効にしてメモリ状態を確認する
5. 対応する`.els`サンプルを追加する

## 8. 既知の注意点

- テストコードのライブラリパスがカレントディレクトリに依存する
- `build/`の成果物は自動生成なので、ソースの正本ではない
- `.asm`生成後のopenMSX起動と実行確認は別途必要
- `<<`／`>>`は16ビット論理シフトとして実装されている
