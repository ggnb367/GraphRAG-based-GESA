"""
Utility for generating a compact knowledge graph from the provided node and edge CSVs.

The script keeps only the lightweight fields requested for downstream PCST matching:
* Gene nodes: `label` (gene symbol)
* Term nodes: `label`
* Triples: `source_label`, `relation`, `target_label`
* A leading ``counts`` object capturing totals for genes, terms, and triples

By default, the script consumes the contents of the ``data`` directory in this
repository and writes a JSON file containing the condensed nodes and triples.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


@dataclass
class GeneNode:
    """Gene node retaining only the ``label`` field."""

    label: str

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "GeneNode":
        label = row.get("label")
        if not label:
            raise ValueError("Gene row is missing required 'label' column")
        return cls(label=label)


@dataclass
class TermNode:
    """Term node retaining only the ``label`` field."""

    label: str

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "TermNode":
        label = row.get("label")
        if not label:
            raise ValueError("Term row is missing required 'label' column")
        return cls(label=label)


@dataclass
class Edge:
    """Edge representation limited to labels and relation identifiers."""

    source_label: str
    relation: str
    target_label: str

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "Edge":
        source_label = row.get("source_label")
        relation = row.get("relation")
        target_label = row.get("target_label")
        if not source_label or not relation or not target_label:
            raise ValueError(
                "Edge row is missing required 'source_label', 'relation', or 'target_label' column"
            )
        return cls(source_label=source_label, relation=relation, target_label=target_label)


def _read_csv_rows(file_path: Path) -> Iterable[Dict[str, str]]:
    """Yield dictionaries for each row in a CSV file."""

    with file_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def load_gene_nodes(gene_node_path: Path) -> List[GeneNode]:
    rows = list(_read_csv_rows(gene_node_path))
    genes: List[GeneNode] = []
    for idx, row in enumerate(rows, start=1):
        try:
            genes.append(GeneNode.from_row(row))
        except ValueError as exc:
            print(f"Skipping invalid gene row #{idx} in {gene_node_path}: {exc}")
    return genes


def load_term_nodes(term_dir: Path) -> List[TermNode]:
    term_files = sorted(term_dir.glob("*.csv"))
    terms: List[TermNode] = []
    for file_path in term_files:
        for idx, row in enumerate(_read_csv_rows(file_path), start=1):
            try:
                terms.append(TermNode.from_row(row))
            except ValueError as exc:
                print(f"Skipping invalid term row #{idx} in {file_path}: {exc}")
    return terms


def load_edges(edge_dir: Path) -> List[Edge]:
    edge_files = sorted(edge_dir.glob("*.csv"))
    edges: List[Edge] = []
    for file_path in edge_files:
        for idx, row in enumerate(_read_csv_rows(file_path), start=1):
            try:
                edges.append(Edge.from_row(row))
            except ValueError as exc:
                print(f"Skipping invalid edge row #{idx} in {file_path}: {exc}")
    return edges


def build_knowledge_graph(
    gene_nodes: Sequence[GeneNode], term_nodes: Sequence[TermNode], edges: Sequence[Edge]
) -> Dict[str, object]:
    """Assemble the compact knowledge graph payload."""
    payload = OrderedDict()
    payload["counts"] = {
        "genes": len(gene_nodes),
        "terms": len(term_nodes),
        "triples": len(edges),
    }
    payload["genes"] = [gene.__dict__ for gene in gene_nodes]
    payload["terms"] = [term.__dict__ for term in term_nodes]
    payload["triples"] = [edge.__dict__ for edge in edges]
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a compact KG JSON from node and edge CSVs.")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data"),
        help="Root directory containing gene_node, term_node, and term_gene_edge subdirectories.",
    )
    parser.add_argument(
        "--gene-file",
        type=Path,
        default=Path("gene_node/Gene.nodes.csv"),
        help="CSV file with gene nodes (expects a 'label' column).",
    )
    parser.add_argument(
        "--term-dir",
        type=Path,
        default=Path("term_node"),
        help="Directory containing term node CSV files.",
    )
    parser.add_argument(
        "--edge-dir",
        type=Path,
        default=Path("term_gene_edge"),
        help="Directory containing term-gene edge CSV files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("compact_kg.json"),
        help="Path to the output JSON file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    gene_file = args.gene_file if args.gene_file.is_absolute() else args.data_root / args.gene_file
    term_dir = args.term_dir if args.term_dir.is_absolute() else args.data_root / args.term_dir
    edge_dir = args.edge_dir if args.edge_dir.is_absolute() else args.data_root / args.edge_dir

    gene_nodes = load_gene_nodes(gene_file)
    term_nodes = load_term_nodes(term_dir)
    edges = load_edges(edge_dir)

    kg_payload = build_knowledge_graph(gene_nodes, term_nodes, edges)

    output_path = args.output if args.output.is_absolute() else args.data_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(kg_payload, f, ensure_ascii=False, indent=2)

    print(f"Compact knowledge graph written to {output_path}")


if __name__ == "__main__":
    main()