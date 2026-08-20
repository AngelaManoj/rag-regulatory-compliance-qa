# main script - run this to see the whole pipeline working
# python run.py

from corpus import docs
from chunking import make_chunks, make_chunks_fixed_width, filter_chunks
from retrieval import HybridRetriever
from rerank import rerank
from generate import generate_answer, verify_answer
from questions import test_questions
from metrics import recall_at_k, mrr, average


def answer_question(retriever, query, use_reranker=True, use_verifier=True):
    candidates = retriever.search(query, top_k=10)
    if use_reranker:
        top_passages = [c for c, s in rerank(query, candidates, top_n=5)]
    else:
        top_passages = [c for c, s in candidates[:5]]

    answer = generate_answer(query, top_passages)
    if use_verifier:
        answer = verify_answer(answer, top_passages)
    return answer, top_passages


def main():
    # only keep current (not superseded) chunks, internal access allowed
    chunks = filter_chunks(make_chunks(docs), allow_internal=True, current_only=True)
    retriever = HybridRetriever(chunks)

    print("=== indexed", len(chunks), "chunks ===\n")

    print("=== example answers ===")
    for item in test_questions[:3] + [test_questions[-1]]:
        answer, passages = answer_question(retriever, item["q"])
        print("\nQ:", item["q"])
        print("A:", answer["text"])
        print("   cites:", answer["cites"], "  abstained:", answer["abstained"])

    print("\n=== retrieval accuracy (recall@5, mrr) ===")
    recalls, mrrs = [], []
    for item in test_questions:
        if not item["gold"]:
            continue
        candidates = retriever.search(item["q"], top_k=10)
        top = [c for c, s in rerank(item["q"], candidates, top_n=5)]
        ids = [c["id"] for c in top]
        recalls.append(recall_at_k(ids, item["gold"], 5))
        mrrs.append(mrr(ids, item["gold"]))
    print("recall@5:", round(average(recalls), 2))
    print("mrr:", round(average(mrrs), 2))

    print("\n=== does it abstain on unanswerable questions? ===")
    for item in test_questions:
        if item["gold"]:
            continue
        answer, _ = answer_question(retriever, item["q"])
        print("-", item["q"], "-> abstained:", answer["abstained"])

    print("\n=== chunking comparison (structure-aware vs fixed-width) ===")
    fw_chunks = filter_chunks(make_chunks_fixed_width(docs), True, True)
    fw_retriever = HybridRetriever(fw_chunks)
    struct_recalls, fw_recalls = [], []
    for item in test_questions:
        if not item["gold"]:
            continue
        struct_top = [c["id"] for c, s in retriever.search(item["q"], top_k=5)]
        struct_recalls.append(recall_at_k(struct_top, item["gold"], 5))
        # fixed-width chunk ids don't line up with gold section ids, so just
        # check whether the right *document* shows up instead
        fw_top_docs = [c["doc_id"] for c, s in fw_retriever.search(item["q"], top_k=5)]
        gold_docs = set(g.split("::")[0] for g in item["gold"])
        fw_recalls.append(1 if any(d in gold_docs for d in fw_top_docs) else 0)
    print("structure-aware recall@5:", round(average(struct_recalls), 2))
    print("fixed-width recall@5 (doc level):", round(average(fw_recalls), 2))

    print("\n=== access control check ===")
    # a user without internal clearance should not see the internal policy doc
    public_chunks = filter_chunks(make_chunks(docs), allow_internal=False, current_only=True)
    public_retriever = HybridRetriever(public_chunks)
    q = "What annual contract value triggers escalation to the Group Outsourcing Committee?"
    internal_answer, _ = answer_question(retriever, q)
    public_answer, _ = answer_question(public_retriever, q)
    print("internal user - abstained:", internal_answer["abstained"])
    print("public user   - abstained:", public_answer["abstained"], "(should be True)")


if __name__ == "__main__":
    main()
