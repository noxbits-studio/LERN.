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
    # 1. Muat data lookup
    levels = {item.get('schoolLevelId', ''): item.get('schoolLevelName', '') for item in load_lookup('school_levels.json') if isinstance(item, dict)}
    classes = {item.get('classId', ''): item.get('className', '') for item in load_lookup('school_classes.json') if isinstance(item, dict)}
    subjects = {item.get('subjectId', ''): item.get('subjectName', '') for item in load_lookup('subjects.json') if isinstance(item, dict)}

    # 2. Ambil data dari API SIBI
    url = "https://api.buku.cloudapp.web.id/api/catalogue/getTextBooks?limit=2000&type_pdf&order_by=updated_at"
    print(f"Mencoba mengambil data dari API...")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"Status HTTP: {response.status}")
            raw_text = response.read().decode('utf-8')
            print(f"Panjang respons: {len(raw_text)} karakter")
            print(f"Cuplikan 200 karakter pertama dari API:\n{raw_text[:200]}")
            
            raw_data = json.loads(raw_text)
    except Exception as e:
        print(f"GAGAL mengambil data dari API: {e}")
        return

    # Cek struktur respons API
    if isinstance(raw_data, dict):
        print("Respons berupa Dictionary. Mencari kunci 'data' atau 'items'...")
        if 'data' in raw_data:
            raw_data = raw_data['data']
        elif 'items' in raw_data:
            raw_data = raw_data['items']

    if not isinstance(raw_data, list):
        print("Format API tidak dikenali (Bukan List/Array). Script berhenti.")
        return

    print(f"Berhasil membaca list. Total ada {len(raw_data)} data buku mentah.")

    cleaned_books = []
    
    # 3. Proses data
    for book in raw_data:
        if not isinstance(book, dict): continue
        
        book_id = book.get('id', '')
        title = book.get('title', '')
        author = book.get('author', '')
        description = book.get('description', '')
        
        level_id = book.get('schoolLevelId', '')
        class_id = book.get('classId', '')
        subject_id = book.get('subjectId', '')
        
        cover_url = ''
        if isinstance(book.get('physicalDescription'), dict):
            cover_url = book.get('physicalDescription', {}).get('coverImage', '')
            
        pdf_url = book.get('pdfUrl', book.get('url', book.get('file', '')))
        
        cleaned_book = {
            "id": book_id,
            "title": title,
            "author": author,
            "curriculum": "Kurikulum Merdeka",
            "level": levels.get(level_id, "Lainnya"),
            "grade": classes.get(class_id, "-"),
            "subject": subjects.get(subject_id, "Umum"),
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
