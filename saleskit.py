import streamlit as st
import pandas as pd

# Konfigurasi Halaman & Memaksa Tema Gelap
st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

# CSS Dark Mode Absolut (Tanpa efek yang membuat tampilan berantakan)
st.markdown("""
<style>
.stApp {
    background-color: #0E1117 !important; 
    color: #FAFAFA !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #FAFAFA !important;
}
.stTextInput > div > div > input {
    color: white !important;
    background-color: #262730 !important;
    border: 1px solid #4B4B4B !important;
}
[data-testid="stAlert"] {
    background-color: #262730 !important;
    border: 1px solid #4B4B4B !important;
    color: white !important;
}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

try:
    df = pd.read_excel("data_spek.xlsx")
    
    st.subheader("🔍 Spotlight Search")
    
    # STEP 1: Keyboard HP langsung muncul saat disentuh
    kata_kunci = st.text_input(
        "1. Ketik Merk/Tipe HP (Contoh: Samsung, Poco):", 
        placeholder="Ketik lalu tekan Enter..."
    )

    if kata_kunci:
        # Cari daftar HP unik yang berhubungan dengan ketikan
        hp_cocok = df[df["Lawan_Dicari"].str.contains(kata_kunci, case=False, na=False)]["Lawan_Dicari"].unique().tolist()
        
        # STEP 2: Filter Pencegah "Banjir Hasil"
        if len(hp_cocok) > 1:
            st.info("👇 Ditemukan beberapa tipe HP. Pilih tipe spesifiknya di bawah ini:")
            pilihan_final = st.selectbox("Pilih Tipe HP:", hp_cocok)
        elif len(hp_cocok) == 1:
            pilihan_final = hp_cocok[0] # Otomatis terpilih jika hanya 1 yang cocok
        else:
            pilihan_final = None
            st.error(f"❌ HP '{kata_kunci}' tidak ditemukan. Coba cek ejaannya.")
            
        # STEP 3: Tampilkan Hasil Akhir
        if pilihan_final:
            hasil_semua = df[df["Lawan_Dicari"] == pilihan_final]
            st.success(f"🔥 Ditemukan rekomendasi untuk {pilihan_final}!")
            
            for index, baris in hasil_semua.iterrows():
                st.markdown(f"### 🎯 Alternatif: {baris['Target_Jualan']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info("📊 Spek Kunci")
                    st.text(baris['Spek_Kunci'])
                with col2:
                    st.warning("💬 Angle Jualan")
                    st.write(f"*{baris['Script_Sales']}*")
                st.markdown("---")
            
except FileNotFoundError:
    st.error("⚠️ File 'data_spek.xlsx' tidak ditemukan! Pastikan file Excel sudah di-save.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")
