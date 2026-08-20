# tries a few different settings and picks the best one on a validation
# set, then checks it on a held-out set (so we're not just overfitting
# to the questions we tuned on)
# python tune.py

import random

from corpus import docs
from chunking import make_chunks, filter_chunks
from retrieval import HybridRetriever
from rerank import rerank
from questions import test_questions
from metrics import recall_at_k, average

answerable = [q for q in test_questions if q["gold"]]
random.seed(0)
random.shuffle(answerable)
half = len(answerable) // 2
tune_set = answerable[:half]
holdout_set = answerable[half:]

chunks = filter_chunks(make_chunks(docs), True, True)


def score_config(w_sparse, rrf_k, qset):
    retriever = HybridRetriever(chunks, w_sparse=w_sparse, rrf_k=rrf_k)
    recalls = []
    for item in qset:
        candidates = retriever.search(item["q"], top_k=10)
        top = [c for c, s in rerank(item["q"], candidates, top_n=5)]
        ids = [c["id"] for c in top]
        recalls.append(recall_at_k(ids, item["gold"], 5))
    return average(recalls)


def main():
    print("tuning on", len(tune_set), "questions, holding out", len(holdout_set))

    # just a small grid search - not a fancy optimiser, but it does the job
    # for a search space this small
    best_score = -1
    best_config = None
    for w_sparse in [0.2, 0.3, 0.5, 0.7, 0.8]:
        for rrf_k in [10, 30, 60, 100]:
            score = score_config(w_sparse, rrf_k, tune_set)
            if score > best_score:
                best_score = score
                best_config = (w_sparse, rrf_k)

    print("best config on tuning set:", best_config, "recall@5 =", round(best_score, 2))

    w_sparse, rrf_k = best_config
    holdout_score = score_config(w_sparse, rrf_k, holdout_set)
    print("same config on held-out set: recall@5 =", round(holdout_score, 2))


if __name__ == "__main__":
    main()
