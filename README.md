# GraphRAG-based-GESA
This project replaces conventional GSEA with subgraph matching to extract phenotype-associated subgraphs and incorporates them as external knowledge into a GraphRAG retrieval-augmented framework, thereby enhancing the LLM’s reasoning and generation to produce highly readable, natural-language biological explanations.


### Knowledge Graph Contents

The current KG includes all **gene** nodes and **term** nodes from DisGeNET, GO, KEGG, and WikiPathway, as well as **term–gene** edges.

#### Gene nodes

* Fields: `id`, `acc`, `label`, `uri`

#### Term nodes

* **DisGeNET**: `id`, `label`, `acc`, `url`
* **GO**: `id`, `label`, `ontology_label`, `acc`, `uri`
* **KEGG**: `id`, `label`, `acc`, `uri`
* **WikiPathway**: `id`, `label`, `pathway`, `acc`, `uri`

#### Term–gene edges

* **DisGeNET**: `source`, `relation`, `target`, `source_label`, `target_label`, `resource`, `link_to_resource`
* **GO**: `source`, `relation`, `target`, `source_label`, `target_label`, `resource`, `link_to_resource`
* **KEGG**: `source`, `relation`, `target`, `source_label`, `target_label`, `resource`, `link_to_resource`
* **WikiPathway**: `source`, `relation`, `target`, `source_label`, `target_label`, `resource`, `link_to_resource`

> **Note:** `acc` denotes the **NCBI Gene ID** (Entrez GeneID).
