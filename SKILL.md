---
name: paper-translate
description: 英語論文（PDF）を日本語に翻訳・要約するスキル。1ファイルでも複数ファイルでも対応。PDFのMarkdown変換・日本語翻訳・構造化サマリー生成・PDF出力を一括で行い、論文タイトル名のフォルダにまとめて保存する。「論文を翻訳して」「英語の論文を日本語にして」「PDFを要約して」「DownloadsにあるXXXの論文を翻訳して」「○○フォルダ内のPDFを全部翻訳して」など、論文・PDF翻訳・要約に関する依頼があれば必ずこのスキルを使うこと。他のスキルへの依存なし。
---

# paper-translate

英語論文のPDFを受け取り、**論文タイトル名のフォルダ**を作成して以下のファイルを格納するスキル。1ファイルでも複数ファイルでも動作する。

```
<出力先>/<論文タイトル>/
├── images/                 — PDFから抽出した図表画像
├── paper.md                — 原文のMarkdown変換（英語・画像埋め込み）
├── paper.ja.md             — 日本語翻訳（本文のみ翻訳、見出しは英語保持・画像埋め込み）
├── paper.summary.ja.md     — 日本語の構造化サマリー
├── paper.ja.pdf            — 日本語翻訳のPDF版（画像・CJK改行対応）
└── paper.summary.ja.pdf    — 日本語サマリーのPDF版
```

---

## 起動方法

1ファイル・複数ファイル・フォルダ指定、いずれもパスでも自然言語でも指定できる：

```
/paper-translate ~/Downloads/attention_is_all_you_need.pdf
/paper-translate DownloadsフォルダのAttention is All You Needの論文
/paper-translate ~/papers/ 内のPDFを全部
/paper-translate デスクトップのpapers フォルダにあるPDFら
```

---

## 実行ステップ

### Step 0: 対象PDFファイルの特定

入力を解釈して、処理対象のPDFファイルリストを作成する。

**単一ファイルの場合:**
- ファイル名・場所・論文タイトルのキーワードから候補を探す
- `find` コマンドや `ls` で該当ディレクトリを検索する
- 候補が複数ある場合はユーザーに確認する

**フォルダ・複数ファイルの場合:**
- `find <ディレクトリ> -name "*.pdf"` でPDFを列挙する
- 処理対象のファイル一覧をユーザーに提示し、確認を取ってから処理を開始する
- 例: 「以下の3件を処理します。よろしいですか？」

処理対象が確定したら、各PDFに対して **Step 1〜5 を順番に繰り返す**。

---

以下の Step 1〜5 は、対象PDFが1件の場合はそのまま実行。複数件の場合は各PDFごとに繰り返す。

---

### Step 1: 出力フォルダの作成

1. PDFを開いて論文タイトルを取得する。
2. タイトルをフォルダ名として使用する。フォルダ名のルール：
   - ファイルシステムで使えない文字（`/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`）はアンダースコアに置換
   - 長すぎる場合は先頭100文字に切り詰める
3. PDFと同じディレクトリに `<論文タイトル>/` フォルダを作成する。
4. 以降の全ファイルはこのフォルダ内に保存する。出力パスを `<出力フォルダ>` とする。

### Step 1.5: PDFから画像を抽出（`<出力フォルダ>/images/`）

PDFに含まれる図表画像を抽出し、Markdownから参照できるようにする。

#### 抽出方法

`pymupdf`（Python `fitz`モジュール）を使用して画像を抽出する：

```python
import fitz
import os
import json

doc = fitz.open("<PDFパス>")
output_dir = "<出力フォルダ>/images"
os.makedirs(output_dir, exist_ok=True)

img_counter = 1
img_meta = {}  # filename -> { width_pct, page }

for page_num in range(len(doc)):
    page = doc[page_num]
    page_width = page.rect.width
    images = page.get_images(full=True)
    for img in images:
        xref = img[0]
        base_image = doc.extract_image(xref)
        ext = base_image["ext"]
        img_data = base_image["image"]
        filename = f"figure_{img_counter}.{ext}"
        with open(os.path.join(output_dir, filename), "wb") as f:
            f.write(img_data)

        # 画像の表示幅を計算（ページ幅に対する割合）
        img_rects = page.get_image_rects(xref)
        if img_rects:
            display_width = img_rects[0].width
            width_pct = round(display_width / page_width * 100)
            width_pct = max(20, min(width_pct, 100))  # 20%〜100% にクランプ
        else:
            width_pct = 80  # 取得できない場合のデフォルト

        img_meta[filename] = {"width_pct": width_pct, "page": page_num + 1}
        print(f"Page {page_num+1}: {filename} ({base_image['width']}x{base_image['height']}, display: {width_pct}%)")
        img_counter += 1

doc.close()

# メタデータを保存（後のステップで参照）
with open(os.path.join(output_dir, "meta.json"), "w") as f:
    json.dump(img_meta, f, indent=2)
```

#### 画像とFigureの対応付け

1. 抽出した画像をページ順に `figure_1.ext`, `figure_2.ext`, ... と命名する。
2. PDFのテキストを読み、各 `Figure N:` キャプションがどのページにあるかを特定する。
3. ページ番号を基に、抽出画像と Figure 番号を対応付ける。
4. 対応表を記録しておく（例: `figure_1.jpeg` → Figure 1, `figure_2.jpeg` → Figure 2）。
5. `meta.json` に各画像の表示幅（`width_pct`）が記録されているので、後のステップで参照する。

#### pymupdf がインストールされていない場合

`pdfimages` コマンドにフォールバックする：

```bash
pdfimages -all "<PDFパス>" "<出力フォルダ>/images/figure"
```

どちらも使えない場合は画像なしで続行し、プレースホルダー `[図N]` を使用する。

### Step 2: PDFをMarkdownに変換（`<出力フォルダ>/paper.md`）

1. `<出力フォルダ>/paper.md` を新規作成する。
2. PDFを読んでセクション構造をMarkdown形式でファイルに出力する。セクション番号はPDFの番号に従うこと。
3. セクションごとに「このセクションの内容をMarkdown形式に変換し、Markdownファイルの該当のセクションの部分に挿入する。段落ごとに空白行で区切ること。」というサブタスクを生成する。
4. 生成したサブタスクを順番に実行する。
5. **画像の埋め込み**: PDFで `Figure N:` として参照されている箇所に、Step 1.5 で抽出した対応画像をMarkdown画像記法で埋め込む。`images/meta.json` から `width_pct` を読み取り、`{width=X%}` 属性を付与する：
   ```markdown
   ![Figure 1: キャプション文](images/figure_1.jpeg){width=70%}
   ```
   - 画像は必ずキャプション付きで挿入する。キャプションはPDFの原文に従う。
   - `{width=X%}` は `meta.json` の値をそのまま使う。`meta.json` がない場合は `{width=80%}` をデフォルトとする。
   - 画像が抽出できなかった場合のみ `[Figure N: キャプション]` のプレースホルダーを使用する。
6. 全てのセクションを1つずつ確認し、空白のセクションがないかを確認する。空白のセクションがあれば修正する。
7. `pnpx markdownlint-cli2 <出力フォルダ>/paper.md` を実行してフォーマットをチェックし、エラーがあれば修正する。

### Step 3: MarkdownをJapanese翻訳（`<出力フォルダ>/paper.ja.md`）

1. `<出力フォルダ>/paper.md` を読み込む。
2. ファイル全体をセクションごとに分割する。
3. 各セクションのタイトル（見出し行）は翻訳せず英語のまま保持する。
4. 各セクションの本文だけを英語から日本語に翻訳する。
   - Markdownの構造（見出し階層、箇条書き、コードブロック、表）はそのまま維持する。
   - 表や図表キャプションも本文に含まれる場合は日本語に翻訳する。
   - **画像参照はそのまま保持する**: `![Figure N: ...](images/figure_N.ext){width=X%}` の行はそのまま維持する（`{width=X%}` 属性も保持すること）。キャプション部分のみ日本語に翻訳してもよい（例: `![図1: 日本語キャプション](images/figure_1.jpeg){width=70%}`）。
5. `<出力フォルダ>/paper.ja.md` として保存する。
6. 全てのセクションを確認し、空欄や未翻訳の部分がないかチェックし修正する。
7. `pnpx markdownlint-cli2 <出力フォルダ>/paper.ja.md` を実行してフォーマットをチェックし、エラーがあれば修正する。

### Step 4: サマリー生成（`<出力フォルダ>/paper.summary.ja.md`）

`<出力フォルダ>/paper.ja.md` を読み込み、以下の構造で `<出力フォルダ>/paper.summary.ja.md` を作成する。

```markdown
# <論文タイトル（英語）> — 要約

## 基本情報
- **著者**: ...
- **発表年**: ...
- **掲載**: ...（学会・ジャーナル名）
- **原文**: <PDFパス>

## 一言まとめ
（1〜2文で論文の核心を説明）

## 背景・課題
（この研究が解こうとした問題）

## 提案手法
（何を・どうやって解決したか）

## 主な結果
（定量的な結果、ベースラインとの比較など）

## 貢献・意義
（この論文のインパクト・新規性）

## 限界・今後の課題
（著者が認めている制限や残課題）

## キーワード
`keyword1`, `keyword2`, ...
```

**注意**: `原文` のパスにバックスラッシュが含まれる場合（Windows）、バッククォートで囲むこと（例: `` `G:\path\to\file.pdf` ``）。LaTeX変換時にバックスラッシュがコマンドと誤解されるのを防ぐ。

### Step 5: PDF出力（`paper.ja.pdf` / `paper.summary.ja.pdf`）

`pandoc` を使って翻訳とサマリーをPDFに変換する。

#### 5-1: pandoc のインストール確認

```bash
pandoc --version
```

インストールされていない場合はユーザーに通知する：
> 「PDF出力にはpandocが必要です。https://pandoc.org/installing.html からインストールしてください。」
> 「インストール済みであれば再度お知らせください。MDファイルはすでに生成済みです。」

#### 5-2: 日本語フォント確認

```bash
# Windows
fc-list | grep -i "noto\|meiryo\|yu gothic\|ms gothic"

# macOS
fc-list | grep -i "noto\|hiragino"
```

利用可能なフォントを確認し、以下の優先順で使用する：

| OS | 優先フォント |
|----|------------|
| Windows | Yu Gothic, Meiryo, MS Gothic |
| macOS | Hiragino Sans, Hiragino Mincho |
| Linux | Noto Sans CJK JP, IPAexGothic |

#### 5-3: LaTeXヘッダーファイルの作成

CJK（日本語・中国語・韓国語）テキストの自動改行を正しく処理するため、`<出力フォルダ>/header.tex` を作成する：

```latex
\usepackage{luatexja}
\usepackage[match]{luatexja-fontspec}
\setmainjfont{<利用可能な日本語フォント>}
```

このヘッダーにより `luatexja` パッケージがロードされ、日本語テキストが自動的に正しい位置で改行される。

#### 5-4: PDF変換実行

**重要**: `--pdf-engine=lualatex` を使用すること。`xelatex` はCJK改行で問題が起きやすい。

```bash
# 翻訳PDFの生成
pandoc "<出力フォルダ>/paper.ja.md" \
  -o "<出力フォルダ>/paper.ja.pdf" \
  --pdf-engine=lualatex \
  -V mainfont="<利用可能なフォント>" \
  -V sansfont="<利用可能なフォント>" \
  -V monofont="<利用可能なフォント>" \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -H "<出力フォルダ>/header.tex"

# サマリーPDFの生成
pandoc "<出力フォルダ>/paper.summary.ja.md" \
  -o "<出力フォルダ>/paper.summary.ja.pdf" \
  --pdf-engine=lualatex \
  -V mainfont="<利用可能なフォント>" \
  -V sansfont="<利用可能なフォント>" \
  -V monofont="<利用可能なフォント>" \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -H "<出力フォルダ>/header.tex"
```

#### 5-5: LaTeXエスケープ問題への対処

Markdownの内容にLaTeXの特殊文字が含まれるとビルドが失敗することがある。よくある問題と対策：

| 問題 | 原因 | 対策 |
|------|------|------|
| `Undefined control sequence` at `\n` | テキスト中の `\n` がLaTeXコマンドとして解釈される | バッククォートで囲む: `` `\n` `` |
| `Undefined control sequence` at `\マ` 等 | Windowsパスのバックスラッシュ `\` | パスをバッククォートで囲む: `` `G:\path` `` |
| テーブルの列が見切れる | 列幅が固定されない | 簡素なテーブルに書き換えるか、長い行を折り返す |

ビルドエラーが出た場合は、エラーメッセージの行番号からMarkdown内の該当箇所を特定し、上記の対策を適用してリビルドする。

#### 5-6: 後片付け

PDF生成完了後、`<出力フォルダ>/header.tex` を削除する。

---

### Step 6: 完了報告

全件処理後に以下を出力する：

**単一ファイルの場合:**
```
✅ 完了

📁 <出力フォルダ>/
├── images/                 （抽出画像）
├── paper.md                （原文MD）
├── paper.ja.md             （翻訳MD）
├── paper.summary.ja.md     （サマリーMD）
├── paper.ja.pdf            （翻訳PDF）
└── paper.summary.ja.pdf    （サマリーPDF）
```

**複数ファイルの場合:**
```
✅ 3件完了

📁 Attention Is All You Need/
📁 BERT_Pre-training of Deep Bidirectional Transformers/
📁 GPT-3_Language Models are Few-Shot Learners/
```

---

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| 自然言語からPDFを特定できない | 候補ファイルを列挙してユーザーに選択を求める |
| PDFが見つからない | パスを確認してユーザーに再入力を求める |
| 複数件処理中に1件失敗 | エラーを記録して残りの処理を続行し、最後にまとめて報告する |
| pandoc が未インストール | MDファイルは保存済みであることを伝え、インストール案内をする |
| lualatex が未インストール | `--pdf-engine=xelatex` にフォールバック（ただしCJK改行は手動で確認）。それも失敗したらMDのみで完了とする |
| 日本語フォントが見つからない | `Noto Sans CJK JP` のインストールを案内し、暫定的に `DejaVu Sans` で試みる |
| pymupdf / pdfimages が未インストール | 画像抽出をスキップし、プレースホルダー `[Figure N]` で続行する |
| 抽出画像が巨大（>5MB） | 品質を維持しつつリサイズ検討。ただしそのまま使用しても問題ない |
| LaTeXビルドエラー | エラーメッセージからMarkdown内の特殊文字を特定し、バッククォートで囲むなどして修正 |
| 非常に長い論文（50ページ超） | セクションごとに分割処理し、最後に結合する |
