import streamlit as st
import requests
import pandas as pd
import base64
import os

# Backend API configuration
API_BASE_URL = os.environ.get("LABELMAKER_API_URL", "http://127.0.0.1:8000")

# Page configuration
st.set_page_config(
    page_title="LabelMaker Pro - Cetak Presisi",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS for professional aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8F8F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #111111;
        margin-bottom: 1rem;
        border-bottom: 2px solid #FF4B4B;
        padding-bottom: 0.5rem;
    }
    
    /* Step numbering badges */
    .step-badge {
        background-color: #FF4B4B;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to render PDF in iframe
def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Initialize Session State for parsed label data
if "parsed_labels" not in st.session_state:
    st.session_state.parsed_labels = []

# Fetch active templates from API
def fetch_templates():
    try:
        res = requests.get(f"{API_BASE_URL}/api/templates")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Gagal menghubungi server backend API: {e}")
    return {}

active_templates = fetch_templates()

# Main Layout
logo_png_path = os.path.join(os.path.dirname(__file__), "logo.png")
if os.path.exists(logo_png_path):
    with open(logo_png_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 25px; padding: 10px 0;">
        <img src="data:image/png;base64,{logo_base64}" width="85" style="filter: drop-shadow(0px 4px 8px rgba(0, 0, 0, 0.08));"/>
        <div>
            <h1 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 3.2rem; font-weight: 800; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">Label Maker Pro</h1>
            <p style="margin: 6px 0 0 0; font-family: 'Outfit', sans-serif; font-size: 1.15rem; color: #4b5563; font-weight: 500; letter-spacing: 0.3px;">print labels fast, parse chat, auto table, ready to print</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<p class="main-title">🏷️ LabelMaker Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Aplikasi Pembuat Label Stiker Presisi Standar Indonesia dengan Template Dinamis</p>', unsafe_allow_html=True)



# Organize workspace into Tabs
tab_print, tab_manage = st.tabs(["🖨️ Cetak Label", "⚙️ Kelola Template"])

# ================= TAB 1: CETAK LABEL =================
with tab_print:
    # Sidebar: Template Settings
    with st.sidebar:
        st.markdown('<p class="sidebar-header">⚙️ Pengaturan Cetak</p>', unsafe_allow_html=True)
        
        # Template Selection
        if active_templates:
            template_options = list(active_templates.keys())
            template_type = st.selectbox(
                "Pilih Ukuran Label:",
                options=template_options,
                format_func=lambda x: active_templates[x].get("name", x)
            )
            selected_config = active_templates[template_type]
        else:
            st.warning("Tidak ada template aktif. Tambahkan template terlebih dahulu.")
            template_type = None
            selected_config = None

        if selected_config:
            st.markdown("---")
            single_line_mode = st.toggle(
                "Mode 1 Baris Teks",
                value=False,
                help="Aktifkan untuk cetak label parfum / nama barang saja (hanya kolom nama yang dicetak di tengah stiker)."
            )
            
            st.markdown("---")
            st.markdown("#### 📐 Kustomisasi Ukuran Font (pt)")
            
            # Determine initial values based on height heuristic
            h = selected_config.get("label_height", 20.0)
            def_name = 12.0 if h > 25 else 10.0
            def_addr = 9.0 if h > 25 else 8.0
            def_det = 8.0 if h > 25 else 7.0
            
            if single_line_mode:
                font_size_name = st.slider(
                    "Ukuran Font Teks Utama:", min_value=6.0, max_value=24.0, value=float(def_name), step=0.5
                )
                font_size_address = None
                font_size_detail = None
            else:
                font_size_name = st.slider(
                    "Ukuran Font Nama:", min_value=6.0, max_value=20.0, value=float(def_name), step=0.5
                )
                font_size_address = st.slider(
                    "Ukuran Font Alamat:", min_value=5.0, max_value=16.0, value=float(def_addr), step=0.5
                )
                font_size_detail = st.slider(
                    "Ukuran Font Detail (HP/Kota):", min_value=4.0, max_value=14.0, value=float(def_det), step=0.5
                )
            
            st.markdown("---")
            st.markdown("#### 🎨 Gaya & Variasi Teks")
            font_family = st.selectbox(
                "Jenis Font:",
                options=["Arial", "Courier New", "Georgia", "Times New Roman", "Verdana", "Impact"],
                index=0
            )
            col_b, col_i, col_u = st.columns(3)
            with col_b:
                font_bold = st.checkbox("Bold", value=False)
            with col_i:
                font_italic = st.checkbox("Italic", value=False)
            with col_u:
                font_underline = st.checkbox("Underline", value=False)
                
            st.markdown("---")
            st.markdown("#### 👁️ Opsi Tampilan")
            show_borders = st.checkbox(
                "Tampilkan Batas Kotak",
                value=True,
                help="Gunakan opsi ini untuk membantu memotong stiker. Matikan saat mencetak langsung pada kertas label berperekat."
            )

    # Step 1: Input Data (Horizontal columns for WA text and Excel upload)
    st.markdown('### <span class="step-badge">1</span> Masukkan Data', unsafe_allow_html=True)
    col_text, col_excel = st.columns(2)
    
    with col_text:
        with st.container(border=True):
            st.markdown("##### 📋 Salinan Chat (WhatsApp / Clipboard)")
            raw_text = st.text_area(
                "Tempel teks mentah di bawah:",
                height=150,
                placeholder="Contoh:\nbulgary aqua 3\naqua kis 1\navril 4\nd&g 30",
                key="wa_text_input"
            )
            
            if st.button("🚀 Proses & Parse Teks WA", use_container_width=True):
                if not raw_text.strip():
                    st.warning("Silakan tempel data teks terlebih dahulu.")
                else:
                    with st.spinner("Sedang mem-parsing data..."):
                        try:
                            res = requests.post(
                                f"{API_BASE_URL}/api/parse",
                                json={"raw_text": raw_text, "single_line_mode": single_line_mode}
                            )
                            if res.status_code == 200:
                                st.session_state.parsed_labels = res.json()
                                st.success(f"Berhasil mem-parse {len(st.session_state.parsed_labels)} data label!")
                                st.rerun()
                            else:
                                st.error(f"Gagal mem-parse data: {res.text}")
                        except Exception as e:
                            st.error(f"Terjadi kesalahan koneksi API: {str(e)}")
                            
    with col_excel:
        with st.container(border=True):
            st.markdown("##### 📁 Unggah File Spreadsheet (Excel)")
            uploaded_file = st.file_uploader(
                "Pilih berkas Excel (.xlsx, .xls):", 
                type=["xlsx", "xls"],
                key="excel_uploader"
            )
            
            if uploaded_file is not None:
                if st.button("📥 Impor dari Excel", use_container_width=True):
                    with st.spinner("Sedang memproses file Excel..."):
                        try:
                            df_uploaded = pd.read_excel(uploaded_file)
                            if not df_uploaded.empty:
                                mapped_data = []
                                cols = list(df_uploaded.columns)
                                
                                for _, row in df_uploaded.iterrows():
                                    item = {"nama": "", "alamat": "", "detail": ""}
                                    if len(cols) > 0:
                                        item["nama"] = str(row[cols[0]]) if pd.notna(row[cols[0]]) else ""
                                    if len(cols) > 1:
                                        item["alamat"] = str(row[cols[1]]) if pd.notna(row[cols[1]]) else ""
                                    if len(cols) > 2:
                                        item["detail"] = str(row[cols[2]]) if pd.notna(row[cols[2]]) else ""
                                        
                                    if item["nama"].strip():
                                        mapped_data.append(item)
                                        
                                st.session_state.parsed_labels = mapped_data
                                st.success(f"Berhasil memuat {len(mapped_data)} stiker dari file Excel!")
                                st.rerun()
                            else:
                                st.warning("File Excel kosong.")
                        except Exception as e:
                            st.error(f"Gagal membaca file Excel: {e}")
            else:
                # Spacer to balance card height when no file is uploaded
                st.write("")
                st.write("")
                st.write("")

    st.markdown("---")

    # Step 2: Validation & Editing (Full Width)
    st.markdown('### <span class="step-badge">2</span> Validasi & Edit Data', unsafe_allow_html=True)
    if not st.session_state.parsed_labels:
        st.info("Silakan masukkan data teks WhatsApp atau unggah berkas Excel pada Tahap 1 di atas terlebih dahulu.")
    else:
        st.info("Anda dapat menambah, menghapus, atau mengedit baris stiker stiker pada tabel interaktif di bawah secara langsung.")
        
        # Load into DataFrame for st.data_editor
        df = pd.DataFrame(st.session_state.parsed_labels)
        for col in ["nama", "alamat", "detail"]:
            if col not in df.columns:
                df[col] = ""
        
        if single_line_mode:
            df = df[["nama"]]
            col_config = {
                "nama": st.column_config.TextColumn("Nama Label / Parfum", required=True)
            }
        else:
            df = df[["nama", "alamat", "detail"]]
            col_config = {
                "nama": st.column_config.TextColumn("Nama Penerima", required=True),
                "alamat": st.column_config.TextColumn("Alamat Lengkap"),
                "detail": st.column_config.TextColumn("Detail Lain (No. HP/Kota)")
            }
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=col_config
        )
        
        # Save back to session state
        new_labels = edited_df.to_dict(orient="records")
        if single_line_mode:
            for item in new_labels:
                item["alamat"] = ""
                item["detail"] = ""
        st.session_state.parsed_labels = new_labels

    st.markdown("---")

    # Step 3: PDF Preview & Download (Full Width)
    st.markdown('### <span class="step-badge">3</span> Preview & Cetak PDF', unsafe_allow_html=True)
    if not st.session_state.parsed_labels:
        st.info("Silakan selesaikan Tahap 1 & 2 di atas untuk mengaktifkan pratinjau cetak PDF.")
    elif not template_type:
        st.warning("Silakan pilih template label terlebih dahulu pada pengaturan di bilah samping kiri.")
    else:
        # Side-by-side action buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            generate_btn = st.button("🔄 Render Ulang PDF Preview", use_container_width=True)
        
        if generate_btn or "pdf_cache" not in st.session_state:
            with st.spinner("Sedang merender berkas PDF presisi..."):
                try:
                    payload = {
                        "labels": st.session_state.parsed_labels,
                        "template_type": template_type,
                        "show_borders": show_borders,
                        "font_size_name": font_size_name,
                        "font_size_address": font_size_address,
                        "font_size_detail": font_size_detail,
                        "single_line_mode": single_line_mode,
                        "font_family": font_family,
                        "font_bold": font_bold,
                        "font_italic": font_italic,
                        "font_underline": font_underline
                    }
                    res = requests.post(f"{API_BASE_URL}/api/generate-pdf", json=payload)
                    
                    if res.status_code == 200:
                        st.session_state.pdf_cache = res.content
                    else:
                        st.error(f"Gagal generate PDF: {res.text}")
                except Exception as e:
                    st.error(f"Terjadi kesalahan koneksi API PDF: {str(e)}")
        
        if "pdf_cache" in st.session_state:
            with col_btn2:
                sw = selected_config.get("sheet_width", 210.0)
                sh = selected_config.get("sheet_height", 297.0)
                st.download_button(
                    label=f"📥 Unduh PDF Siap Cetak ({int(sw/10)} x {int(sh/10)} cm)",
                    data=st.session_state.pdf_cache,
                    file_name=f"labels_{template_type}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            st.markdown("**Pratinjau Hasil Cetak:**")
            display_pdf(st.session_state.pdf_cache)


# ================= TAB 2: KELOLA TEMPLATE =================
with tab_manage:
    st.markdown("### 🛠️ Pengaturan & Manajemen Template")
    st.write("Tambahkan, edit, atau hapus template stiker label kustom sesuai kebutuhan ukuran kertas dan label.")

    # 1. Display Existing Templates Table
    if active_templates:
        st.markdown("#### Daftar Template Tersimpan")
        df_templates = pd.DataFrame.from_dict(active_templates, orient="index")
        # Rename index to ID
        df_templates.index.name = "Template ID"
        st.dataframe(df_templates, use_container_width=True)
    else:
        st.info("Belum ada template yang tersimpan.")

    st.markdown("---")

    col_add, col_edit_del = st.columns(2)

    # 2. Add New Template Form
    with col_add:
        st.markdown("#### ➕ Tambah Template Baru")
        with st.form("add_template_form", clear_on_submit=True):
            new_id = st.text_input("Template ID (Angka unik, e.g. 103, 121):", placeholder="e.g. 103").strip()
            new_name = st.text_input("Nama Template Label:", placeholder="e.g. Label 103 (32 x 64 mm)")
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                label_w = st.number_input("Lebar Label (mm):", min_value=1.0, value=32.0, step=0.1)
                label_h = st.number_input("Tinggi Label (mm):", min_value=1.0, value=64.0, step=0.1)
                h_pitch = st.number_input("Horizontal Pitch (mm):", min_value=1.0, value=66.0, step=0.1, help="Lebar stiker + jarak kolom stiker")
                v_pitch = st.number_input("Vertical Pitch (mm):", min_value=1.0, value=34.0, step=0.1, help="Tinggi stiker + jarak baris stiker")
            with f_col2:
                num_across = st.number_input("Number Across (Jumlah kolom):", min_value=1, value=3, step=1)
                num_down = st.number_input("Number Down (Jumlah baris):", min_value=1, value=4, step=1)
                t_margin = st.number_input("Top Margin (mm):", min_value=0.0, value=10.0, step=0.1)
                s_margin = st.number_input("Side Margin (mm):", min_value=0.0, value=15.0, step=0.1)
                sheet_w = st.number_input("Lebar Kertas (mm):", min_value=10.0, value=210.0, step=1.0)
                sheet_h = st.number_input("Tinggi Kertas (mm):", min_value=10.0, value=170.0, step=1.0)
                
            submit_add = st.form_submit_button("Simpan Template Baru", use_container_width=True)
            
            if submit_add:
                if not new_id or not new_name:
                    st.error("Template ID dan Nama harus diisi.")
                elif new_id in active_templates:
                    st.error(f"Template ID '{new_id}' sudah terdaftar.")
                elif h_pitch < label_w or v_pitch < label_h:
                    st.error("Horizontal/Vertical Pitch tidak boleh lebih kecil dari Lebar/Tinggi Label.")
                else:
                    payload = {
                        "name": new_name,
                        "label_height": label_h,
                        "label_width": label_w,
                        "vertical_pitch": v_pitch,
                        "horizontal_pitch": h_pitch,
                        "number_across": num_across,
                        "number_down": num_down,
                        "top_margin": t_margin,
                        "side_margin": s_margin,
                        "sheet_width": sheet_w,
                        "sheet_height": sheet_h
                    }
                    try:
                        res = requests.post(f"{API_BASE_URL}/api/templates/{new_id}", json=payload)
                        if res.status_code == 200:
                            st.success(f"Berhasil menyimpan template baru '{new_name}'!")
                            st.rerun()
                        else:
                            st.error(f"Gagal menyimpan ke API: {res.text}")
                    except Exception as e:
                        st.error(f"Error koneksi API: {e}")

    # 3. Edit & Delete Existing Templates Form
    with col_edit_del:
        st.markdown("#### ✏️ Ubah / 🗑️ Hapus Template")
        if not active_templates:
            st.info("Tambahkan template terlebih dahulu untuk membuka menu edit/hapus.")
        else:
            select_id = st.selectbox(
                "Pilih ID Template yang Ingin Dikelola:",
                options=list(active_templates.keys()),
                format_func=lambda x: f"{x} - {active_templates[x].get('name', '')}"
            )
            
            selected_t = active_templates[select_id]
            
            # Form fields prefilled with selected config
            with st.form("edit_template_form"):
                edit_name = st.text_input("Nama Template Label:", value=selected_t.get("name", ""))
                
                fe_col1, fe_col2 = st.columns(2)
                with fe_col1:
                    edit_w = st.number_input("Lebar Label (mm):", min_value=1.0, value=float(selected_t.get("label_width", 32.0)), step=0.1)
                    edit_h = st.number_input("Tinggi Label (mm):", min_value=1.0, value=float(selected_t.get("label_height", 64.0)), step=0.1)
                    edit_hp = st.number_input("Horizontal Pitch (mm):", min_value=1.0, value=float(selected_t.get("horizontal_pitch", 66.0)), step=0.1)
                    edit_vp = st.number_input("Vertical Pitch (mm):", min_value=1.0, value=float(selected_t.get("vertical_pitch", 34.0)), step=0.1)
                with fe_col2:
                    edit_across = st.number_input("Number Across (Jumlah kolom):", min_value=1, value=int(selected_t.get("number_across", 3)), step=1)
                    edit_down = st.number_input("Number Down (Jumlah baris):", min_value=1, value=int(selected_t.get("number_down", 4)), step=1)
                    edit_tm = st.number_input("Top Margin (mm):", min_value=0.0, value=float(selected_t.get("top_margin", 10.0)), step=0.1)
                    edit_sm = st.number_input("Side Margin (mm):", min_value=0.0, value=float(selected_t.get("side_margin", 15.0)), step=0.1)
                    edit_sw = st.number_input("Lebar Kertas (mm):", min_value=10.0, value=float(selected_t.get("sheet_width", 210.0)), step=1.0)
                    edit_sh = st.number_input("Tinggi Kertas (mm):", min_value=10.0, value=float(selected_t.get("sheet_height", 170.0)), step=1.0)
                    
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit_edit = st.form_submit_button("Simpan Perubahan", use_container_width=True)
                with col_btn2:
                    submit_del = st.form_submit_button("🗑️ Hapus Template", use_container_width=True)
                
                if submit_edit:
                    if not edit_name:
                        st.error("Nama Template harus diisi.")
                    elif edit_hp < edit_w or edit_vp < edit_h:
                        st.error("Horizontal/Vertical Pitch tidak boleh lebih kecil dari Lebar/Tinggi Label.")
                    else:
                        payload = {
                            "name": edit_name,
                            "label_height": edit_h,
                            "label_width": edit_w,
                            "vertical_pitch": edit_vp,
                            "horizontal_pitch": edit_hp,
                            "number_across": edit_across,
                            "number_down": edit_down,
                            "top_margin": edit_tm,
                            "side_margin": edit_sm,
                            "sheet_width": edit_sw,
                            "sheet_height": edit_sh
                        }
                        try:
                            res = requests.put(f"{API_BASE_URL}/api/templates/{select_id}", json=payload)
                            if res.status_code == 200:
                                st.success(f"Berhasil memperbarui template '{edit_name}'!")
                                st.rerun()
                            else:
                                st.error(f"Gagal memperbarui template: {res.text}")
                        except Exception as e:
                            st.error(f"Error koneksi API: {e}")
                            
                if submit_del:
                    try:
                        res = requests.delete(f"{API_BASE_URL}/api/templates/{select_id}")
                        if res.status_code == 200:
                            st.success(f"Template '{edit_name}' berhasil dihapus.")
                            st.rerun()
                        else:
                            st.error(f"Gagal menghapus template: {res.text}")
                    except Exception as e:
                        st.error(f"Error koneksi API: {e}")
