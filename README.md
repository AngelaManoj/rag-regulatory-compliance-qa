# RAG prototype - Q1 code

Small version of the pipeline from the report: retrieve -> rerank -> generate -> verify.
Not production code, just enough to test the design decisions from the report
(chunking, hybrid retrieval, abstention, access control) actually work.

Two ways to run it - `RAG_Pipeline.ipynb` in Jupyter (everything in one notebook,
run cell by cell), or the `.py` files from a terminal (`python run.py`, `python tune.py`).
Same code either way.

## models

Tries real models first, falls back if they're not available:
- dense retrieval: all-MiniLM-L6-v2 embeddings, falls back to TF-IDF
- reranker: ms-marco-MiniLM cross-encoder, falls back to word overlap
- generation: Claude API (needs ANTHROPIC_API_KEY set), falls back to picking
  + citing the best matching sentences instead

whichever one loads gets printed when you run it so it's not silently using
the weaker version. when I ran this myself the models couldn't download
(no internet in my environment) so what's below is from the fallback path.
with normal internet + `pip install sentence-transformers` it downloads the
real models automatically, no code changes needed.

## the data

4 of the 5 documents are real regulatory text, checked against the actual
sources (not made up): the CBI outsourcing guidance, the CP138 consultation
paper it replaced, DORA article 19 (incident reporting deadlines), and the
fitness & probity requirement from the Central Bank Reform Act 2010. each
one says where it's from in its `source` field in corpus.py.

the 5th (internal ICT policy) is made up, because a real bank obviously
doesn't publish its internal policy anywhere - so there's nothing real to
source. it's labelled `[ILLUSTRATIVE, NOT A REAL DOCUMENT]` right in the
title rather than pretending it's real. it's also the one document marked
non-public, which is needed to actually test the access control filter -
if every doc were public there'd be nothing to filter.

worth mentioning: I originally invented "20 working days" for the CBI
notification requirement. checked it against real sources and the Central
Bank actually says the opposite - no fixed timeframe is prescribed. fixed
that and it's now a test question (does it correctly say "not prescribed"
instead of making up a number).

## running it

```
pip install -r requirements.txt
python run.py
python tune.py
```
or open RAG_Pipeline.ipynb in Jupyter and run all cells.

set ANTHROPIC_API_KEY first if you want real generation instead of the
sentence-extraction fallback.

## what the numbers mean

recall@5 and mrr both come out at 1.0 but that's mostly just because the
corpus is tiny (5 docs, 7-8 chunks) - almost anything finds the right
passage at that size. wouldn't read much into the exact numbers. what's
actually worth looking at: it abstains on the questions that can't be
answered instead of guessing, the access control filter actually excludes
the internal doc when it should, and the verify step drops any sentence
whose numbers don't match the source it's citing.
