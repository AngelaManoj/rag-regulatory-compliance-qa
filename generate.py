# generates an answer from the top passages, adds citations, and
# checks the answer is actually supported before returning it
#
# tries a real LLM call first (Claude, via the anthropic package) since
# that's what the report actually proposes for generation. needs an
# ANTHROPIC_API_KEY environment variable and internet access. if that's
# not set up, falls back to picking the best matching sentences from the
# passages instead and citing them - not a real generation model, just
# keeps the pipeline runnable without an API key.

import os
import re
from retrieval import tokenize

try:
    import anthropic
    HAVE_ANTHROPIC_LIB = True
except ImportError:
    HAVE_ANTHROPIC_LIB = False

USE_LLM = HAVE_ANTHROPIC_LIB and os.environ.get("ANTHROPIC_API_KEY")
if USE_LLM:
    print("generation: using Claude API")
else:
    print("generation: no ANTHROPIC_API_KEY set - falling back to sentence extraction")


def word_overlap(query, text):
    q = set(w for w in tokenize(query) if len(w) > 3)
    if not q:
        return 0
    t = set(tokenize(text))
    return len(q.intersection(t)) / len(q)


def call_llm(query, passages):
    client = anthropic.Anthropic()
    numbered = "\n".join(f"[{i}] {p['raw_text']}" for i, p in enumerate(passages, start=1))
    prompt = (
        "Answer the question using ONLY the numbered passages below. "
        "Put a [n] citation after every fact you use, matching the passage number. "
        "If the passages don't contain the answer, reply exactly: INSUFFICIENT_EVIDENCE\n\n"
        f"PASSAGES:\n{numbered}\n\nQUESTION: {query}\nANSWER:"
    )
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def generate_answer(query, passages, abstain_threshold=0.3):
    if not passages:
        return {"text": "INSUFFICIENT_EVIDENCE - nothing was retrieved.",
                "cites": [], "abstained": True}

    best_match = max(word_overlap(query, p["raw_text"]) for p in passages)
    if best_match < abstain_threshold:
        return {"text": "INSUFFICIENT_EVIDENCE - none of the retrieved passages "
                         "look relevant enough to answer this.",
                "cites": [], "abstained": True}

    if USE_LLM:
        text = call_llm(query, passages)
        cite_nums = set(int(n) for n in re.findall(r"\[(\d+)\]", text))
        cites = [passages[n - 1]["id"] for n in cite_nums if 0 < n <= len(passages)]
        abstained = text.strip().startswith("INSUFFICIENT_EVIDENCE")
        return {"text": text, "cites": cites, "abstained": abstained}

    # fallback: no LLM available, so just pick the best matching sentences
    # from the passages instead. not real generation, just keeps the
    # citation + abstention control flow testable without an API key.
    scored_sentences = []
    for i, p in enumerate(passages, start=1):
        for sent in re.split(r"(?<=\.)\s+", p["raw_text"]):
            if len(sent.split()) < 5:
                continue
            scored_sentences.append((word_overlap(query, sent), i, sent))

    scored_sentences.sort(key=lambda x: -x[0])
    top = [s for s in scored_sentences[:3] if s[0] > 0]

    if not top:
        return {"text": "INSUFFICIENT_EVIDENCE", "cites": [], "abstained": True}

    text = " ".join(f"{sent} [{i}]" for _, i, sent in top)
    cites = [passages[i - 1]["id"] for _, i, _ in top]
    return {"text": text, "cites": cites, "abstained": False}


def verify_answer(answer, passages):
    # drops any sentence whose numbers don't actually appear in the
    # passage it's citing - catches made-up thresholds/deadlines
    if answer["abstained"]:
        return answer

    sentences = re.findall(r"(.+?)\s*\[(\d+)\]", answer["text"])
    good = []
    for sent, idx in sentences:
        idx = int(idx)
        if idx - 1 >= len(passages):
            continue
        source = passages[idx - 1]["raw_text"]
        claim_numbers = set(re.findall(r"\d+", sent))
        source_numbers = set(re.findall(r"\d+", source))
        if claim_numbers.issubset(source_numbers):
            good.append(f"{sent.strip()} [{idx}]")

    if not good:
        return {"text": "INSUFFICIENT_EVIDENCE - could not verify the numbers "
                         "in the draft answer against the sources.",
                "cites": [], "abstained": True}

    return {"text": " ".join(good), "cites": answer["cites"], "abstained": False}
