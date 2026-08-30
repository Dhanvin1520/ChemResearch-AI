import math
from typing import Optional


def recall_at_k(retrieved_ids: list[int], relevant_ids: list[int], k: int = 10) -> float:
    if not relevant_ids:
        return 0.0
    retrieved_set = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    return len(retrieved_set & relevant_set) / len(relevant_set)


def precision_at_k(retrieved_ids: list[int], relevant_ids: list[int], k: int = 10) -> float:
    if k == 0:
        return 0.0
    retrieved_set = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    return len(retrieved_set & relevant_set) / k


def average_precision(retrieved_ids: list[int], relevant_ids: list[int]) -> float:
    if not relevant_ids:
        return 0.0

    relevant_set = set(relevant_ids)
    num_relevant = 0
    sum_precision = 0.0

    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in relevant_set:
            num_relevant += 1
            sum_precision += num_relevant / (i + 1)

    return sum_precision / len(relevant_set)


def mean_reciprocal_rank(ranked_results: list[list[int]], relevant_sets: list[list[int]]) -> float:
    if not ranked_results:
        return 0.0

    rr_sum = 0.0
    for retrieved, relevant in zip(ranked_results, relevant_sets):
        relevant_set = set(relevant)
        for rank, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant_set:
                rr_sum += 1.0 / rank
                break

    return rr_sum / len(ranked_results)


def ndcg_at_k(retrieved_ids: list[int], relevant_ids: list[int], k: int = 10) -> float:
    if not relevant_ids:
        return 0.0

    relevant_set = set(relevant_ids)

    dcg = 0.0
    for i, doc_id in enumerate(retrieved_ids[:k]):
        relevance = 1.0 if doc_id in relevant_set else 0.0
        dcg += relevance / math.log2(i + 2)

    ideal_relevance = sorted([1.0 if doc_id in relevant_set else 0.0 for doc_id in retrieved_ids[:k]], reverse=True)
    ideal_relevance.extend([1.0] * max(0, min(k, len(relevant_set)) - len(ideal_relevance)))

    idcg = 0.0
    for i, rel in enumerate(ideal_relevance[:k]):
        idcg += rel / math.log2(i + 2)

    return dcg / idcg if idcg > 0 else 0.0


def entity_precision_recall_f1(
    extracted: list[str],
    expected: list[str],
) -> dict:
    if not expected and not extracted:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not expected:
        return {"precision": 0.0, "recall": 1.0, "f1": 0.0}
    if not extracted:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    extracted_set = set(e.lower().strip() for e in extracted)
    expected_set = set(e.lower().strip() for e in expected)

    true_positives = len(extracted_set & expected_set)
    precision = true_positives / len(extracted_set) if extracted_set else 0.0
    recall = true_positives / len(expected_set) if expected_set else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def faithfulness_score(claims: list[dict]) -> float:
    if not claims:
        return 1.0

    supported = sum(1 for c in claims if c.get("supported", False))
    return round(supported / len(claims), 4)


def citation_accuracy(citations: list[dict], evidence: list[dict]) -> float:
    if not citations:
        return 1.0

    evidence_map = {}
    for i, ev in enumerate(evidence, 1):
        evidence_map[i] = ev.get("content", "").lower()

    accurate = 0
    for citation in citations:
        citation_id = citation.get("citation_id", 0)
        evidence_text = citation.get("evidence_text", "").lower()

        if citation_id in evidence_map:
            source_text = evidence_map[citation_id]
            key_words = [w for w in evidence_text.split() if len(w) > 3][:10]
            matching = sum(1 for w in key_words if w in source_text)
            if matching >= max(1, len(key_words) // 3):
                accurate += 1

    return round(accurate / len(citations), 4)


def aggregate_metrics(all_metrics: list[dict]) -> dict:
    if not all_metrics:
        return {}

    aggregated = {}
    keys = all_metrics[0].keys()

    for key in keys:
        values = [m[key] for m in all_metrics if isinstance(m.get(key), (int, float))]
        if values:
            aggregated[key] = {
                "mean": round(sum(values) / len(values), 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
                "count": len(values),
            }

    return aggregated
