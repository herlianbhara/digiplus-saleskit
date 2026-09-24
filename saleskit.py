import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman & Memaksa Tema Gelap (Dark Mode Override)
st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

# CSS untuk memaksa warna gelap (mengabaikan pengaturan perangkat pengguna)
st.markdown("""
<style>
/* Memaksa background seluruh aplikasi menjadi abu-abu sangat gelap (Dark Mode Apple) */
.stApp {
    background-color: #0E1117 !important; 
    color: #FAFAFA !important;
}

/* Memastikan semua teks dasar berwarna putih keabuan */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #FAFAFA !important;
}

/* Styling kolom input agar menyatu dengan dark mode */
.stTextInput > div > div > input {
    color: white !important;
    background-color: #262730 !important;
    border: 1px solid #4B4B4B !important;
}

/* Memperbaiki warna teks peringatan agar kontras */
[data-testid="stAlert"] {
    background-color: #262730 !important;
    border: 1px solid #4B4B4B !important;
    color: white !important;
}

/* Menyembunyikan menu bawaan streamlit di pojok kanan atas (opsional tapi bikin rapi) */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

# Tarik Data dari Excel Otomatis
try:
    df = pd.read_excel("data_spek.xlsx")
    
    st.subheader("🔍 Spotlight Search")
    
    # KUNCI UTAMA KEYBOARD HP: Menggunakan st.text_input MURNI. 
    # Sekali sentuh di HP, keyboard langsung keluar!
    kata_kunci = st.text_input(
        "Ketik Merk/Tipe HP (Contoh: Poco X8, S25, dll):", 
        placeholder="Ketik nama HP di sini lalu tekan Enter..."
    )

    # Logika Pencarian Pintar (Tidak sensitif huruf besar/kecil)
    if kata_kunci:
        # Mencari baris di Excel yang kolom 'Lawan_Dicari' nya mengandung kata kunci
        hasil_semua = df[df["Lawan_Dicari"].str.contains(kata_kunci, case=False, na=False)]
        
        if not hasil_semua.empty:
            st.success(f"🔥 Ditemukan **{len(hasil_semua)} Rekomendasi** dari database!")
            
            # Looping untuk memunculkan semua hasil yang cocok ke bawah (sederhana & rapi)
            for index, baris in hasil_semua.iterrows():
                st.markdown(f"### 🎯 Alternatif: {baris['Target_Jualan']} (Pengganti {baris['Lawan_Dicari']})")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📊 Spek Kunci {baris['Target_Jualan']}")
                    st.text(baris['Spek_Kunci'])
                    
                with col2:
                    st.warning("💬 Angle Jualan 'Rahasia Dapur'")
                    st.write(f"*{baris['Script_Sales']}*")
                
                st.markdown("---") # Garis pembatas antar hasil
                
        else:
            st.error(f"❌ HP '{kata_kunci}' tidak ditemukan di database. Coba ketik mereknya saja.")
            
except FileNotFoundError:
    st.error("⚠️ File 'data_spek.xlsx' tidak ditemukan! Pastikan file Excel sudah di-save di folder yang sama.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")
