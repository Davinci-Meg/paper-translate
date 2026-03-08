# paper-translate

**Claude Code skill** — 英語論文（PDF）を日本語に翻訳・要約し、図版付きで出力する。

```
/paper-translate path/to/paper.pdf
```

1ファイルでも複数ファイルでも、パス指定でも自然言語でも動作する。

---

## 出力

```
<PDFと同じディレクトリ>/<論文タイトル>/
├── images/                 — 論文内の図を抽出した画像ファイル
│   ├── page01_01.png
│   └── ...
├── paper.md                — 原文の Markdown 変換（英語・図版付き）
├── paper.ja.md             — 日本語翻訳（図版付き）
├── paper.summary.ja.md     — 日本語の構造化サマリー
├── paper.ja.pdf            — 日本語翻訳の PDF 版
└── paper.summary.ja.pdf    — 日本語サマリーの PDF 版
```

---

## インストール

### 1. このリポジトリをクローン

```bash
git clone https://github.com/<your-name>/paper-translate.git
```

### 2. Claude Code のスキルとして登録

`SKILL.md` を Claude Code のカスタムスキルディレクトリに配置する：

```bash
# macOS / Linux
mkdir -p ~/.claude/commands/paper-translate
cp SKILL.md ~/.claude/commands/paper-translate/SKILL.md
cp extract_images.py ~/.claude/commands/paper-translate/extract_images.py

# Windows (PowerShell)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\commands\paper-translate"
Copy-Item SKILL.md "$env:USERPROFILE\.claude\commands\paper-translate\SKILL.md"
Copy-Item extract_images.py "$env:USERPROFILE\.claude\commands\paper-translate\extract_images.py"
```

### 3. 依存関係のインストール

**Python ライブラリ（画像抽出に必要）**

```bash
pip install pymupdf
```

**PDF 変換エンジン（PDF 出力に必要）**

- [pandoc](https://pandoc.org/installing.html) をインストール
- xelatex を含む TeX ディストリビューションをインストール
  - Windows: [MiKTeX](https://miktex.org/)
  - macOS: `brew install --cask mactex`
  - Linux: `sudo apt install texlive-xetex texlive-lang-japanese`

---

## 使い方

Claude Code を起動して `/paper-translate` を実行：

```
/paper-translate ~/Downloads/attention_is_all_you_need.pdf
/paper-translate DownloadsフォルダのAttention is All You Needの論文
/paper-translate ~/papers/ 内のPDFを全部
```

---

## 動作環境

| 項目 | 要件 |
|------|------|
| Claude Code | 最新版 |
| Python | 3.10 以上 |
| pymupdf | 1.23 以上 |
| pandoc | 2.x 以上 |
| TeX エンジン | xelatex または lualatex |
| 日本語フォント | Yu Gothic (Win) / Hiragino (mac) / Noto CJK (Linux) |

---

## ファイル構成

```
paper-translate/
├── SKILL.md            — Claude Code スキル定義（メインロジック）
├── extract_images.py   — PDF からの画像抽出スクリプト
└── README.md           — このファイル
```

### SKILL.md

Claude Code のカスタムスキルとして動作するプロンプト定義。`/paper-translate` コマンドで呼び出されると、Step 0〜6 を順番に実行する。

### extract_images.py

pymupdf を使って PDF から図版を抽出し、Markdown の `Figure N` 参照箇所に `![Figure N: caption](images/...)` を自動挿入するスクリプト。SKILL.md から呼び出される。

```bash
python extract_images.py <pdf_path> <output_dir>
```

---

## サンプル出力

[Nukabot: Design of Care for Human-Microbe Relationships (CHI '21)](https://doi.org/10.1145/3411763.3451605) を処理した例：

**paper.ja.md（抜粋）**

```markdown
## 1 INTRODUCTION AND BACKGROUND

ヒューマン・コンピュータ・インタラクション（HCI）研究者たちは...

![Figure 1: Nukadoko fermentation involving human, veg-](images/page01_02.png)
```

**paper.summary.ja.md**

```markdown
# Nukabot: Design of Care for Human-Microbe Relationships — 要約

## 一言まとめ
日本の伝統的な発酵食品「糠床」を音声対話付きのスマート桶「Nukabot」に進化させ、
人間と微生物の間に情動的・倫理的関係を育むHCIデザインを提案・評価した研究。
...
```

---

## ライセンス

MIT
