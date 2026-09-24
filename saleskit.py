import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman (Harus paling atas)
st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

# --- 2. SUNTIKAN CSS SUPER GLASSMORPHISM (iOS STYLE) ---
st.markdown("""
<style>
/* Latar Belakang Utama (Wallpaper iOS Dark Fluid) */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=2564&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Bikin header Streamlit transparan agar wallpaper tidak tertutup */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* Efek Kaca pada kotak input, alert, tab, dan kontainer radio button */
[data-testid="stAlert"], 
div[data-baseweb="input"] > div,
div[data-testid="stVerticalBlock"] > div > div,
div[role="radiogroup"] {
    background-color: rgba(30, 30, 30, 0.45) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    color: white !important;
}

/* Penyesuaian warna teks agar tajam dan elegan di atas kaca */
h1, h2, h3, p, label, div[data-testid="stMarkdownContainer"] p {
    color: white !important;
    text-shadow: 0px 2px 4px rgba(0,0,0,0.8);
}
</style>
""", unsafe_allow_html=True)

# --- 3. KONTEN APLIKASI ---
st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

# Tarik Data Excel
try:
    df = pd.read_excel("data_spek.xlsx")
    
    st.subheader("🔍 Spotlight Search")
    
    # STEP 1: Kolom Teks (Memancing keyboard HP muncul)
    kata_kunci = st.text_input("1. Ketik Merk/Tipe HP (Contoh: sam / poco):", placeholder="Ketik di sini...")

    # Mesin Pencari Real-Time
    if kata_kunci:
        # Cari daftar HP unik dari Excel yang mirip dengan ketikan
        hp_cocok = df[df["Lawan_Dicari"].str.contains(kata_kunci, case=False, na=False)]["Lawan_Dicari"].unique().tolist()
        
        # STEP 2: Filter Pemilihan
        if len(hp_cocok) > 1:
            st.info("👇 Pilih tipe HP spesifik di bawah ini:")
            pilihan_final = st.radio("Daftar HP:", hp_cocok)
        elif len(hp_cocok) == 1:
            pilihan_final = hp_cocok[0] # Otomatis terpilih jika hasil pencarian hanya 1
        else:
            pilihan_final = None
            st.error("❌ Produk tidak ditemukan. Pastikan ejaan benar.")
            
        # STEP 3: Tampilkan Hasil (Setelah 1 HP spesifik terpilih)
        if pilihan_final:
            hasil_semua = df[df["Lawan_Dicari"] == pilihan_final]
            
            st.success(f"🔥 Ditemukan **{len(hasil_semua)} Opsi Switch Selling** untuk {pilihan_final}!")
            
            # Gunakan tabs untuk opsi target
            nama_target = hasil_semua["Target_Jualan"].tolist()
            tabs = st.tabs(nama_target)
            
            for index, tab in enumerate(tabs):
                with tab:
                    baris_data = hasil_semua.iloc[index]
                    st.markdown(f"### 🎯 Beralih ke {baris_data['Target_Jualan']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info("📊 Spek Kunci")
                        st.text(baris_data['Spek_Kunci'])
                    with col2:
                        st.warning("💬 Angle Jualan")
                        st.write(f"*{baris_data['Script_Sales']}*")
                        
except FileNotFoundError:
    st.error("⚠️ File 'data_spek.xlsx' tidak ditemukan! Pastikan file Excel sudah di-save di folder yang sama.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")
