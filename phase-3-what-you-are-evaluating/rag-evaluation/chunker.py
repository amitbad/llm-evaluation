import os
import json
import re

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR     = os.path.join(SCRIPT_DIR, "documents")
OUTPUT_FILE  = os.path.join(SCRIPT_DIR, "chunks.json")


def split_into_chunks(text):
    # Split on one or more blank lines
    raw = re.split(r'\n\s*\n', text.strip())
    chunks = [c.strip() for c in raw if len(c.strip()) > 40]
    return chunks


def build_chunks():
    chunks = []
    chunk_id = 1

    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        doc_chunks = split_into_chunks(text)

        for chunk_text in doc_chunks:
            chunks.append({
                "id":     chunk_id,
                "source": filename,
                "text":   chunk_text
            })
            chunk_id += 1

    return chunks


if __name__ == "__main__":
    chunks = build_chunks()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    # Summary
    from collections import Counter
    by_doc = Counter(c["source"] for c in chunks)
    print(f"Total chunks: {len(chunks)}")
    for doc, count in sorted(by_doc.items()):
        print(f"  {doc}: {count} chunks")
    print(f"Saved to: {OUTPUT_FILE}")
