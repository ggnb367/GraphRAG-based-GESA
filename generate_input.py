
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
下载人类全部 HGNC 基因，随机打分并生成一个 pre-ranked GSEA 输入 txt。

输出格式（无表头，两列，制表符分隔）：
GENE_SYMBOL <TAB> SCORE

示例用法：
    python make_human_gsea_list.py
    python make_human_gsea_list.py --protein-coding-only --out human_pc_genes_preranked.txt
"""

import argparse
import csv
import random
import sys
from typing import List, Tuple
from urllib.request import urlopen

# HGNC 官方 complete set TSV（2025 年已经从 FTP 改到 Google Storage）
HGNC_TSV_URL = (
    "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt"
)


def download_hgnc_tsv(url: str = HGNC_TSV_URL) -> str:
    """下载 HGNC complete set TSV 并以字符串形式返回。"""
    print(f"[INFO] Downloading HGNC complete set from:\n  {url}")
    with urlopen(url) as resp:
        data = resp.read().decode("utf-8")
    print("[INFO] Download complete.")
    return data


def parse_gene_symbols(
    tsv_text: str,
    protein_coding_only: bool = False,
) -> List[str]:
    """
    从 hgnc_complete_set 中解析基因符号列表。

    默认只保留 status == 'Approved' 的基因。
    若 protein_coding_only=True，则进一步要求 locus_group == 'protein-coding gene'。
    """
    reader = csv.DictReader(tsv_text.splitlines(), delimiter="\t")
    genes: List[str] = []

    n_total = 0
    for row in reader:
        n_total += 1
        symbol = (row.get("symbol") or "").strip()
        status = (row.get("status") or "").strip()

        if not symbol:
            continue
        if status != "Approved":
            continue

        if protein_coding_only:
            locus_group = (row.get("locus_group") or "").strip()
            if locus_group != "protein-coding gene":
                continue

        genes.append(symbol)

    print(f"[INFO] Parsed {len(genes)} genes "
          f"({'protein-coding only' if protein_coding_only else 'all Approved'}) "
          f"from {n_total} rows.")
    return genes


def assign_random_scores(
    genes: List[str],
    seed: int = 42,
) -> List[Tuple[str, float]]:
    """
    为每个基因分配一个随机得分，并按得分从大到小排序。

    这里用的是 N(0,1) 高斯分布，模拟 GSEA 里那种连续统计量。
    你可以根据需要替换成别的分布。
    """
    random.seed(seed)
    scores = [(g, random.gauss(0.0, 1.0)) for g in genes]
    scores.sort(key=lambda x: x[1], reverse=True)
    print(f"[INFO] Assigned random scores to {len(scores)} genes.")
    return scores


def write_preranked_file(
    scores: List[Tuple[str, float]],
    out_path: str,
) -> None:
    """
    将 (gene, score) 列表写出为两列 txt 文件：
    GENE_SYMBOL<TAB>SCORE
    """
    with open(out_path, "w", encoding="utf-8") as f:
        for gene, score in scores:
            f.write(f"{gene}\t{score:.6f}\n")

    print(f"[INFO] Wrote pre-ranked gene list to: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a pre-ranked GSEA input file for all human genes."
    )
    parser.add_argument(
        "--protein-coding-only",
        action="store_true",
        help="只保留 protein-coding gene（默认：所有 Approved 基因）。",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="human_genes_preranked.txt",
        help="输出文件名（默认：human_genes_preranked.txt）。",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机数种子（默认：42）。",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=HGNC_TSV_URL,
        help="HGNC TSV 下载地址（一般不需要改）。",
    )

    args = parser.parse_args()

    try:
        tsv_text = download_hgnc_tsv(args.url)
    except Exception as e:
        print(f"[ERROR] Failed to download HGNC TSV: {e}", file=sys.stderr)
        sys.exit(1)

    genes = parse_gene_symbols(
        tsv_text,
        protein_coding_only=args.protein_coding_only,
    )
    if not genes:
        print("[ERROR] No genes were parsed. Check the TSV format / filters.",
              file=sys.stderr)
        sys.exit(1)

    scores = assign_random_scores(
        genes,
        seed=args.seed,
    )
    write_preranked_file(scores, args.out)


if __name__ == "__main__":
    main()
