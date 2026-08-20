# basic retrieval metrics - recall, mrr

def recall_at_k(retrieved_ids, gold_ids, k):
    if not gold_ids:
        return None
    top = set(retrieved_ids[:k])
    return len(top.intersection(gold_ids)) / len(gold_ids)


def mrr(retrieved_ids, gold_ids):
    if not gold_ids:
        return None
    for i, cid in enumerate(retrieved_ids, start=1):
        if cid in gold_ids:
            return 1 / i
    return 0


def average(values):
    values = [v for v in values if v is not None]
    if not values:
        return 0
    return sum(values) / len(values)
