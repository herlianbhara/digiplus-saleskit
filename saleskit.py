import streamlit as st
import pandas as pd
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="Digiplus Smart Sales Assistant", layout="wide")

st.title("⚔️ Digiplus Smart Sales Assistant")
st.markdown("**Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!**")
st.markdown("---")

# ============================================
# 1. LOAD DATA - Multi-sheet + auto-refresh
# ============================================
@st.cache_data(ttl=60)
def load_data():
    """
    Baca SEMUA sheet dari Excel.
    Return: (df_toko, df_kompetitor)
    """
    sheets_dict = pd.read_excel("data_hp.xlsx", sheet_name=None)
    
    # ✨ Pisahin sheet Kompetitor dari sheet produk toko
    df_kompetitor = sheets_dict.pop("Kompetitor", pd.DataFrame())
    
    # ✨ Skip sheet yang bukan data produk
    skip_sheets = ["Panduan", "Master", "Notes", "Template", "Sheet1"]
    valid_sheets = {
        name: sheet for name, sheet in sheets_dict.items()
        if name not in skip_sheets
    }
    
    # ✨ Gabungin semua sheet toko
    df_toko = pd.concat(valid_sheets.values(), ignore_index=True)
    df_toko = df_toko.dropna(subset=["Brand", "Model"])
    
    # ✨ Bersihin df_kompetitor (kalau ada)
    if not df_kompetitor.empty:
        df_kompetitor = df_kompetitor.dropna(subset=["Brand", "Model"])
    
    return df_toko, df_kompetitor

try:
    df_toko, df_kompetitor = load_data()
except FileNotFoundError:
    st.error("⚠️ File 'data_hp.xlsx' tidak ditemukan!")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error baca Excel: {e}")
    st.stop()

# ============================================
# ✨ Gabungin Brand + Model dengan cek anti-duplikat
# ============================================
def gabung_nama(row):
    brand = str(row["Brand"]).strip()
    model = str(row["Model"]).strip()
    if model.lower().startswith(brand.lower()):
        return model
    else:
        return f"{brand} {model}"

df_toko["Nama_Lengkap"] = df_toko.apply(gabung_nama, axis=1)

# ✨ Cek apakah kolom Chipset ada
has_chipset_toko = "Chipset" in df_toko.columns

if not df_kompetitor.empty:
    df_kompetitor["Nama_Lengkap"] = df_kompetitor.apply(gabung_nama, axis=1)
    has_chipset_komp = "Chipset" in df_kompetitor.columns
else:
    has_chipset_komp = False

# ============================================
# 2A. LOGIC PENCARIAN ALTERNATIF (Produk Toko Kosong)
# ============================================
def cari_alternatif(hp_kosong, df, max_selisih_harga=2500000, top_n=5):
    """
    Cari alternatif dari produk yang kita jual, ketika produk toko kosong.
    """
    data_kosong = df[df["Nama_Lengkap"] == hp_kosong].iloc[0]
    harga_acuan = data_kosong["Harga"]
    tier_acuan = data_kosong["Tier"]
    
    kandidat = df[df["Nama_Lengkap"] != hp_kosong].copy()
    kandidat["Selisih_Harga"] = abs(kandidat["Harga"] - harga_acuan)
    kandidat = kandidat[kandidat["Selisih_Harga"] <= max_selisih_harga]
    
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
# 2B. LOGIC PENCARIAN ALTERNATIF (Produk Kompetitor)
# ============================================
def cari_alternatif_dari_kompetitor(hp_kompetitor, df_kompetitor, df_toko, 
                                       max_selisih_persen=0.3, top_n=3):
    """
    Cari produk dari toko kita yang match dengan produk kompetitor
    berdasarkan: Harga (±30%), Tier, dan Chipset.
    """
    data_komp = df_kompetitor[df_kompetitor["Nama_Lengkap"] == hp_kompetitor].iloc[0]
    harga_komp = data_komp["Harga"]
    tier_komp = str(data_komp.get("Tier", "")).strip()
    chipset_komp = str(data_komp.get("Chipset", "")).strip().lower()
    
    kandidat = df_toko.copy()
    
    # ✨ Filter 1: Harga dalam range ±30%
    max_selisih = harga_komp * max_selisih_persen
    kandidat["Selisih_Harga"] = abs(kandidat["Harga"] - harga_komp)
    kandidat = kandidat[kandidat["Selisih_Harga"] <= max_selisih]
    
    # ✨ Skor kecocokan
    def hitung_skor(row):
        skor = 0
        
        # 1. Skor Harga (max 40 poin)
        if max_selisih > 0:
            skor += max(0, 40 - (row["Selisih_Harga"] / max_selisih * 40))
        
        # 2. Skor Tier (max 30 poin)
        tier_row = str(row.get("Tier", "")).strip()
        if tier_row == tier_komp:
            skor += 30
        elif tier_row and tier_komp:
            # Tier mirip (Mid vs Mid-Range, dll)
            tier_lower = tier_row.lower()
            tier_komp_lower = tier_komp.lower()
            if ("mid" in tier_lower and "mid" in tier_komp_lower) or \
               ("flag" in tier_lower and "flag" in tier_komp_lower) or \
               ("high" in tier_lower and "high" in tier_komp_lower):
                skor += 15
        
        # 3. Skor Chipset (max 30 poin)
        if chipset_komp and "Chipset" in row.index:
            chipset_row = str(row.get("Chipset", "")).strip().lower()
            if chipset_row == chipset_komp:
                skor += 30  # Chipset persis sama
            elif chipset_komp and chipset_row:
                # Chipset sekelas (misal: Snapdragon 6s Gen 4 vs Snapdragon 6s Gen 3)
                # Ambil kata kunci utama (Snapdragon 6s, Dimensity 7xxx, dll)
                chipset_komp_key = chipset_komp.split()[0] if chipset_komp.split() else ""
                chipset_row_key = chipset_row.split()[0] if chipset_row.split() else ""
                if chipset_komp_key and chipset_komp_key == chipset_row_key:
                    skor += 15
                # Cek angka seri yang sama
                import re
                angka_komp = re.findall(r'\d+', chipset_komp)
                angka_row = re.findall(r'\d+', chipset_row)
                if angka_komp and angka_row and angka_komp[0] == angka_row[0]:
                    skor += 10
        
        return skor
    
    if len(kandidat) > 0:
        kandidat["Skor"] = kandidat.apply(hitung_skor, axis=1)
        kandidat = kandidat.sort_values("Skor", ascending=False).head(top_n)
    else:
        kandidat["Skor"] = []
    
    return kandidat, data_komp

# ============================================
# 3. LOGIC GENERATE IDE PROBING
# ============================================
def generate_ide_probing(data_kosong, data_alternatif, mode="toko"):
    """
    mode="toko" → produk toko kosong
    mode="kompetitor" → produk kompetitor dicari match-nya
    """
    nama_kosong = data_kosong["Nama_Lengkap"]
    nama_alt = data_alternatif["Nama_Lengkap"]
    brand_alt = data_alternatif["Brand"]
    
    kelebihan = []
    for i in range(1, 4):
        kolom = f"Kelebihan_{i}"
        if kolom in data_alternatif and pd.notna(data_alternatif[kolom]):
            kelebihan.append(data_alternatif[kolom])
    
    if len(kelebihan) >= 2:
        kelebihan_teks = f"{kelebihan[0]} dan {kelebihan[1]}"
    elif len(kelebihan) == 1:
        kelebihan_teks = kelebihan[0]
    else:
        kelebihan_teks = "spesifikasi yang nggak kalah bagus"
    
    # ✨ Kalau mode KOMPETITOR, pembukanya beda
    if mode == "kompetitor":
        pembuka = (f"Kak, {nama_kosong} memang nggak kami jual, "
                   f"tapi saya punya rekomendasi yang spesifikasinya mirip banget: {nama_alt}. "
                   f"Sebelum saya jelasin, boleh tahu Kakak paling prioritasin apa dari HP itu—"
                   f"performa, baterai, atau kamera?")
        penawaran = f"Nah, {nama_alt} ini punya {kelebihan_teks}, persis seperti yang Kakak cari."
    else:
        if brand_alt == "iPhone":
            pembuka = f"Kak, {nama_kosong} lagi kosong nih. Boleh saya tahu, Kakak biasanya paling sering pakai HP buat apa? Kalau buat foto dan konten, kita ada {nama_alt} yang sekelas dan nggak kalah keren."
        elif brand_alt == "Samsung":
            pembuka = f"Kak, {nama_kosong} stoknya habis. Sebelum saya kasih rekomendasi, boleh tahu Kakak lebih prioritasin kamera, baterai, atau performa? Kalau soal itu, kita ada {nama_alt} yang bisa jadi pertimbangan."
        else:
            pembuka = f"Kak, {nama_kosong} lagi kosong. Boleh saya tanya dulu, Kakak biasanya cari HP yang fokusnya ke mana—kamera, gaming, atau baterai awet? Kalau boleh saya saranin, {nama_alt} ini menarik buat dipertimbangkan."
        
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
st.subheader("🔍 HP apa yang sedang kosong / dicari customer?")
st.markdown("*Biar aku bantu cariin penggantinya lengkap dengan cara jualan ☺️*")

# ✨ Gabungin semua nama produk (toko + kompetitor)
pilihan_toko = df_toko["Nama_Lengkap"].unique().tolist()
pilihan_kompetitor = df_kompetitor["Nama_Lengkap"].unique().tolist() if not df_kompetitor.empty else []
pilihan_unik = sorted(pilihan_toko + pilihan_kompetitor)

def search_hp(searchterm: str):
    if not searchterm:
        return pilihan_unik
    return [
        hp for hp in pilihan_unik 
        if searchterm.lower() in hp.lower()
    ]

pilihan_customer = st_searchbox(
    search_hp,
    label="🔎 Cari HP yang sedang kosong / dicari customer:",
    placeholder="Ketik atau pilih nama HP...",
    key="search_hp",
    default_options=pilihan_unik
)

# ✨ Slider + tombol refresh di sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan")
    max_selisih = st.slider(
        "Toleransi selisih harga (Rp):", 
        min_value=500000, max_value=5000000, 
        value=2500000, step=500000,
        format="Rp %d"
    )
    top_n = st.slider("Jumlah rekomendasi:", 1, 10, 5)
    
    st.markdown("---")
    st.markdown("### 🔄 Update Data")
    st.caption("Klik tombol di bawah kalau habis edit Excel & upload ke GitHub.")
    
    if st.button("🔄 Refresh Data Sekarang", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data berhasil di-refresh!")
        st.rerun()

# ============================================
# 5. LOGIC UTAMA: Deteksi apakah produk toko atau kompetitor
# ============================================
if pilihan_customer:
    # Cek apakah produk ini ada di toko kita atau di sheet Kompetitor
    is_produk_toko = pilihan_customer in pilihan_toko
    is_produk_kompetitor = pilihan_customer in pilihan_kompetitor
    
    if is_produk_toko:
        # ==========================================
        # FLOW 1: Produk toko kosong
        # ==========================================
        mode = "toko"
        kandidat, data_kosong = cari_alternatif(
            pilihan_customer, df_toko, max_selisih, top_n
        )
        
        st.info(f"ℹ️ **{pilihan_customer}** adalah produk toko yang sedang kosong.")
        
    elif is_produk_kompetitor:
        # ==========================================
        # FLOW 2: Produk kompetitor (nggak dijual)
        # ==========================================
        mode = "kompetitor"
        kandidat, data_kosong = cari_alternatif_dari_kompetitor(
            pilihan_customer, df_kompetitor, df_toko, 
            max_selisih_persen=0.3, top_n=3
        )
        
        st.warning(f"⚠️ **{pilihan_customer}** TIDAK DIJUAL di toko kami. "
                   f"Tapi kita punya alternatif dengan spek serupa! 🎯")
        
    else:
        st.error(f"❌ Produk **{pilihan_customer}** tidak ditemukan di database.")
        st.stop()
    
    # ==========================================
    # TAMPILAN HASIL (sama untuk kedua flow)
    # ==========================================
    if len(kandidat) == 0:
        st.warning(f"⚠️ Nggak ada alternatif untuk {pilihan_customer}. "
                   f"Coba naikkan toleransi di sidebar atau tambah data produk.")
    else:
        st.success(f"🔥 Ditemukan **{len(kandidat)} rekomendasi** pengganti untuk {pilihan_customer}!")
        
        # Info produk acuan
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Harga Acuan", f"Rp {data_kosong['Harga']:,.0f}")
        col_b.metric("Tier", data_kosong.get('Tier', '-'))
        col_c.metric("Brand", data_kosong['Brand'])
        
        # ✨ Kalau mode kompetitor, tampilkan chipset-nya juga
        if mode == "kompetitor" and has_chipset_komp:
            chipset_komp = data_kosong.get('Chipset', '-')
            if pd.notna(chipset_komp):
                st.caption(f"🔧 Chipset acuan: **{chipset_komp}**")
        
        st.markdown("---")
        
        # Tabs alternatif
        nama_target = kandidat["Nama_Lengkap"].tolist()
        tabs = st.tabs([f"📱 {nama}" for nama in nama_target])
        
        for index, tab in enumerate(tabs):
            with tab:
                baris_data = kandidat.iloc[index]
                
                st.markdown(f"### 🎯 Alternatif: {baris_data['Nama_Lengkap']}")
                
                selisih = baris_data["Harga"] - data_kosong["Harga"]
                tanda = "+" if selisih > 0 else ""
                st.caption(f"💰 Harga: **Rp {baris_data['Harga']:,.0f}** "
                           f"({tanda}Rp {selisih:,.0f} dari {pilihan_customer}) | "
                           f"🎯 Skor Kecocokan: **{baris_data['Skor']:.0f}/100**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"📊 Kelebihan {baris_data['Nama_Lengkap']}")
                    for i in range(1, 4):
                        kolom = f"Kelebihan_{i}"
                        if kolom in baris_data and pd.notna(baris_data[kolom]):
                            st.write(f"✅ {baris_data[kolom]}")
                    
                    # ✨ Tampilkan chipset produk toko (biar keliatan match-nya)
                    if mode == "kompetitor" and has_chipset_toko:
                        chipset_row = baris_data.get('Chipset', '-')
                        if pd.notna(chipset_row):
                            st.caption(f"🔧 Chipset: **{chipset_row}**")
                
                with col2:
                    st.warning("💬 Ide Probing")
                    ide_probing = generate_ide_probing(data_kosong, baris_data, mode=mode)
                    st.write(f"*{ide_probing}*")

else:
    st.info("👆 Ketik atau pilih nama HP di kolom pencarian untuk mulai.")
    if not df_kompetitor.empty:
        st.caption(f"💡 Total: **{len(pilihan_toko)}** produk toko + "
                   f"**{len(pilihan_kompetitor)}** produk kompetitor di database")
