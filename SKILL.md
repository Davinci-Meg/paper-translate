---
name: paper-translate
description: 英語論文（PDF）を日本語に翻訳・要約するスキル。1ファイルでも複数ファイルでも対応。PDFのMarkdown変換・日本語翻訳・構造化サマリー生成・PDF出力を一括で行い、論文タイトル名のフォルダにまとめて保存する。「論文を翻訳して」「英語の論文を日本語にして」「PDFを要約して」「DownloadsにあるXXXの論文を翻訳して」「○○フォルダ内のPDFを全部翻訳して」など、論文・PDF翻訳・要約に関する依頼があれば必ずこのスキルを使うこと。他のスキルへの依存なし。
---

# paper-translate

英語論文のPDFを受け取り、**論文タイトル名のフォルダ**を作成して以下のファイルを格納するスキル。1ファイルでも複数ファイルでも動作する。

```
<出力先>/<論文タイトル>/
├── images/                 — 論文内の図を抽出した画像ファイル
│   ├── page01_01.png
│   └── ...
├── paper.md                — 原文のMarkdown変換（英語・図版付き）
├── paper.ja.md             — 日本語翻訳（図版付き）
├── paper.summary.ja.md     — 日本語の構造化サマリー
├── paper.ja.pdf            — 日本語翻訳のPDF版（図版埋め込み）
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

### Step 1.5: 画像抽出と Markdown への挿入

`extract_images.py` が SKILL.md と同じディレクトリに存在する場合に実行する。

1. `extract_images.py` のパスを特定する（SKILL.md と同じディレクトリ）。
2. 以下のコマンドを実行する：

```bash
python "<SKILL.mdのディレクトリ>/extract_images.py" "<PDFパス>" "<出力フォルダ>"
```

3. スクリプトは以下を自動で行う：
   - PDF から図版を `<出力フォルダ>/images/` に抽出（小さすぎる装飾画像は除外）
   - 各 Figure のキャプションを検出して画像と対応付け
   - `paper.md` と `paper.ja.md` の Figure 参照箇所に `![Figure N: caption](images/...)` を挿入

4. `pymupdf` が未インストールの場合はスキップし、画像なしで続行する（ユーザーに通知）。

### Step 2: PDFをMarkdownに変換（`<出力フォルダ>/paper.md`）

1. `<出力フォルダ>/paper.md` を新規作成する。
2. PDFを読んでセクション構造をMarkdown形式でファイルに出力する。セクション番号はPDFの番号に従うこと。
3. セクションごとに「このセクションの内容をMarkdown形式に変換し、Markdownファイルの該当のセクションの部分に挿入する。段落ごとに空白行で区切ること。」というサブタスクを生成する。
4. 生成したサブタスクを順番に実行する。
5. 全てのセクションを1つずつ確認し、空白のセクションがないかを確認する。空白のセクションがあれば修正する。
6. `pnpx markdownlint-cli2 <出力フォルダ>/paper.md` を実行してフォーマットをチェックし、エラーがあれば修正する。

### Step 3: MarkdownをJapanese翻訳（`<出力フォルダ>/paper.ja.md`）

1. `<出力フォルダ>/paper.md` を読み込む。
2. ファイル全体をセクションごとに分割する。
3. 各セクションのタイトル（見出し行）は翻訳せず英語のまま保持する。
4. 各セクションの本文だけを英語から日本語に翻訳する。
   - Markdownの構造（見出し階層、箇条書き、コードブロック、表）はそのまま維持する。
   - 表や図表キャプションも本文に含まれる場合は日本語に翻訳する。
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

#### 5-3: PDF変換実行

```bash
# 翻訳PDFの生成（--resource-path で images/ を参照可能にする）
pandoc "<出力フォルダ>/paper.ja.md" \
  -o "<出力フォルダ>/paper.ja.pdf" \
  --pdf-engine=xelatex \
  -V mainfont="<利用可能なフォント>" \
  -V CJKmainfont="<利用可能なフォント>" \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V lang=ja \
  --resource-path="<出力フォルダ>"

# サマリーPDFの生成
pandoc "<出力フォルダ>/paper.summary.ja.md" \
  -o "<出力フォルダ>/paper.summary.ja.pdf" \
  --pdf-engine=xelatex \
  -V mainfont="<利用可能なフォント>" \
  -V CJKmainfont="<利用可能なフォント>" \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V lang=ja
```

xelatex が使えない場合は `--pdf-engine=lualatex` にフォールバックする。

---

### Step 6: 完了報告

全件処理後に以下を出力する：

**単一ファイルの場合:**
```
✅ 完了

📁 <出力フォルダ>/
├── images/                 （抽出図版）
├── paper.md                （原文MD・図版付き）
├── paper.ja.md             （翻訳MD・図版付き）
├── paper.summary.ja.md     （サマリーMD）
├── paper.ja.pdf            （翻訳PDF・図版埋め込み）
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
| pymupdf が未インストール | `pip install pymupdf` を案内し、画像なしで続行する |
| pandoc が未インストール | MDファイルは保存済みであることを伝え、インストール案内をする |
| xelatex/lualatex が未インストール | `--pdf-engine=weasyprint` にフォールバックし、それも失敗したらMDのみで完了とする |
| 日本語フォントが見つからない | `Noto Sans CJK JP` のインストールを案内し、暫定的に `DejaVu Sans` で試みる |
| 数式・図が多い論文 | 変換できない要素は `[図N]` `[数式N]` のプレースホルダーに置換 |
| 非常に長い論文（50ページ超） | セクションごとに分割処理し、最後に結合する |
