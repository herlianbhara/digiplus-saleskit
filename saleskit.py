import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman & Memaksa Tema Gelap
st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

# CSS Dark Mode Absolut
st.markdown("""

""", unsafe_allow_html=True)

st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

try:
    df = pd.read_excel("data_spek.xlsx")
    
    st.subheader("🔍 HP apa yang sedang kosong?")
    st.markdown("*biar aku bantu cariin penggantinya lengkap dengan cara jualan ☺️*")
    
    pilihan_unik = df["Lawan_Dicari"].unique().tolist()
    
    pilihan_customer = st.selectbox(
        "Pilih HP yang sedang kosong:", 
        options=pilihan_unik,
        index=None,
        placeholder="Pilih HP yang sedang kosong..."
    )

    if pilihan_customer:
        hasil_semua = df[df["Lawan_Dicari"] == pilihan_customer]
        st.success(f"🔥 Ditemukan **{len(hasil_semua)} rekomendasi** pengganti untuk {pilihan_customer}!")
        
        # --- KEMBALI MENGGUNAKAN TABS YANG ELEGAN DAN RAPI ---
        nama_target = hasil_semua["Target_Jualan"].tolist()
        tabs = st.tabs(nama_target)
        
        for index, tab in enumerate(tabs):
            with tab:
                baris_data = hasil_semua.iloc[index]
                
                st.markdown(f"### 🎯 Alternatif: Beralih ke {baris_data['Target_Jualan']}")
                
                # Bagi layar jadi 2 kolom di dalam tab
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📊 Spek Kunci {baris_data['Target_Jualan']}")
                    st.text(baris_data['Spek_Kunci'])
                    
                with col2:
                    st.warning("💬 Angle Jualan 'Rahasia Dapur'")
                    st.write(f"*{baris_data['Script_Sales']}*")
            
except FileNotFoundError:
    st.error("⚠️ File 'data_spek.xlsx' tidak ditemukan! Pastikan file Excel sudah di-save.")
except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")
