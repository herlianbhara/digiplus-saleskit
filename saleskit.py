import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman (Harus paling atas)
st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

# --- 2. SUNTIKAN CSS SUPER GLASSMORPHISM (iOS STYLE) ---
st.markdown("""

""", unsafe_allow_html=True)

# --- 3. KONTEN APLIKASI ---
st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

# Tarik Data Excel
try:
    df = pd.read_excel("data_spek.xlsx")
    
    st.subheader("🔍 Spotlight Search")
    
    # SOLUSI KEYBOARD HP: 1 Kolom Teks Murni (Langsung panggil keyboard)
    kata_kunci = st.text_input("Ketik Merk/Tipe HP (Contoh: Poco):", placeholder="Ketik di sini lalu tekan Enter/Selesai...")

    # Mesin Pencari Real-Time
    if kata_kunci:
        # Mencari data yang mirip dengan ketikan (tidak sensitif huruf besar/kecil)
        hasil_semua = df[df["Lawan_Dicari"].str.contains(kata_kunci, case=False, na=False)]
        
        if not hasil_semua.empty:
            st.success(f"🔥 Ditemukan **{len(hasil_semua)} Opsi Switch Selling**!")
            
            # Gunakan tabs untuk opsi
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
        else:
            st.error("❌ Produk tidak ditemukan. Pastikan ejaan benar.")
            
except FileNotFoundError:
    st.error("⚠️ File 'data_spek.xlsx' tidak ditemukan! Pastikan file Excel sudah di-save di folder yang sama.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")
