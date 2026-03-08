#!/usr/bin/env python3
"""
extract_images.py  —  PDF から画像を抽出し、Markdown の Figure 参照に挿入する

使い方:
  python extract_images.py <pdf_path> <output_dir>

出力:
  <output_dir>/images/   に画像ファイルを保存
  stdout に JSON で { "figures": [ { "label": "Figure 1", "file": "images/fig1.png", "page": 1, "caption": "..." }, ... ] }
"""

import sys
import os
import json
import re
import fitz  # PyMuPDF


MIN_WIDTH  = 80   # px: これより小さい画像は装飾とみなしてスキップ
MIN_HEIGHT = 80


def extract_images(pdf_path: str, output_dir: str) -> list[dict]:
    """PDF から画像を抽出し、images/ に保存。メタデータを返す。"""
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    extracted = []
    seen_xrefs = set()

    for page_num, page in enumerate(doc, start=1):
        img_list = page.get_images(full=True)
        page_counter = 0

        for img_info in img_list:
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                pix = fitz.Pixmap(doc, xref)

                # CMYK → RGB 変換
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                # サイズフィルタ
                if pix.width < MIN_WIDTH or pix.height < MIN_HEIGHT:
                    continue

                page_counter += 1
                filename = f"page{page_num:02d}_{page_counter:02d}.png"
                filepath = os.path.join(images_dir, filename)
                pix.save(filepath)

                extracted.append({
                    "file": os.path.join("images", filename).replace("\\", "/"),
                    "page": page_num,
                    "width": pix.width,
                    "height": pix.height,
                    "xref": xref,
                })
            except Exception as e:
                sys.stderr.write(f"[WARN] xref={xref} page={page_num}: {e}\n")

    doc.close()
    return extracted


def extract_text_by_page(pdf_path: str) -> dict[int, str]:
    """ページごとのテキストを返す。"""
    doc = fitz.open(pdf_path)
    result = {}
    for page_num, page in enumerate(doc, start=1):
        result[page_num] = page.get_text()
    doc.close()
    return result


def find_captions(page_texts: dict[int, str]) -> list[dict]:
    """
    行頭の "Figure N:" / "Fig. N." パターンのみをキャプションとして検索。
    本文中のインライン参照（"...see Figure 3."）は除外する。
    """
    # 行頭または改行直後に現れる Figure N: / Figure N. のみを対象
    pattern = re.compile(
        r'(?:^|\n)(Figure\s+(\d+)|Fig\.\s*(\d+))[:\.\s]+([^\n]{5,160})',
        re.IGNORECASE
    )
    results = []
    seen = set()
    for page_num, text in page_texts.items():
        for m in pattern.finditer(text):
            num = m.group(2) or m.group(3)
            caption_text = m.group(4).strip()
            key = f"Figure {num}"
            # 本文中の参照っぽいものを除外:
            # キャプションは通常10文字以上・動詞や名詞で始まる
            # セクション番号で始まる場合はスキップ（例: "3.3 System Design"）
            if re.match(r'^\d+\.\d+', caption_text):
                continue
            # 短すぎる or "Figure" で再び始まる場合はスキップ
            if len(caption_text) < 8 or caption_text.lower().startswith("figure"):
                continue
            if key not in seen:
                seen.add(key)
                results.append({
                    "label": key,
                    "caption": caption_text,
                    "page": page_num,
                })
    results.sort(key=lambda x: int(re.search(r'\d+', x['label']).group()))
    return results


def assign_images_to_figures(
    images: list[dict],
    captions: list[dict],
) -> list[dict]:
    """
    各 Figure キャプションに最も近いページの画像を割り当てる。
    同じ画像が複数の Figure に使われないよう管理する。
    """
    used = set()
    figures = []

    for cap in captions:
        cap_page = cap["page"]
        # キャプションと同じページ、または前後1ページ以内の画像を候補に
        candidates = [
            img for img in images
            if abs(img["page"] - cap_page) <= 1 and img["xref"] not in used
        ]
        if not candidates:
            # 範囲を広げる
            candidates = [img for img in images if img["xref"] not in used]

        if candidates:
            # キャプションページとの距離が最小のものを選択（同距離ならサイズ優先）
            best = min(
                candidates,
                key=lambda img: (abs(img["page"] - cap_page), -img["width"] * img["height"])
            )
            used.add(best["xref"])
            figures.append({
                "label": cap["label"],
                "caption": cap["caption"],
                "page": cap["page"],
                "file": best["file"],
                "width": best["width"],
                "height": best["height"],
            })
        else:
            figures.append({
                "label": cap["label"],
                "caption": cap["caption"],
                "page": cap["page"],
                "file": None,
            })

    return figures


def insert_figures_into_markdown(md_path: str, figures: list[dict]) -> None:
    """
    paper.md / paper.ja.md の Figure 参照箇所の直後に
    ![Figure N: caption](images/...) を挿入する。
    すでに挿入済みの場合はスキップ。
    """
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    for fig in figures:
        if fig["file"] is None:
            continue
        label = fig["label"]          # e.g. "Figure 1"
        img_path = fig["file"]        # e.g. "images/page01_01.png"
        alt = f'{label}: {fig["caption"]}'
        img_md = f'\n\n![{alt}]({img_path})\n'

        # すでに挿入済みならスキップ
        if img_path in content:
            continue

        # "Figure N" または "Figure N:" を含む行の直後に挿入
        pattern = re.compile(
            rf'(.*{re.escape(label)}[^(\n]*\n)',
            re.IGNORECASE
        )
        match = pattern.search(content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + img_md + content[insert_pos:]

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <pdf_path> <output_dir>", file=sys.stderr)
        sys.exit(1)

    pdf_path   = sys.argv[1]
    output_dir = sys.argv[2]

    print(f"[1/3] 画像を抽出中: {pdf_path}", file=sys.stderr)
    images = extract_images(pdf_path, output_dir)
    print(f"      {len(images)} 枚の画像を抽出しました", file=sys.stderr)

    print("[2/3] Figure キャプションを検索中...", file=sys.stderr)
    page_texts = extract_text_by_page(pdf_path)
    captions   = find_captions(page_texts)
    print(f"      {len(captions)} 個のキャプションを検出しました", file=sys.stderr)

    figures = assign_images_to_figures(images, captions)

    print("[3/3] Markdown に画像参照を挿入中...", file=sys.stderr)
    for md_file in ["paper.md", "paper.ja.md"]:
        md_path = os.path.join(output_dir, md_file)
        if os.path.exists(md_path):
            insert_figures_into_markdown(md_path, figures)
            print(f"      {md_file} を更新しました", file=sys.stderr)

    # 結果を JSON で出力
    print(json.dumps({"figures": figures}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
