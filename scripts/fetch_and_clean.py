import json
import urllib.request
import os

# Fungsi untuk memuat lookup
def load_lookup(filename):
    with open(f'lookup/{filename}', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # 1. Muat data lookup
    levels = {item['schoolLevelId']: item['schoolLevelName'] for item in load_lookup('school_levels.json')}
    classes = {item['classId']: item['className'] for item in load_lookup('school_classes.json')}
    subjects = {item['subjectId']: item['subjectName'] for item in load_lookup('subjects.json')}

    # 2. Ambil data dari API SIBI (contoh endpoint)
    # Menggunakan endpoint dari BLUEPRINT.md
    url = "https://api.buku.cloudapp.web.id/api/catalogue/getTextBooks?limit=2000&type_pdf&order_by=updated_at"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        raw_data = json.loads(response.read().decode())

    cleaned_books = []
    
    # 3. Proses dan bersihkan data
    for book in raw_data:
        # Ekstrak ID dan terjemahkan ke teks
        book_id = book.get('id')
        title = book.get('title')
        author = book.get('author')
        description = book.get('description', '') # Sinopsis mengikuti API
        
        level_id = book.get('schoolLevelId')
        class_id = book.get('classId')
        subject_id = book.get('subjectId')
        
        # Ambil URL Cover & PDF
        cover_url = book.get('physicalDescription', {}).get('coverImage', '')
        pdf_url = book.get('pdfUrl', '') # Sesuaikan dengan field asli API
        
        cleaned_book = {
            "id": book_id,
            "title": title,
            "author": author,
            "curriculum": "Kurikulum Merdeka", # Asumsi, atau bisa dideteksi dari field lain
            "level": levels.get(level_id, "Lainnya"),
            "grade": classes.get(class_id, "-"),
            "subject": subjects.get(subject_id, "Umum"),
            "synopsis": description,
            "cover_url": cover_url,
            "pdf_url": pdf_url,
            "is_available": True
        }
        cleaned_books.append(cleaned_book)

    # 4. Simpan ke file JSON
    os.makedirs('data', exist_ok=True)
    with open('data/books_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_books, f, indent=2, ensure_ascii=False)
        
    print(f"Berhasil memproses {len(cleaned_books)} buku.")

if __name__ == "__main__":
    main()
