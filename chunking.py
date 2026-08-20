# turns the documents into small chunks that we can search over
# each chunk keeps the doc id + section number so we can cite it later

def make_chunks(docs):
    chunks = []
    for doc in docs:
        for section_no, text in doc["sections"].items():
            chunk = {
                "id": doc["id"] + "::" + section_no,
                "doc_id": doc["id"],
                "section": section_no,
                # putting the doc title + section number in front of the text helps
                # the retriever match on it, and it means the chunk still makes sense
                # on its own (report calls this a "contextual header")
                "text": "[" + doc["title"] + " " + section_no + "] " + text,
                "raw_text": text,
                "current": doc["current"],
                "public": doc["public"],
                "date": doc["date"]
            }
            chunks.append(chunk)
    return chunks


def make_chunks_fixed_width(docs, width=25):
    # baseline for comparison - just cuts text every N words, ignores sentence/section
    # boundaries. used in the report to show why this is a bad idea
    chunks = []
    for doc in docs:
        words = []
        for text in doc["sections"].values():
            words += text.split()
        i = 0
        n = 0
        while i < len(words):
            piece = " ".join(words[i:i+width])
            chunks.append({
                "id": doc["id"] + "::fw" + str(n),
                "doc_id": doc["id"],
                "section": "n/a",
                "text": piece,
                "raw_text": piece,
                "current": doc["current"],
                "public": doc["public"],
                "date": doc["date"]
            })
            i += width
            n += 1
    return chunks


def filter_chunks(chunks, allow_internal=True, current_only=True):
    # this is the access control + "only current regulations" filter from the report
    out = []
    for c in chunks:
        if current_only and not c["current"]:
            continue
        if not allow_internal and not c["public"]:
            continue
        out.append(c)
    return out
