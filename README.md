# :page_facing_up: paper-translator-en2ja

A Claude Code skill that translates English academic papers (PDF) into Japanese — with figures, structured summaries, and PDF output.

![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-blueviolet?logo=anthropic)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-AGPL--v3-green)

> :jp: このスキルは英語論文を日本語に翻訳します

## :sparkles: Features

- **PDF to Markdown** — 論文PDFをセクション構造を保ったままMarkdownに変換
- **Japanese translation** — 本文を日本語に翻訳（セクション見出しは英語のまま保持）
- **Figure extraction** — pymupdf で図表を自動抽出し、Markdownに埋め込み
- **Structured summary** — 一言まとめ・セクション要約・キーワードを含む構造化サマリーを生成
- **PDF export** — 日本語翻訳・サマリーをそれぞれPDFとして出力（CJK改行対応）
- **Batch processing** — 複数PDFの一括処理に対応
- **Flexible input** — ファイルパス指定でも自然言語でも動作

## :package: Output

```
<PDFと同じディレクトリ>/<論文タイトル>/
├── images/                 — PDFから抽出した図表画像
├── paper.md                — 原文の Markdown 変換（英語・画像埋め込み）
├── paper.ja.md             — 日本語翻訳（見出しは英語保持・画像埋め込み）
├── paper.summary.ja.md     — 日本語の構造化サマリー
├── paper.ja.pdf            — 日本語翻訳の PDF 版
└── paper.summary.ja.pdf    — 日本語サマリーの PDF 版
```

## :wrench: Installation

### 1. Clone this repository

```bash
git clone https://github.com/Davinci-Meg/paper-translator-en2ja.git
```

### 2. Register as a Claude Code skill

Copy `SKILL.md` to the Claude Code custom skill directory:

```bash
# macOS / Linux
mkdir -p ~/.claude/commands/paper-translate
cp SKILL.md ~/.claude/commands/paper-translate/SKILL.md

# Windows (PowerShell)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\commands\paper-translate"
Copy-Item SKILL.md "$env:USERPROFILE\.claude\commands\paper-translate\SKILL.md"
```

### 3. Install dependencies

**Python library (for figure extraction)**

```bash
pip install pymupdf
```

**PDF conversion engine (for PDF output)**

- Install [pandoc](https://pandoc.org/installing.html)
- Install a TeX distribution with lualatex:

| OS | Command |
|---|---|
| Windows | Install [MiKTeX](https://miktex.org/) |
| macOS | `brew install --cask mactex` |
| Linux | `sudo apt install texlive-luatex texlive-lang-japanese` |

## :rocket: Usage

Launch Claude Code and run `/paper-translate`:

```
/paper-translate ~/Downloads/attention_is_all_you_need.pdf
/paper-translate DownloadsフォルダのAttention is All You Needの論文
/paper-translate ~/papers/ 内のPDFを全部
```

## :gear: Requirements

| Item | Requirement |
|---|---|
| Claude Code | Latest version |
| Python | 3.10+ |
| pymupdf | 1.23+ |
| pandoc | 2.x+ |
| TeX engine | lualatex (recommended) or xelatex |
| Japanese font | Yu Gothic (Win) / Hiragino (Mac) / Noto CJK (Linux) |

## :bulb: Example Output

Processed from [Nukabot: Design of Care for Human-Microbe Relationships (CHI '21)](https://doi.org/10.1145/3411763.3451605):

**paper.ja.md (excerpt)**

```markdown
## 1 INTRODUCTION AND BACKGROUND

ヒューマン・コンピュータ・インタラクション（HCI）研究者たちは...

![Figure 1: Nukadoko fermentation involving human, veg-](images/figure_1.jpeg)
```

**paper.summary.ja.md**

```markdown
# Nukabot: Design of Care for Human-Microbe Relationships — 要約

## 一言まとめ
日本の伝統的な発酵食品「糠床」を音声対話付きのスマート桶「Nukabot」に進化させ、
人間と微生物の間に情動的・倫理的関係を育むHCIデザインを提案・評価した研究。
```

## :building_construction: How It Works

1. **Step 0** — PDFファイルの特定と出力フォルダの作成
2. **Step 1** — PDFから図表画像を抽出 (`pymupdf`)
3. **Step 2** — PDFをセクション構造付きMarkdownに変換
4. **Step 3** — 日本語に翻訳（見出しは英語保持）
5. **Step 4** — 構造化サマリーを生成
6. **Step 5** — pandoc + lualatex で PDF を生成
7. **Step 6** — 最終確認と完了報告

## :file_folder: File Structure

```
paper-translator-en2ja/
├── SKILL.md    — Claude Code skill definition (main logic)
├── LICENSE     — AGPL-v3
└── README.md   — This file
```

## :scroll: License

[GNU Affero General Public License v3.0](LICENSE)
