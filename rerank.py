# reranks the top results from retrieval.py
#
# tries a real cross-encoder model first (ms-marco-MiniLM, via
# sentence-transformers) since that's what the report proposes and it
# actually models query+passage together, unlike plain word overlap.
# needs internet to download the model, so if that's not available we
# fall back to scoring how many query words appear in the passage instead.

from retrieval import tokenize

try:
    from sentence_transformers import CrossEncoder
    _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    print("reranker: using cross-encoder/ms-marco-MiniLM-L-6-v2")
except Exception as e:
    _cross_encoder = None
    print(f"reranker: could not load cross-encoder ({e}) - falling back to word overlap")


def rerank(query, candidates, top_n=5):
    if _cross_encoder is not None:
        pairs = [(query, c["text"]) for c, _ in candidates]
        scores = _cross_encoder.predict(pairs)
        scored = [(candidates[i][0], float(scores[i])) for i in range(len(candidates))]
    else:
        q_words = set(tokenize(query))
        scored = []
        for chunk, old_score in candidates:
            words = tokenize(chunk["text"])
            overlap = len(q_words.intersection(words))
            score = overlap / max(1, len(q_words))
            scored.append((chunk, score))

    scored.sort(key=lambda x: -x[1])
    return scored[:top_n]
