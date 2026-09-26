import streamlit as st
import pandas as pd
from streamlit_searchbox import st_searchbox

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
# ✨ Gabungin Brand + Model jadi Nama_Lengkap
# ============================================
df["Nama_Lengkap"] = df["Brand"].astype(str) + " " + df["Model"].astype(str)

# ============================================
# 2. LOGIC PENCARIAN ALTERNATIF
# ============================================
def cari_alternatif(hp_kosong, df, max_selisih_harga=2500000, top_n=5):
    """
    Cari HP alternatif berdasarkan:
    - Selisih harga maksimal
    - Skor kemiripan (harga + tier)
    """
    data_kosong = df[df["Nama_Lengkap"] == hp_kosong].iloc[0]
    harga_acuan = data_kosong["Harga"]
    tier_acuan = data_kosong["Tier"]
    
    kandidat = df[df["Nama_Lengkap"] != hp_kosong].copy()
    kandidat["Selisih_Harga"] = abs(kandidat["Harga"] - harga_acuan)
    kandidat = kandidat[kandidat["Selisih_Harga"] <= max_selisih_harga]
    
    # Hitung skor kecocokan
    def hitung_skor(row):
        skor = 0
        skor += max(0, 60 - (row["Selisih_Harga"] / max_selisih_harga * 60))
        if row["Tier"] == tier_acuan:
            skor += 40
        elif abs(row["Tier"] == tier_acuan):
            skor += 15
        if row["Brand"] == data_kosong["Brand"]:
            skor += 10
        return skor
    
    kandidat["Skor"] = kandidat.apply(hitung_skor, axis=1)
    kandidat = kandidat.sort_values("Skor", ascending=False).head(top_n)
    
    return kandidat, data_kosong

# ============================================
# 3. LOGIC GENERATE IDE PROBING
# ============================================
def generate_ide_probing(data_kosong, data_alternatif):
    """
    Generate ide probing + kalimat penawaran berdasarkan perbandingan
    """
    nama_kosong = data_kosong["Nama_Lengkap"]
    nama_alt = data_alternatif["Nama_Lengkap"]
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
    
    # Pembuka bernuansa PROBING (menggali kebutuhan dulu)
    if brand_alt == "iPhone":
        pembuka = f"Kak, {nama_kosong} lagi kosong nih. Boleh saya tahu, Kakak biasanya paling sering pakai HP buat apa? Kalau buat foto dan konten, kita ada {nama_alt} yang sekelas dan nggak kalah keren."
    elif brand_alt == "Samsung":
        pembuka = f"Kak, {nama_kosong} stoknya habis. Sebelum saya kasih rekomendasi, boleh tahu Kakak lebih prioritasin kamera, baterai, atau performa? Kalau soal itu, kita ada {nama_alt} yang bisa jadi pertimbangan."
    else:
        pembuka = f"Kak, {nama_kosong} lagi kosong. Boleh saya tanya dulu, Kakak biasanya cari HP yang fokusnya ke mana—kamera, gaming, atau baterai awet? Kalau boleh saya saranin, {nama_alt} ini menarik buat dipertimbangkan."
    
    # Penawaran keunggulan
    penawaran = f"{nama_alt} ini punya {kelebihan_teks}."
    
    # Closing berdasarkan harga
    selisih = data_alternatif["Harga"] - data_kosong["Harga"]
    if selisih < -500000:
        closing = f"Harganya malah lebih murah {abs(selisih):,.0f} rupiah, Kak. Jadi lebih hemat!"
    elif selisih > 500000:
        closing = f"Selisihnya cuma {selisih:,.0f} rupiah, Kak, tapi dapet upgrade yang worth it."
    else:
        closing = "Harganya mirip banget, Kak, tapi fiturnya bisa jadi lebih cocok buat Kakak."
    
    ide_probing = f"{pembuka} {penawaran} {closing} Mau saya tunjukin langsung?"
    
    return ide_probing.replace("  ", " ").strip()

# ============================================
# 4. TAMPILAN UTAMA
# ============================================
st.subheader("🔍 HP apa yang sedang kosong?")
st.markdown("*Biar aku bantu cariin penggantinya lengkap dengan cara jualan ☺️*")

pilihan_unik = df["Nama_Lengkap"].unique().tolist()

# ✨ Fungsi search untuk st_searchbox
def search_hp(searchterm: str):
    if not searchterm:
        return pilihan_unik[:20]  # Tampilkan 20 pertama kalau kosong
    return [
        hp for hp in pilihan_unik 
        if searchterm.lower() in hp.lower()
    ][:20]  # Maksimal 20 saran

# ✨ Search box dengan keyboard + autocomplete dropdown
pilihan_customer = st_searchbox(
    search_hp,
    label="🔎 Cari HP yang sedang kosong:",
    placeholder="Ketik nama HP... (contoh: Galaxy S25, iPhone 17)",
    key="search_hp"
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
        
        nama_target = kandidat["Nama_Lengkap"].tolist()
        tabs = st.tabs([f"📱 {nama}" for nama in nama_target])
        
        for index, tab in enumerate(tabs):
            with tab:
                baris_data = kandidat.iloc[index]
                
                st.markdown(f"### 🎯 Alternatif: {baris_data['Nama_Lengkap']}")
                
                # Info harga & selisih
                selisih = baris_data["Harga"] - data_kosong["Harga"]
                tanda = "+" if selisih > 0 else ""
                st.caption(f"💰 Harga: **Rp {baris_data['Harga']:,.0f}** ({tanda}Rp {selisih:,.0f} dari {pilihan_customer}) | 🎯 Skor Kecocokan: **{baris_data['Skor']:.0f}/100**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📊 Kelebihan {baris_data['Nama_Lengkap']}")
                    for i in range(1, 4):
                        kolom = f"Kelebihan_{i}"
                        if kolom in baris_data and pd.notna(baris_data[kolom]):
                            st.write(f"✅ {baris_data[kolom]}")
                
                with col2:
                    st.warning("💬 Ide Probing")
                    ide_probing = generate_ide_probing(data_kosong, baris_data)
                    st.write(f"*{ide_probing}*")

else:
    st.info("👆 Ketik nama HP di kolom pencarian untuk mulai.")
