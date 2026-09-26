import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman & Memaksa Tema Gelap
st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

# CSS Dark Mode Absolut (Rapi dan Bersih)
st.markdown("""
<style>
.stApp {
    background-color: #0E1117 !important; 
    color: #FAFAFA !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #FAFAFA !important;
}
/* Mempercantik kotak Dropdown agar menyatu dengan Dark Mode */
div[data-baseweb="select"] > div {
    background-color: #262730 !important;
    border: 1px solid #4B4B4B !important;
    color: white !important;
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
    
    # PERUBAHAN COPYWRITING SESUAI IDE BRILIANMU
    st.subheader("🔍 HP apa yang sedang kosong?")
    st.markdown("*biar aku bantu cariin penggantinya lengkap dengan cara jualan ☺️*")
    
    pilihan_unik = df["Lawan_Dicari"].unique().tolist()
    
    pilihan_customer = st.selectbox(
        "Pilih HP yang sedang kosong:", 
        options=pilihan_unik,
        index=None,
        placeholder="Pilih HP yang sedang kosong..."
    )

    # Menampilkan Hasil secara langsung setelah dipilih dari Hover
    if pilihan_customer:
        hasil_semua = df[df["Lawan_Dicari"] == pilihan_customer]
        st.success(f"🔥 Ditemukan rekomendasi untuk {pilihan_customer}!")
        
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
