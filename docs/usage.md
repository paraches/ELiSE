# ELiSE 現場利用マニュアル

この文書は、ELiSEで`.els`をコンパイルし、ROMを作成してopenMSXで実行・確認するための実作業手順です。

作業はすべてELiSE-originalをcloneしたプロジェクトルートで行います。

```bash
cd /path/to/ELiSE-original
```

## 1. 事前確認

仮想環境を有効にします。

```bash
source .venv/bin/activate
```

ツールの確認:

```bash
python --version
zasm --version
openmsx --version
```

現在確認済みの目安:

```text
Python 3.12.x
zasm 4.4.7
openMSX 21.0
```

## 2. 最小サンプルを作る

`examples/Hello/Main.els`として、このサンプルを同梱しています。

```els
class Main {
    function void main() {
        Output.printIntLn(7);
        return;
    }
}
```

このプログラムは、MSX上で整数`7`を表示して終了します。

## 3. コンパイルする

```bash
python elise.py examples/Hello -VB 0
```

成功すると、次のファイルが`build/Hello/`に生成されます。

```text
Main.vm
Hello.asm
Hello.symbols.json
```

`test/`や`examples/`に生成物が戻っていないことを確認します。

```bash
find test examples -type f \
    \( -name '*.vm' -o -name '*.asm' -o -name '*.rom' -o -name '*.lst' \)
```

何も表示されなければ正常です。

## 4. カートリッジROMを作る

zasmでアセンブルします。

```bash
python elise.py examples/Hello \
    --media cartridge \
    --assemble \
    -VB 0
```

生成物を確認します。

```bash
ls -lh build/Hello
```

主な成果物:

```text
Hello.asm
Hello.rom
Hello.lst
Hello.symbols.json
```

## 5. openMSXで実行する

C-BIOSのMSX2+はカートリッジから起動するため、`--media cartridge`を指定します。
この指定により、カートリッジヘッダと`ORG 0x4000`が自動的に設定されます。

```bash
python elise.py examples/Hello \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    -VB 0
```

`--run`を指定すると、コンパイル、アセンブル、openMSX起動を続けて実行します。

画面に`7`が表示されることを確認してください。openMSXを終了する場合は、通常のウィンドウ終了操作を使います。

起動ログ:

```text
build/Hello/logs/emulator.log
```

## 6. 関数ブレークポイントを設定する

`Main.main`の開始位置にブレークポイントを設定します。

```bash
python elise.py examples/Hello \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    --breakpoint Main.main \
    -VB 0
```

次のファイルが生成されます。

```text
build/Hello/Hello.tcl
```

内容は次のようなopenMSXコマンドです。

```tcl
debug breakpoint create 0x....
```

関数を複数指定する場合は`--breakpoint`を繰り返します。指定できるのは、今回コンパイルする`.els`側で定義された関数です。

## 7. symbols.jsonを確認する

```bash
python -m json.tool build/Hello/Hello.symbols.json | less
```

`symbols.json`には、次の対応が入っています。

- `.els`のソースファイルと宣言行
- VMファイルと`function`行
- ASM行
- zasmで確定した実アドレス
- `heap`、`sys_SP`などのランタイムラベル

## 8. openMSXをPythonから制御する

ROMをヘッドレスのopenMSXで起動し、デバッグ情報を取得できます。

```bash
python - <<'PY'
from elise.OpenMSXControl import OpenMSXControlSession

session = OpenMSXControlSession.launch(
    "build/Hello/Hello.rom",
    machine="C-BIOS_MSX2+",
)

print("debug status:", session.debug_breaked().text.strip())
print("registers:", session.debug_registers())

session.debug_break()
snapshot = session.runtime_snapshot(
    "build/Hello/Hello.symbols.json",
    stack_bytes=16,
    heap_bytes=16,
)
print("stack:", snapshot["stack"])
print("heap:", snapshot.get("heap"))

session.close()
PY
```

この操作では、次を確認できます。

- CPUレジスタ
- 現在のスタック位置とスタック内容
- ヒープ開始位置、空きリスト、ブロックサイズ
- openMSXの停止・ステップ制御

## 9. Sevenサンプルを実行する

既存のサンプルを試す場合:

```bash
python elise.py test/Seven \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    -VB 0
```

ブレークポイント付き:

```bash
python elise.py test/Seven \
    --run \
    --machine 'C-BIOS_MSX2+' \
    --media cartridge \
    --breakpoint Main.main \
    -VB 0
```

## 10. よくある問題

### `zasm: command not found`

zasmの場所を確認します。

```bash
command -v zasm
```

必要なら`--assembler`で明示します。

```bash
python elise.py examples/Hello \
    --assemble \
    --assembler /usr/local/bin/zasm
```

### `openMSX executable not found`

```bash
command -v openmsx
```

PATHにない場合は、openMSXのインストール先を指定します。

```bash
python elise.py examples/Hello \
    --run \
    --openmsx /path/to/openmsx \
    --machine 'C-BIOS_MSX2+'
```

### `Function not found in symbols`

`--breakpoint`には、クラス名を含む関数名を指定します。

```text
正: Main.main
誤: main
```

### 生成物がソースディレクトリにある

生成物は`build/<program>/`に置かれます。`test/`や`examples/`へ手動でコピーしないでください。

### テストを実行したい

テストは`test/`をカレントディレクトリにして実行します。

```bash
cd test
PYTHONPATH=../src ../.venv/bin/python -m unittest discover -s . -p 'test_*.py'
```

## 11. 現在の範囲

このマニュアルで説明している範囲は、現在のELiSE-originalで利用できる機能です。

```text
.els
  -> VM
  -> ASM
  -> ROM
  -> openMSX
  -> breakpoint / step / memory / registers / stack / heap
```

VSCodeのデバッグ画面への統合、WebMSX、MSX実機への自動転送は、
この公開版のCLIには含まれていません。
