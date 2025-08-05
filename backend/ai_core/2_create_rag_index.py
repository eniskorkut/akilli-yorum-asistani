import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def chunk_text(text, max_length=200):
    """
    Yorumu anlamlı ve kısa parçalara böler. Noktalama ve uzunluk dikkate alınır.
    """
    import re
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ''
    for sent in sentences:
        if len(current) + len(sent) <= max_length:
            current += (' ' if current else '') + sent
        else:
            if current:
                chunks.append(current.strip())
            current = sent
    if current:
        chunks.append(current.strip())
    return [c for c in chunks if c]

def main():
    # Script'in bulunduğu dizini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Yorumları oku
    reviews_path = os.path.join(script_dir, 'reviews.json')
    with open(reviews_path, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    # 2. Chunk'lara ayır
    all_chunks = []
    for review in reviews:
        text = review.get('comment', '')
        if text:
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
    print(f"Toplam {len(all_chunks)} metin parçası oluşturuldu.")
    # 3. Embedding modeli yükle
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(all_chunks, show_progress_bar=True, convert_to_numpy=True)
    # 4. FAISS indeksi oluştur
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    index_path = os.path.join(script_dir, 'index.faiss')
    faiss.write_index(index, index_path)
    print(f"FAISS indeksi '{index_path}' olarak kaydedildi.")
    # 5. Chunks'ı kaydet
    chunks_path = os.path.join(script_dir, 'chunks.json')
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"Tüm metin parçaları '{chunks_path}' olarak kaydedildi.")

if __name__ == "__main__":
    main()
