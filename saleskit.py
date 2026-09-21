import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")
st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

# 1. Tarik Data dari Excel Otomatis!
try:
    # Membaca file Excel
    df = pd.read_excel("data_spek.xlsx")
    
    # 2. Area Pencarian Kasir / SA
    st.subheader("🔍 Skenario Pelanggan")
    
    # FITUR BARU: Kolom Ketik Khusus HP (Memaksa keyboard muncul)
    kata_kunci = st.text_input("Ketik Merk/Tipe HP yang dicari customer:", placeholder="Misal: Poco X8")
    
    # Ambil daftar unik dari Excel
    pilihan_unik = df["Lawan_Dicari"].unique().tolist()
    
    # Mesin Penyaring Otomatis berdasarkan ketikan
    if kata_kunci:
        pilihan_tersaring = [hp for hp in pilihan_unik if kata_kunci.lower() in str(hp).lower()]
    else:
        pilihan_tersaring = pilihan_unik
        
    # Dropdown yang datanya sudah disaring oleh kolom ketik di atas
    pilihan_customer = st.selectbox(
        "👇 Pilih Hasil Pencarian:", 
        ["-- Apa barang yang kosong? --"] + pilihan_tersaring
    )

    # 3. Logika Menampilkan MULTIPLE Senjata Rahasia
    if pilihan_customer != "-- Apa barang yang kosong? --":
        # Tarik SEMUA data yang sesuai dengan pilihan
        hasil_semua = df[df["Lawan_Dicari"] == pilihan_customer]
        
        st.success(f"🔥 Ditemukan **{len(hasil_semua)} Opsi Switch Selling** untuk menggantikan {pilihan_customer}!")
        
        # Pakai TABS supaya tampilannya rapi dan interaktif
        nama_target = hasil_semua["Target_Jualan"].tolist()
        tabs = st.tabs(nama_target)
        
        # Looping untuk mengisi masing-masing tab dengan datanya
        for index, tab in enumerate(tabs):
            with tab:
                baris_data = hasil_semua.iloc[index]
                
                st.markdown(f"### 🎯 Opsi ke-{index+1}: Beralih ke {baris_data['Target_Jualan']}")
                
                # Bagi layar jadi 2 kolom di dalam tab
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📊 Spek Kunci {baris_data['Target_Jualan']}")
                    st.text(baris_data['Spek_Kunci'])
                    
                with col2:
                    st.warning("💬 Angle Jualan 'Rahasia Dapur'")
                    st.write(f"*{baris_data['Script_Sales']}*")
            
except FileNotFoundError:
    st.error("⚠️ File 'data_spek.xlsx' tidak ditemukan! Pastikan file Excel sudah di-save di folder yang sama.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")