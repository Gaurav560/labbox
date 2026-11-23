"""Chapter 8: run with  python store.py   Fieldbook's chunks in a Qdrant collection, searched with filters."""
from fieldbook import COLLECTION, embed, filtered_search, load_corpus, make_store, normalize, chunk_text

chunks = load_corpus()
client = make_store(chunks, normalize(embed([chunk_text(c) for c in chunks])))
print(f"{client.count(COLLECTION).count} points in the collection {COLLECTION!r}\n")

question = "a leopard near people"
query = normalize(embed([question])[0])
for label, options in [("no filter", {}), ("reports only", {"kind": "report"}),
                       ("reports from the buffer zone", {"kind": "report", "zone": "buffer"})]:
    print(f"{question!r}, {label}:")
    for hit in filtered_search(client, query, k=3, **options):
        print(f"  {hit['score']:.3f}  [{hit['id']}] {hit['title']}")
    print()
