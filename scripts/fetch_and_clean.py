import json
import urllib.request
import os

def main():
    url = "https://api.buku.cloudapp.web.id/api/catalogue/getTextBooks?limit=2000&type_pdf&order_by=updated_at"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    print("Mengambil data dari API...")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw_text = response.read().decode('utf-8')
            raw_data = json.loads(raw_text)
    except Exception as e:
        print(f"GAGAL mengambil data dari API: {e}")
        return

    # Ambil list dari key 'results'
    if isinstance(raw_data, dict) and 'results' in raw_data:
        raw_data = raw_data['results']

    if not isinstance(raw_data, list):
        print("Format API tidak dikenali. Script berhenti.")
        return

    cleaned_books = []
    
    for book in raw_data:
        if not isinstance(book, dict): continue
        
        # Normalisasi Kurikulum
        curriculum_raw = book.get('curriculum', '')
        if '2013' in curriculum_raw:
            curriculum = 'K13'
        elif 'merdeka' in curriculum_raw.lower():
            curriculum = 'Merdeka'
        else:
            curriculum = curriculum_raw

        # Normalisasi Jenjang (SD/MI -> SD)
        level_raw = book.get('level', '')
        if 'SD' in level_raw: level = 'SD'
        elif 'SMP' in level_raw: level = 'SMP'
        elif 'SMA' in level_raw: level = 'SMA'
        elif 'SMK' in level_raw: level = 'SMK'
        else: level = level_raw

        # Ambil Deskripsi (jika kosong, pakai het_title atau title)
        synopsis = book.get('description', '')
        if not synopsis:
            synopsis = book.get('het_title', book.get('title', ''))

        cleaned_book = {
            "id": str(book.get('id', '')),
            "title": book.get('title', ''),
            "author": book.get('writer', ''),
            "curriculum": curriculum,
            "level": level,
            "grade": str(book.get('class', '')), # Kelas 1-12
            "subject": book.get('subject', '').capitalize(), # Tematik, Matematika, dll.
            "synopsis": synopsis,
            "cover_url": book.get('image', ''),
            "pdf_url": book.get('attachment', ''),
            "is_available": True
        }
        cleaned_books.append(cleaned_book)

    # Simpan ke file
    os.makedirs('data', exist_ok=True)
    with open('data/books_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_books, f, indent=2, ensure_ascii=False)
        
    print(f"Berhasil memproses dan menyimpan {len(cleaned_books)} buku ke books_catalog.json.")

if __name__ == "__main__":
    main()
