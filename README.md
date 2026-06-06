# LabelMaker Pro 🏷️

Aplikasi web pembuat stiker label adhesif standar Indonesia (tipe 107 dan 109) secara cepat dan presisi menggunakan Python (FastAPI + Streamlit + Jinja2 + WeasyPrint). 

Aplikasi ini menggantikan alur kerja manual "Microsoft Word + Excel Mail Merge" yang sering mengalami masalah pergeseran layout/alignment, dengan antarmuka web modern yang ringkas di mana user cukup *copy-paste* data teks WhatsApp, melakukan edit interaktif, melihat pratinjau, lalu mengunduh PDF siap cetak.

---

## Fitur Utama
1. **Smart Text Parser**: Secara otomatis mem-parsing data alamat tidak terstruktur dari salinan chat WhatsApp atau teks baris-per-baris dengan cerdas.
2. **Interactive Data Editor**: Melakukan edit data, tambah baris, atau hapus baris langsung di tabel web sebelum dicetak.
3. **Preset Template Presisi (CSS Grid)**:
   - **Label 107**: Ukuran 18 mm x 50 mm (A4, 3 kolom, 14 baris = 42 stiker/lembar)
   - **Label 109**: Ukuran 38 mm x 82 mm (A4, 2 kolom, 7 baris = 14 stiker/lembar)
4. **Live PDF Preview**: Melihat tampilan lembaran stiker secara instan sebelum diunduh.
5. **Kustomisasi Font & Border**: Mengubah ukuran teks secara fleksibel dan menyembunyikan border bantuan potong.

---

## Struktur Direktori
```
labelmaker/
├── backend/
│   ├── main.py            # API routing & schemas (FastAPI)
│   ├── parser.py          # Logika parsing regex untuk text WhatsApp
│   ├── generator.py       # Render Jinja2 & compile ke PDF (WeasyPrint)
│   └── templates/         # Template HTML & CSS presisi tinggi (mm)
│       ├── base.html      # Tata letak dasar halaman A4 & CSS Reset
│       ├── label_107.html # Desain grid Label 107
│       └── label_109.html # Desain grid Label 109
├── frontend/
│   └── app.py             # User Interface (Streamlit)
├── requirements.txt       # Daftar package Python
└── README.md              # Dokumentasi instalasi & pemakaian
```

---

## Langkah Instalasi & Persiapan

### 1. Prasyarat Sistem
Aplikasi ini menggunakan **WeasyPrint** untuk menghasilkan dokumen PDF berkualitas tinggi yang presisi. Di sistem operasi Windows, WeasyPrint membutuhkan pustaka eksternal **GTK+** untuk merender gambar/font.

#### Cara Instalasi GTK+ di Windows:
1. Unduh installer GTK+ terbaru untuk Windows dari [gvsbuild](https://github.com/wingtk/gvsbuild) atau unduh installer portabel yang disederhanakan dari [WeasyPrint Windows Docs](https://doc.weasyprint.org/en/stable/install.html#windows).
2. Tambahkan folder `bin` dari GTK+ ke dalam sistem variabel **PATH** komputer Anda.
   *(Contoh path: `C:\Program Files\GTK3-Runtime\bin`)*.
3. Mulai ulang terminal/command prompt setelah memperbarui variabel PATH.

### 2. Instalasi Paket Python
Buka terminal di direktori proyek `labelmaker` lalu jalankan perintah berikut:
```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan Aplikasi

Aplikasi berjalan pada dua komponen terpisah (Backend API & Frontend UI). Jalankan masing-masing di jendela terminal terpisah:

### 1. Jalankan Backend (FastAPI)
```bash
uvicorn backend.main:app --reload --port 8000
```
API akan berjalan di alamat `http://127.0.0.1:8000`. Dokumen API interaktif dapat diakses di `http://127.0.0.1:8000/docs`.

### 2. Jalankan Frontend (Streamlit)
```bash
streamlit run frontend/app.py
```
Aplikasi web Streamlit akan terbuka secara otomatis di browser Anda pada alamat `http://localhost:8501`.

---

## Alur Kerja Pengguna (User Journey)
1. **Pilih Ukuran Label**: Pada panel samping kiri, pilih template label (Label 107 atau Label 109).
2. **Kustomisasi Font & Border**: Sesuaikan ukuran huruf nama/alamat dan aktifkan "Tampilkan Batas Kotak" jika Anda ingin mencetak garis putus-putus sebagai bantuan potong.
3. **Tempel Teks Mentah**: Tempel teks data nama & alamat dari WhatsApp ke area input teks.
4. **Proses & Parse**: Tekan tombol **Proses & Parse Data** untuk mengubah teks tersebut menjadi format tabel terstruktur.
5. **Validasi & Edit**: Ubah data langsung di tabel bila ada kesalahan parsing. Anda juga dapat menambah baris baru dengan menekan tombol `+` di bawah tabel.
6. **Unduh & Cetak**: Tekan tombol **Render Ulang PDF Preview** untuk melihat pratinjau stiker, lalu klik **Unduh PDF Siap Cetak** untuk mengunduh PDF.
7. **Cetak PDF**: Buka file PDF di browser atau Adobe Acrobat. Saat mencetak, pastikan untuk menyetel skala cetak pada pengaturan printer ke **Actual Size (100%)** atau **Fit/Scale to Page = None** agar ukuran stiker tetap presisi dalam milimeter.
