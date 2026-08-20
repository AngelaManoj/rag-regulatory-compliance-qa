# hybrid retrieval: BM25 (word matching) + a dense embedding search,
# combined together. this is the "hybrid retrieval" bit from the report.
#
# for the dense part we try to use a real sentence-embedding model
# (all-MiniLM-L6-v2, via sentence-transformers) since this is a deep
# learning module and a proper embedding model is what the report actually
# proposes. that needs internet access to download the model the first
# time though, so if it's not available (no internet, package not
# installed) we fall back to TF-IDF + cosine similarity instead, which is
# not a neural model but at least keeps the pipeline runnable anywhere.
# whichever one loads gets printed so it's obvious which mode you're in.

import re
import math
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    HAVE_SBERT = True
except ImportError:
    HAVE_SBERT = False


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25:
    # standard BM25 formula, nothing fancy
    def __init__(self, texts, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.docs = [tokenize(t) for t in texts]
        self.n_docs = len(self.docs)
        self.doc_lens = [len(d) for d in self.docs]
        self.avg_len = sum(self.doc_lens) / self.n_docs
        self.term_freqs = [Counter(d) for d in self.docs]

        df = Counter()
        for d in self.docs:
            for term in set(d):
                df[term] += 1
        self.idf = {}
        for term, n in df.items():
            self.idf[term] = math.log(1 + (self.n_docs - n + 0.5) / (n + 0.5))

    def score(self, query):
        q_terms = tokenize(query)
        scores = [0.0] * self.n_docs
        for term in q_terms:
            if term not in self.idf:
                continue
            idf = self.idf[term]
            for i in range(self.n_docs):
                f = self.term_freqs[i].get(term, 0)
                if f == 0:
                    continue
                denom = f + self.k1 * (1 - self.b + self.b * self.doc_lens[i] / self.avg_len)
                scores[i] += idf * f * (self.k1 + 1) / denom
        return scores


# only try to load the real embedding model once per run, not once per
# retriever - it's slow to retry a failed network connection every time
_sbert_model = None
_sbert_tried = False


def _get_sbert():
    global _sbert_model, _sbert_tried
    if not _sbert_tried:
        _sbert_tried = True
        if HAVE_SBERT:
            try:
                _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
                print("dense retrieval: using all-MiniLM-L6-v2 (sentence-transformers)")
            except Exception as e:
                print(f"dense retrieval: could not load embedding model ({type(e).__name__}) "
                      "- falling back to TF-IDF")
        else:
            print("dense retrieval: sentence-transformers not installed - using TF-IDF")
    return _sbert_model


class DenseSearch:
    # tries a real sentence-embedding model first, falls back to TF-IDF
    def __init__(self, texts):
        self.texts = texts
        self.model = _get_sbert()

        if self.model is not None:
            self.embeddings = self.model.encode(texts)
        else:
            self.vec = TfidfVectorizer(stop_words="english")
            self.matrix = self.vec.fit_transform(texts)

    def score(self, query):
        if self.model is not None:
            q_emb = self.model.encode([query])
            sims = cosine_similarity(q_emb, self.embeddings)[0]
        else:
            q_vec = self.vec.transform([query])
            sims = cosine_similarity(q_vec, self.matrix)[0]
        return list(sims)


def rank_from_scores(scores):
    # turns a list of scores into a list of ranks (1 = best)
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    ranks = [0] * len(scores)
    for rank, idx in enumerate(order, start=1):
        ranks[idx] = rank
    return ranks


class HybridRetriever:
    def __init__(self, chunks, w_sparse=0.5, rrf_k=60):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        self.bm25 = BM25(texts)
        self.vecs = DenseSearch(texts)
        self.w_sparse = w_sparse
        self.rrf_k = rrf_k

    def search(self, query, top_k=10):
        sparse_scores = self.bm25.score(query)
        dense_scores = self.vecs.score(query)

        sparse_ranks = rank_from_scores(sparse_scores)
        dense_ranks = rank_from_scores(dense_scores)

        # combine the two rankings - reciprocal rank fusion
        combined = []
        for i in range(len(self.chunks)):
            fused = (self.w_sparse / (self.rrf_k + sparse_ranks[i]) +
                     (1 - self.w_sparse) / (self.rrf_k + dense_ranks[i]))
            combined.append((self.chunks[i], fused))

        combined.sort(key=lambda x: -x[1])
        return combined[:top_k]
