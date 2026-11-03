import json
import urllib.request
import os

def load_lookup(filename):
    try:
        with open(f'lookup/{filename}', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Peringatan: Gagal membaca {filename}: {e}")
        return []

def main():
    levels = {item.get('schoolLevelId', ''): item.get('schoolLevelName', '') for item in load_lookup('school_levels.json') if isinstance(item, dict)}
    classes = {item.get('classId', ''): item.get('className', '') for item in load_lookup('school_classes.json') if isinstance(item, dict)}
    subjects = {item.get('subjectId', ''): item.get('subjectName', '') for item in load_lookup('subjects.json') if isinstance(item, dict)}

    url = "https://api.buku.cloudapp.web.id/api/catalogue/getTextBooks?limit=2000&type_pdf&order_by=updated_at"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw_text = response.read().decode('utf-8')
            raw_data = json.loads(raw_text)
    except Exception as e:
        print(f"GAGAL mengambil data dari API: {e}")
        return

    # Perbaikan: API SIBI menggunakan key 'results'
    if isinstance(raw_data, dict):
        if 'results' in raw_data:
            raw_data = raw_data['results']
        elif 'data' in raw_data:
            raw_data = raw_data['data']

    if not isinstance(raw_data, list):
        print("Format API tidak dikenali (Bukan List/Array). Script berhenti.")
        return

    print(f"Berhasil membaca list. Total ada {len(raw_data)} data buku mentah.")

    # --- FITUR DEBUG: Mencetak 1 buku pertama secara utuh ---
    if len(raw_data) > 0:
        print("\n=== CONTOH DATA MENTAH BUKU PERTAMA ===")
        print(json.dumps(raw_data[0], indent=2))
        print("=======================================\n")
    # --------------------------------------------------------

    cleaned_books = []
    
    for book in raw_data:
        if not isinstance(book, dict): continue
        
        # Kita gunakan nama field sementara, nanti kita perbaiki setelah melihat hasil debug di atas
        book_id = book.get('id', '')
        title = book.get('title', '')
        author = book.get('author', '')
        description = book.get('description', book.get('sinopsis', '')) # Toleransi jika namanya sinopsis
        
        # Toleransi nama field untuk cover
        cover_url = book.get('image', book.get('cover', ''))
        
        # Toleransi nama field untuk PDF
        pdf_url = book.get('pdf', book.get('file_pdf', book.get('url', '')))
        
        cleaned_book = {
            "id": book_id,
            "title": title,
            "author": author,
            "curriculum": "Kurikulum Merdeka",
            "level": "Lainnya", # Sementara
            "grade": "-",       # Sementara
            "subject": "Umum",  # Sementara
            "synopsis": description,
            "cover_url": cover_url,
            "pdf_url": pdf_url,
            "is_available": True
        }
        cleaned_books.append(cleaned_book)

    # 4. Simpan ke file
    os.makedirs('data', exist_ok=True)
    with open('data/books_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_books, f, indent=2, ensure_ascii=False)
        
    print(f"Berhasil memproses dan menyimpan {len(cleaned_books)} buku.")

if __name__ == "__main__":
    main()
