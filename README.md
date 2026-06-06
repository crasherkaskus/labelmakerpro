# LabelMaker Pro 🏷️

Aplikasi web pembuat stiker label adhesif standar Indonesia (seperti tipe Tom & Jerry 107, 109, 103, dll.) secara cepat, presisi, dan dinamis menggunakan Python (**FastAPI + Streamlit + Jinja2 + xhtml2pdf / WeasyPrint**).

Aplikasi ini menggantikan alur kerja manual "Microsoft Word + Excel Mail Merge" yang tidak presisi, dengan antarmuka web modern yang ringkas. Pengguna dapat mengimpor file Excel atau menyalin teks chat WhatsApp secara langsung, menyesuaikan gaya teks (ukuran font, tebal, miring, garis bawah), mengelola daftar template, pratinjau instan, dan mengunduh PDF siap cetak.

---

## 🚀 Fitur Utama

1. **Smart Text & Quantity Parser**:
   * Mengurai teks alamat tidak terstruktur dari chat WhatsApp.
   * **Smart Quantity Suffix Multiplier**: Mendeteksi akhiran kuantitas (contoh: `d&g 30`, `avril 4`) untuk menduplikasi baris cetak stiker secara otomatis sesuai angka yang dimasukkan.
   * **Mode 1 Baris Teks**: Opsi parsing baris tunggal yang dirancang khusus untuk label nama produk/barang tanpa kolom alamat/detail.

2. **Impor Berkas Excel (.xlsx, .xls)**:
   * Pengguna dapat mengunggah file Excel secara langsung di Tahap 1.
   * Data diimpor secara instan dan dipetakan langsung ke tabel validasi tanpa perlu melalui proses parsing teks.

3. **Manajemen Template Dinamis (CRUD)**:
   * **Universal HTML Template**: Menggunakan mesin kalkulasi dimensi CSS dinamis (`backend/templates/dynamic_label.html`) dalam satuan milimeter (`mm`) sehingga layout stiker tetap presisi tinggi.
   * **Manajemen UI (Tab Kelola Template)**: Menambah, mengubah, dan menghapus template stiker langsung dari antarmuka pengguna secara real-time tanpa menyentuh kode. Konfigurasi disimpan secara persisten di `backend/templates_config.json`.

4. **Kustomisasi Tipografi Lengkap**:
   * Mendukung pemilihan variasi font (`Arial`, `Georgia`, `Verdana`, `Courier New`, dll.).
   * Opsi dekorasi teks (*Bold*, *Italic*, *Underline*) secara universal.
   * Kontrol ukuran huruf yang dinamis menyesuaikan mode stiker aktif (1 slider ukuran utama pada Mode 1 Baris, dan 3 slider terpisah untuk Mode Alamat/Multibaris).

5. **Dua Mesin Render PDF (Auto-Fallback)**:
   * **WeasyPrint**: Pilihan utama untuk akurasi render CSS tingkat tinggi (membutuhkan library GTK+).
   * **xhtml2pdf**: Berfungsi sebagai mesin cadangan (*fallback*) otomatis zero-dependency apabila library GTK+/WeasyPrint belum terinstal di sistem Windows user.

6. **Tata Letak Vertikal Ergonomis**:
   * Alur kerja bertahap yang tersusun ke bawah: **Tahap 1: Input Data / Unggah Excel** $\rightarrow$ **Tahap 2: Validasi & Edit Tabel** $\rightarrow$ **Tahap 3: Preview PDF & Cetak**.

7. **Desain Tampilan Premium**:
   * Header banner elegan yang dilengkapi dengan integrasi logo transparan resolusi tinggi modern.

---

## 📁 Struktur Direktori

```text
labelmaker/
├── backend/
│   ├── main.py              # API routing & CRUD Template (FastAPI)
│   ├── parser.py            # Logika parsing regex & kuantitas text
│   ├── generator.py         # Renderer HTML & compiler PDF (WeasyPrint/xhtml2pdf)
│   ├── templates_config.json# Database konfigurasi template stiker
│   └── templates/           # Template HTML & CSS dinamis
│       ├── base.html        # Tata letak dasar lembar cetak
│       └── dynamic_label.html # Template stiker kalkulasi presisi mm
├── frontend/
│   ├── app.py               # User Interface (Streamlit)
│   ├── logo.png             # Logo aplikasi tanpa background (transparent)
│   └── logo.jpg             # Aset logo alternatif cadangan
├── requirements.txt         # Daftar dependencies Python
└── README.md                # Dokumentasi aplikasi
```

---

## 🔧 Langkah Instalasi & Persiapan

### 1. Kloning / Unduh Proyek
Pastikan Python versi 3.9 ke atas telah terinstal pada komputer Anda.

### 2. Instalasi Dependensi Python
Buka terminal/command prompt pada direktori proyek `labelmaker` lalu jalankan perintah berikut:
```bash
pip install -r requirements.txt
```

*(Catatan: Paket `openpyxl` otomatis ikut terpasang untuk mendukung pembacaan data Excel)*

### 3. Setup Render Engine (Opsional)
Aplikasi ini secara default akan menggunakan `xhtml2pdf` jika pustaka WeasyPrint tidak dapat mendeteksi GTK+ di Windows. Jika Anda menginginkan kualitas rendering CSS paling sempurna melalui WeasyPrint:
* Unduh installer GTK+ terbaru untuk Windows di [WeasyPrint Docs](https://doc.weasyprint.org/en/stable/install.html#windows).
* Tambahkan folder `bin` dari GTK+ ke sistem variabel **PATH** komputer Anda (contoh: `C:\Program Files\GTK3-Runtime\bin`).
* Buka kembali terminal Anda agar sistem mengenali perubahan path tersebut.

---

## 🖥️ Cara Menjalankan Aplikasi

Jalankan backend API dan frontend UI di dua terminal terpisah:

### 1. Jalankan Backend (FastAPI)
```bash
uvicorn backend.main:app --reload --port 8000
```
Backend API akan berjalan di alamat `http://127.0.0.1:8000`.

### 2. Jalankan Frontend (Streamlit)
```bash
streamlit run frontend/app.py
```
Aplikasi web Streamlit akan otomatis terbuka di browser pada alamat `http://localhost:8501`.

---

## 📖 Alur Kerja Penggunaan

1. **Pilih & Konfigurasi Template**: Pada panel samping kiri, pilih stiker (misal: Tom & Jerry 107/109). Anda juga dapat mengatur ukuran font dan jenis gaya cetakan.
2. **Tahap 1: Masukkan Data**:
   * **Cara Teks**: Tempel salinan pesan chat WhatsApp ke area teks di sisi kiri dan klik **Proses & Parse Data**.
   * **Cara Excel**: Unggah file `.xlsx` / `.xls` berisi baris data label di sisi kanan lalu klik **Impor Berkas Excel**.
3. **Tahap 2: Validasi & Edit**: Data yang berhasil diimpor/diurai akan muncul di tabel validasi tengah. Anda dapat mengubah teks secara langsung pada sel tabel, menghapus baris, atau menambah baris kosong baru.
4. **Tahap 3: Preview & Cetak**: Tekan tombol **Render PDF Preview** untuk memuat tampilan lembar cetak berskala besar. Klik tombol **Unduh PDF Siap Cetak** jika sudah sesuai.
5. **Mencetak di Printer**: Buka file PDF hasil unduhan. Pada menu print, pastikan untuk mengatur skala kertas ke **Actual Size (100%)** atau matikan fitur *Fit/Scale to Page* agar ukuran cetak stiker presisi sesuai ukuran milimeter stiker fisik Anda.
