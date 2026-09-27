# ELiSE アーキテクチャ

## 1. 全体像

ELiSEは、ソース言語、VM中間表現、Z80アセンブリの3層で構成されています。

```text
┌──────────────┐
│ .els source  │  クラス、関数、MSX API呼び出し
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Front end     │  Tokenizer / SymbolTableCreator / Parser
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Extended VM   │  push/pop/call + lib_call/data/x2
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Back end      │  ASMTranslator / AsmWriter
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Linker        │  AsmComposer + Boot/System + Lib/*.asm
└──────┬───────┘
       │
       ▼
  build/<program>/<program>.asm
```

コンパイラ本体は外部アセンブラを呼び出しません。最終成果物はZ80アセンブリです。

## 2. コンパイルの段階

### 2.1 入力ファイルの収集

`Compiler.compile()` はディレクトリまたは単一ファイルを受け取ります。

- ディレクトリの場合、その直下の `.els` をすべて対象にする
- 単一ファイルの場合、そのファイルだけを対象にする
- 出力先は `build/<program>/`

ディレクトリ入力の例:

```text
入力:  test/Array/
出力:  build/Array/
```

### 2.2 ライブラリのシンボル表作成

`SymbolTableCreator` は、入力ソースだけでなく `Lib/*.asm` のコメントに書かれた関数宣言も読み取ります。

ライブラリの宣言は次の形式です。

```asm
; func    function void printInt(int value)
```

この宣言から、クラス名、関数種別、戻り値、関数名、引数の型と名前を登録します。

そのため、ライブラリ関数を追加・変更する場合は、アセンブリ本体だけでなく `; func` 宣言も更新する必要があります。

### 2.3 字句解析

`Tokenizer` はソースを `Token` の列へ変換します。

対応する主な入力は次の通りです。

- キーワード
- 識別子
- 整数（10進、16進、8進、2進）
- 文字列
- 記号
- 行コメントとブロックコメント

`<=`、`>=`、`==`、`!=`、`++`、`--`などは、内部用のトークン名へ変換されます。

### 2.4 構文解析とVM生成

`Parser` はシンボル表を参照しながら、構文木を保持せずにVM命令列を生成します。

`Analyzer.load_vm_writer()` は `VMWriter.py` の `vm_` で始まる関数を動的に収集します。例えば `vm_push()` は `push` 命令を生成します。

通常のVM命令に加えて、ELiSE固有の命令があります。

| 命令 | 目的 |
|---|---|
| `lib_call` | ライブラリ呼び出し前の戻り先準備 |
| `lib_ret_address` | ライブラリ呼び出しから戻る位置 |
| `data` | `dat`で定義した静的データのアドレス生成 |
| `x2` | 16ビット配列要素のアドレス計算 |

### 2.5 VMからZ80への変換

`ASMTranslator` は `.vm`を読み、`AsmWriter`の命令生成メソッドを呼び出します。

`AsmWriter` は次の状態を持ちます。

- VMセグメントのアドレス
- 静的変数一覧
- 文字列データ一覧
- `dat`データ一覧
- 比較演算用ラベル番号
- 関数呼び出し用の戻り先ラベル

VMの`call`は、戻りアドレス、`LOCAL`、`ARGUMENT`、`THIS`、`THAT`をスタックへ退避し、呼び出し先へジャンプするZ80コードになります。

### 2.6 リンク

`AsmComposer` は次の順番で最終アセンブリを作成します。

1. ブートコード
2. 生成されたユーザーコード
3. `Lib/*.asm`
4. 静的変数、文字列、`dat`データ、ワークエリア、ヒープ
5. 終了コード

`db`環境が無効な場合、`Debug.asm`はリンクされません。

## 3. 起動環境

`elise.py`には2つの環境定義があります。

| 環境 | ORG | 初期SP | ヒープサイズ | 用途 |
|---|---:|---:|---:|---|
| `ELISE_ENV` | `0x8100` | `0xDC60` | `0x1000` | MSXPen |
| `ELISE_ENV_CARTRIDGE` | `0x4000` | `0xDC60` | `0x2000` | カートリッジ |

カートリッジ環境ではROMヘッダを生成し、プログラム領域の後ろにワークエリアを配置します。

## 4. ランタイムのメモリモデル

MSX向けの実行系では、VMのセグメントをZ80メモリ上のワーク領域へ対応させます。

主な領域は次の通りです。

- `sys_SP`
- `sys_LOCAL`
- `sys_ARGUMENT`
- `sys_POINTER`
- `sys_THIS`
- `sys_THAT`
- `sys_TEMP`
- 静的変数
- 文字列データ
- `dat`データ
- ヒープ

配列要素は16ビットワードで格納されるため、添字をアドレスへ加算する前に`x2`で2倍します。

## 5. 変更時の責務

| 変更したい内容 | 主な変更箇所 |
|---|---|
| 新しい演算子 | `Token.py`、`Tokenizer.py`、`Parser.py`、`AsmWriter.py` |
| 新しい文 | `Token.py`、`Parser.py`、`VMWriter.py` |
| 新しい型・変数規則 | `Token.py`、`SymbolTable.py`、`SymbolTableCreator.py` |
| 新しいVM命令 | `VMWriter.py`、`ASMTranslator.py`、`AsmWriter.py` |
| 新しいMSX API | `Lib/<name>.asm`の実装と`; func`宣言 |
| 新しい起動方式 | `elise.py`、`BootLibrary.py`、`SystemLibrary.py` |
| 出力場所 | `Compiler.py`、`elise.py` |

## 6. 現在の制約

- シンボル表は型情報を持つが、完全な型検査器ではない
- クラスの`parent`フィールドは存在するが、継承機能は言語仕様として確立していない
- 外部アセンブラ、ROM作成、エミュレータ実行はELiSEのコンパイル処理外
- テストのライブラリパスは現在のところカレントディレクトリに依存する
