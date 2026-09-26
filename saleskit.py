import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

# ============================================
# 1. LOAD DATA
# ============================================
@st.cache_data
def load_data():
    return pd.read_excel("data_hp.xlsx")

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ File 'data_hp.xlsx' tidak ditemukan!")
    st.stop()

# ============================================
# 2. LOGIC PENCARIAN ALTERNATIF
# ============================================
def cari_alternatif(hp_kosong, df, max_selisih_harga=2500000, top_n=5):
    """
    Cari HP alternatif berdasarkan:
    - Selisih harga maksimal
    - Skor kemiripan (harga + tier)
    """
    data_kosong = df[df["Model"] == hp_kosong].iloc[0]
    harga_acuan = data_kosong["Harga"]
    tier_acuan = data_kosong["Tier"]
    
    # Filter: HP lain (bukan dirinya sendiri) dengan selisih harga masuk akal
    kandidat = df[df["Model"] != hp_kosong].copy()
    kandidat["Selisih_Harga"] = abs(kandidat["Harga"] - harga_acuan)
    kandidat = kandidat[kandidat["Selisih_Harga"] <= max_selisih_harga]
    
    # Hitung skor kecocokan
    def hitung_skor(row):
        skor = 0
        # Skor harga: semakin dekat, semakin tinggi (max 60 poin)
        skor += max(0, 60 - (row["Selisih_Harga"] / max_selisih_harga * 60))
        # Skor tier: sama tier dapat 40 poin
        if row["Tier"] == tier_acuan:
            skor += 40
        elif abs(row["Tier"] == tier_acuan):
            skor += 15
        # Bonus kalau brand sama (orang biasanya loyal brand)
        if row["Brand"] == data_kosong["Brand"]:
            skor += 10
        return skor
    
    kandidat["Skor"] = kandidat.apply(hitung_skor, axis=1)
    kandidat = kandidat.sort_values("Skor", ascending=False).head(top_n)
    
    return kandidat, data_kosong

# ============================================
# 3. LOGIC GENERATE SCRIPT OTOMATIS
# ============================================
def generate_script(data_kosong, data_alternatif):
    """
    Generate script jualan otomatis berdasarkan perbandingan
    """
    nama_kosong = data_kosong["Model"]
    nama_alt = data_alternatif["Model"]
    brand_alt = data_alternatif["Brand"]
    
    # Kumpulkan kelebihan
    kelebihan = []
    for i in range(1, 4):
        kolom = f"Kelebihan_{i}"
        if kolom in data_alternatif and pd.notna(data_alternatif[kolom]):
            kelebihan.append(data_alternatif[kolom])
    
    # Format kelebihan jadi kalimat
    if len(kelebihan) >= 2:
        kelebihan_teks = f"{kelebihan[0]} dan {kelebihan[1]}"
    elif len(kelebihan) == 1:
        kelebihan_teks = kelebihan[0]
    else:
        kelebihan_teks = "spesifikasi yang nggak kalah bagus"
    
    # Pilih pembuka berdasarkan brand
    if brand_alt == "iPhone":
        pembuka = f"Kak, kalau lagi cari yang sekelas iPhone, kita ada {nama_alt} nih."
    elif brand_alt == "Samsung":
        pembuka = f"Kak, {nama_kosong} lagi kosong, tapi kita ada {nama_alt} yang nggak kalah keren."
    else:
        pembuka = f"Kak, {nama_kosong} stoknya habis, tapi saya punya rekomendasi menarik: {nama_alt}."
    
    # Closing berdasarkan harga
    selisih = data_alternatif["Harga"] - data_kosong["Harga"]
    if selisih < -500000:
        closing = f"Harganya malah lebih murah {abs(selisih):,.0f} rupiah, Kak. Jadi lebih hemat!"
    elif selisih > 500000:
        closing = f"Selisihnya cuma {selisih:,.0f} rupiah, Kak, tapi dapet upgrade yang worth it."
    else:
        closing = "Harganya mirip banget, Kak, tapi fiturnya bisa jadi lebih cocok buat Kakak."
    
    script = f"{pembuka} {nama_alt} ini punya {kelebihan_teks}. {closing} Mau saya tunjukin langsung?"
    
    return script.replace("  ", " ").strip()

# ============================================
# 4. TAMPILAN UTAMA
# ============================================
st.subheader("🔍 HP apa yang sedang kosong?")
st.markdown("*Biar aku bantu cariin penggantinya lengkap dengan cara jualan ☺️*")

pilihan_unik = df["Model"].unique().tolist()

pilihan_customer = st.selectbox(
    "Pilih HP yang sedang kosong:", 
    options=pilihan_unik,
    index=None,
    placeholder="Pilih HP yang sedang kosong..."
)

# Slider untuk atur toleransi harga
with st.sidebar:
    st.header("⚙️ Pengaturan")
    max_selisih = st.slider(
        "Toleransi selisih harga (Rp):", 
        min_value=500000, max_value=5000000, 
        value=2500000, step=500000,
        format="Rp %d"
    )
    top_n = st.slider("Jumlah rekomendasi:", 1, 10, 5)

if pilihan_customer:
    kandidat, data_kosong = cari_alternatif(
        pilihan_customer, df, max_selisih, top_n
    )
    
    if len(kandidat) == 0:
        st.warning(f"⚠️ Nggak ada alternatif untuk {pilihan_customer} dalam toleransi harga ini. Coba naikkan toleransi di sidebar.")
    else:
        st.success(f"🔥 Ditemukan **{len(kandidat)} rekomendasi** pengganti untuk {pilihan_customer}!")
        
        # Info produk kosong
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Harga Acuan", f"Rp {data_kosong['Harga']:,.0f}")
        col_b.metric("Tier", data_kosong['Tier'])
        col_c.metric("Brand", data_kosong['Brand'])
        
        st.markdown("---")
        
        # Tabs untuk setiap alternatif
        nama_target = kandidat["Model"].tolist()
        tabs = st.tabs([f"📱 {nama}" for nama in nama_target])
        
        for index, tab in enumerate(tabs):
            with tab:
                baris_data = kandidat.iloc[index]
                
                st.markdown(f"### 🎯 Alternatif: {baris_data['Model']} ({baris_data['Brand']})")
                
                # Info harga & selisih
                selisih = baris_data["Harga"] - data_kosong["Harga"]
                tanda = "+" if selisih > 0 else ""
                st.caption(f"💰 Harga: **Rp {baris_data['Harga']:,.0f}** ({tanda}Rp {selisih:,.0f} dari {pilihan_customer}) | 🎯 Skor Kecocokan: **{baris_data['Skor']:.0f}/100**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📊 Kelebihan {baris_data['Model']}")
                    for i in range(1, 4):
                        kolom = f"Kelebihan_{i}"
                        if kolom in baris_data and pd.notna(baris_data[kolom]):
                            st.write(f"✅ {baris_data[kolom]}")
                
                with col2:
                    st.warning("💬 Script Jualan Otomatis")
                    script = generate_script(data_kosong, baris_data)
                    st.write(f"*{script}*")
                    st.code(script, language=None)

else:
    st.info("👆 Pilih HP yang kosong di atas untuk mulai.")
