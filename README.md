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


## ES (Enrichment Score)

1. Match the input ranked gene list against the target gene set and build a binary `tag_indicator` vector  
   (1 = gene is in the set, 0 = not in the set).

2. For the corresponding ranking metric / score vector `score`, construct a weighting vector `weight` by  
   taking `|score|` to a user-defined power.  
   When `weight = 0`, all hit weights are set to 1.  
   This produces the weighted “hit increment” for each gene in the set.

3. Compute the running-sum statistic `RES` along the ranked list:  
   - At each hit position, increase `RES` by `|score|^weight / sum_hit_scores`.  
   - At each miss position, decrease `RES` by `1 / N_miss`.  

   The Enrichment Score **ES** is defined as the maximum absolute deviation of `RES` from zero.  
   A positive ES indicates that the gene set is enriched toward the top of the ranked list,  
   while a negative ES indicates enrichment toward the bottom.

---

## NES (Normalized ES)

1. Generate a null distribution `esnull` for each pathway by permuting gene labels  
   (typically 1,000 permutations).

2. From the permuted results, compute separately:  
   - the mean of positive ES values: `esnull_pos`  
   - the mean of negative ES values: `esnull_neg`.

3. Normalize the observed ES using these means:

   - If `ES > 0`: `NES = ES / mean(esnull_pos)`  
   - If `ES < 0`: `NES = -ES / mean(esnull_neg)`

   The permuted ES values in `esnull` are normalized in the same way and are then used  
   to compute p-values and FDR.
