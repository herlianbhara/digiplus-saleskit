import re
import csv
import os
import uuid
import html
from datetime import datetime, timezone, timedelta

import streamlit as st
import pandas as pd
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="Digiplus Smart Sales Assistant", page_icon="D",
                   layout="wide", initial_sidebar_state="collapsed")

# Warna aksen merah Digiplus: ubah #E31E24 di bawah kalau perlu
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
html, body, .stApp, button, input, textarea, [class*="st-"] {font-family: 'Roboto', Arial, sans-serif !important;}
.stApp {background: radial-gradient(1100px 520px at 85% -10%, rgba(227,30,36,.12), transparent 60%), #06080D; color: #F5F5F5;}
header[data-testid="stHeader"] {background: transparent;} #MainMenu, footer {visibility: hidden;}
.block-container {max-width: 1080px; padding: 1.4rem 1rem 4rem;}
.dp-head {display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid rgba(255,255,255,.08); padding-bottom:.8rem;}
.dp-brand {font-size:.8rem; letter-spacing:.35em; color:#E31E24; font-weight:700;}
.dp-title {font-size:1.5rem; font-weight:300; letter-spacing:.14em;}
.dp-tag {font-size:.65rem; letter-spacing:.22em; color:#9CA3AF;}
.dp-sub {color:#A7AFBF; font-size:.95rem; margin:.7rem 0 1rem;}
.dp-h {font-size:.72rem; letter-spacing:.28em; color:#9CA3AF; text-transform:uppercase; margin:1.6rem 0 .6rem; font-weight:500;}
.dp-label, .dp-sl {font-size:.68rem; letter-spacing:.28em; color:#E31E24; font-weight:700; margin-bottom:.4rem;}
.dp-sl {margin-top:.6rem;}
.dp-card {background: rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.09); border-radius:14px; padding:1.2rem 1.3rem; box-shadow:0 10px 40px rgba(0,0,0,.35);}
.dp-hero {box-shadow: 0 0 0 1px rgba(227,30,36,.35), 0 18px 60px rgba(227,30,36,.10); animation: dpin .35s ease;}
@keyframes dpin {from {opacity:0; transform: translateY(6px);} to {opacity:1; transform:none;}}
.dp-status {display:flex; gap:.8rem; align-items:flex-start; padding:.9rem 1.1rem; border-radius:12px; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08); margin:1rem 0;}
.dp-dot {width:9px; height:9px; border-radius:50%; margin-top:.4rem; background:#E31E24; box-shadow:0 0 12px #E31E24;}
.dp-s-warn .dp-dot {background:#E0A526; box-shadow:0 0 12px #E0A526;}
.dp-slabel {font-size:.68rem; letter-spacing:.26em; color:#9CA3AF; font-weight:500;}
.dp-sname {font-size:1.15rem; font-weight:500;} .dp-sdesc {font-size:.85rem; color:#A7AFBF;}
.dp-mono {height:150px; border-radius:10px; display:flex; flex-direction:column; justify-content:center; align-items:center;
          background: linear-gradient(145deg, rgba(255,255,255,.06), rgba(255,255,255,.01)); border:1px solid rgba(255,255,255,.07); margin-bottom:1rem;}
.dp-mono-b {font-size:1.7rem; letter-spacing:.2em; font-weight:300; text-transform:uppercase;} .dp-mono-c {font-size:.8rem; color:#9CA3AF; margin-top:.3rem;}
.dp-img {width:100%; max-height:260px; object-fit:contain; margin-bottom:1rem;}
.dp-name {font-size:1.7rem; font-weight:700; line-height:1.2;} .dp-price {font-size:1.25rem; margin-top:.4rem; font-weight:300;}
.dp-badge {display:inline-block; font-size:.78rem; padding:2px 10px; border-radius:999px; margin-left:.5rem; background:rgba(255,255,255,.08); font-weight:500;}
.dp-up {color:#E0A526; background:rgba(224,165,38,.12);} .dp-down {color:#4FBF8B; background:rgba(79,191,139,.12);}
.dp-chips {margin:.8rem 0;} .dp-chip {display:inline-block; font-size:.74rem; padding:3px 11px; margin:0 .4rem .4rem 0; border:1px solid rgba(255,255,255,.16); border-radius:999px; color:#D6DAE3;}
.dp-score-t {display:flex; justify-content:space-between; font-size:.7rem; letter-spacing:.2em; color:#9CA3AF;} .dp-score-t b {color:#fff; font-size:.95rem; letter-spacing:0;}
.dp-bar {height:5px; border-radius:99px; background:rgba(255,255,255,.1); margin-top:.45rem; overflow:hidden;}
.dp-bar > div {height:100%; background:#E31E24; border-radius:99px; transition: width .8s ease;}
.dp-target, .dp-note {font-size:.82rem; color:#A7AFBF; margin-top:.8rem;} .dp-note {color:#E0A526;}
.dp-pts {display:grid; grid-template-columns:repeat(3,1fr); gap:.8rem;}
.dp-pt {background:rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.09); border-radius:12px; padding:1rem;}
.dp-pn {font-size:.72rem; color:#E31E24; font-weight:700; letter-spacing:.15em;} .dp-pk {font-size:.66rem; letter-spacing:.24em; color:#9CA3AF; margin:.35rem 0;}
.dp-pv {font-size:.98rem; line-height:1.45;}
.dp-why {display:grid; gap:.45rem;} .dp-w {display:flex; gap:.6rem; align-items:center; font-size:.93rem; color:#E5E7EB;}
.dp-w i {width:7px; height:7px; border-radius:50%; background:#4FBF8B; flex:none;} .dp-w.no i {background:#6B7280;}
.dp-cmp {display:grid; grid-template-columns: 90px 1fr 1fr; gap:.55rem .9rem; font-size:.88rem;}
.dp-ch {font-size:.72rem; color:#9CA3AF; letter-spacing:.1em;} .dp-ch b {display:block; color:#fff; font-size:.92rem; letter-spacing:0; font-weight:500;}
.dp-cl {color:#9CA3AF; font-size:.76rem;} .dp-cv {color:#E5E7EB;} .dp-cb {color:#fff; border-left:2px solid #E31E24; padding-left:.7rem;}
.dp-done {border:1px solid rgba(79,191,139,.4); color:#4FBF8B; padding:.8rem 1rem; border-radius:12px; background:rgba(79,191,139,.07);}
.dp-pilot {margin-top:2.2rem; padding:1rem 1.2rem; border-top:1px solid rgba(255,255,255,.08);}
.dp-pl {font-size:.66rem; letter-spacing:.28em; color:#9CA3AF;} .dp-pn2 {font-size:1.6rem; font-weight:300;} .dp-pn2 span {font-size:.72rem; letter-spacing:.2em; color:#9CA3AF;}
.dp-empty {padding:2.4rem 1rem; text-align:center; font-size:1.1rem; color:#E5E7EB;} .dp-empty span {color:#9CA3AF; font-size:.9rem;}
/* tombol & selector bergaya produk, bukan Streamlit default */
div.stButton > button {width:100%; min-height:3.1rem; border-radius:12px; background:rgba(255,255,255,.05); color:#fff; border:1px solid rgba(255,255,255,.14); transition: all .2s ease;}
div.stButton > button:hover {border-color:#E31E24; background:rgba(227,30,36,.12); color:#fff;}
div[role="radiogroup"] {gap:.5rem;} div[role="radiogroup"] label {background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.1); border-radius:12px; padding:.75rem .9rem; width:100%; transition: all .2s ease;}
div[role="radiogroup"] label:has(input:checked) {border-color:#E31E24; background:rgba(227,30,36,.14); box-shadow:0 0 18px rgba(227,30,36,.25);}
div[role="radiogroup"] label > div:first-child {display:none;}
div[data-testid="stCode"] pre {white-space: pre-wrap !important; line-height:1.55;}
@media (max-width: 768px) {
  .st-key-showcase [data-testid="stHorizontalBlock"] {flex-direction: column-reverse; gap:.6rem;}
  .st-key-showcase div[role="radiogroup"] {flex-direction: row; overflow-x:auto; flex-wrap:nowrap;}
  .st-key-showcase div[role="radiogroup"] label {white-space:nowrap; width:auto;}
  .dp-pts {grid-template-columns:1fr;} .dp-cmp {grid-template-columns: 70px 1fr 1fr; font-size:.82rem;}
  .dp-name {font-size:1.4rem;} .dp-title {font-size:1.1rem;} .dp-tag {display:none;}
}
</style>
""", unsafe_allow_html=True)

# >>> LOGIKA (fungsi murni, tanpa Streamlit) >>>
# ============================================
# 1. BOBOT SKOR (total maksimal 100)
# ============================================
W_HARGA = 25
W_TIER = 15
W_CHIPSET = 20
W_BENTUK = 20     # hanya dihitung kalau salah satu HP lipat (lipat dicocokkan dengan lipat)
W_BRAND = 5       # hanya untuk mode "toko" (produk toko kosong)
W_POSISI = 10      # kemiripan target pengguna (hanya kalau kedua produk punya datanya)

PRIORITAS = {
    "⚡ Performa": "performa",
    "🔋 Baterai": "baterai",
    "📸 Kamera": "kamera",
    "🖥️ Layar": "layar",
    "🛡️ Tahan banting": "tahan",
}

# Pola kata kunci yang dicari di kolom Kelebihan_1..3 dan Target_User
POLA = {
    "performa": [r"performa", r"gaming|gamer", r"\bfps\b", r"prosesor|processor",
                 r"chipset", r"\bram\b", r"multitasking", r"kencang|ngebut"],
    "baterai": [r"baterai|battery", r"mah", r"charging|\d+\s?w\b", r"awet"],
    "kamera": [r"kamera|camera", r"foto|fotografer", r"telefoto|zoom|optik",
               r"\d+\s?mp\b", r"video|selfie", r"konten|content"],
    "layar": [r"layar|display", r"amoled|oled|lcd", r"\d+\s?hz", r"nits"],
    "tahan": [r"ip6\d", r"gorilla|victus", r"benturan|gores|militer",
              r"tahan air|tahan banting|tahan debu|anti.?air"],
}


def clean(v):
    """Ubah nilai sel Excel jadi teks bersih, atau None kalau kosong/NaN."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    return s if s and s.lower() != "nan" else None


def rp(x):
    try:
        return "Rp " + f"{float(x):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "-"


def rp_selisih(x):
    tanda = "+" if x > 0 else "−" if x < 0 else ""
    return f"{tanda}{rp(abs(x))}"


def gabung_nama(row):
    brand = str(row["Brand"]).strip()
    model = str(row["Model"]).strip()
    if model.lower().startswith(brand.lower()):
        return model
    return f"{brand} {model}"


def teks_produk(row):
    bagian = []
    for kolom in ["Kelebihan_1", "Kelebihan_2", "Kelebihan_3", "Target_User"]:
        t = clean(row.get(kolom))
        if t:
            bagian.append(t)
    return " | ".join(bagian)


def ringkas(teks, maks=70):
    """Ambil bagian depan sebelum tanda ' — ' dan potong di batas kata."""
    t = re.split(r"\s[—–-]\s", teks)[0].strip()
    if len(t) > maks:
        t = t[:maks].rsplit(" ", 1)[0]
    return t


def ambil_mah(teks):
    nilai = []
    for m in re.finditer(r"(\d{1,2}[.,]?\d{3})\s*mah", teks.lower()):
        try:
            nilai.append(int(re.sub(r"[.,]", "", m.group(1))))
        except ValueError:
            pass
    return max(nilai) if nilai else None


def fmt_mah(mah):
    return f"{mah:,}".replace(",", ".") + "mAh"


def level_tier(tier):
    s = (clean(tier) or "").lower()
    if not s:
        return None
    if "flag" in s or "premium" in s:
        return 4
    if ("mid" in s and "high" in s) or "upper" in s:
        return 3
    if "mid" in s:
        return 2
    if "entry" in s or "budget" in s or "low" in s:
        return 1
    return None


def level_chipset(nama):
    """Perkiraan kelas performa chipset (1 = entry ... 5 = flagship)."""
    s = (clean(nama) or "").lower()
    if not s:
        return None
    if "snapdragon" in s or "qualcomm" in s:
        m3 = re.search(r"snapdragon\s*(\d)\d{2}\b", s)
        if m3:
            return {8: 5, 7: 3.5, 6: 2, 4: 1.5}.get(int(m3.group(1)))
        m = re.search(r"snapdragon\s*(\d)", s)
        if m:
            return {8: 5, 7: 4, 6: 3, 4: 2}.get(int(m.group(1)))
    if "dimensity" in s:
        m = re.search(r"dimensity\s*(\d)", s)
        if m:
            return {9: 5, 8: 4, 7: 3.5, 6: 2.5}.get(int(m.group(1)))
    if "exynos" in s:
        m = re.search(r"exynos\s*(\d)", s)
        if m:
            return {2: 5, 1: 3.5}.get(int(m.group(1)))
    if "kirin" in s:
        m = re.search(r"kirin\s*(\d)", s)
        if m:
            return {9: 5, 8: 3.5}.get(int(m.group(1)))
    if "tensor" in s:
        return 4.5
    if "apple" in s or re.search(r"\ba\d{2}\b", s):
        return 5
    if "helio" in s:
        return 2
    if "unisoc" in s:
        return 1.5
    return None


def adalah_lipat(nama):
    return bool(re.search(r"fold|flip|razr|find n\d|mate x\d|magic v\d", str(nama).lower()))


def kekuatan_prioritas(key, row, level_chip):
    """Seberapa kuat produk memenuhi satu prioritas (0.0 - 1.0)."""
    teks = teks_produk(row).lower()
    hits = sum(1 for p in POLA[key] if re.search(p, teks))
    if key == "baterai":
        mah = ambil_mah(teks)
        if mah:
            return (1.0 if mah >= 7000 else 0.85 if mah >= 6000 else
                    0.7 if mah >= 5000 else 0.5 if mah >= 4500 else 0.3)
        return min(1, hits / 3) * 0.5
    if key == "performa":
        dasar = min(1, hits / 2)
        if level_chip:
            return 0.6 * (level_chip / 5) + 0.4 * dasar
        return 0.6 * dasar
    return min(1, hits / 3)


def cari_bukti(key, row):
    """Kutipan singkat dari data produk sebagai alasan (atau None)."""
    if key == "baterai":
        mah = ambil_mah(teks_produk(row))
        if mah:
            return f"baterai {fmt_mah(mah)}"
    if key == "performa" and clean(row.get("Chipset")):
        return f"chipset {clean(row.get('Chipset'))}"
    for kolom in ["Kelebihan_1", "Kelebihan_2", "Kelebihan_3"]:
        t = clean(row.get(kolom))
        if t and any(re.search(p, t.lower()) for p in POLA[key]):
            return ringkas(t, 60)
    return None


def hitung_kecocokan(ref, alt, mode, prioritas, tol):
    """Skor 0-100 yang transparan: setiap poin punya alasan."""
    dapat, maks, alasan = 0.0, 0, []

    # --- Harga ---
    selisih = float(alt["Harga"]) - float(ref["Harga"])
    maks += W_HARGA
    p = W_HARGA * max(0.0, 1 - abs(selisih) / tol) if tol > 0 else 0.0
    dapat += p
    if p >= 0.6 * W_HARGA:
        alasan.append(("✅", f"Harga dekat, selisih {rp_selisih(selisih)}"))
    else:
        alasan.append(("➖", f"Selisih harga cukup jauh ({rp_selisih(selisih)})"))

    # --- Tier ---
    maks += W_TIER
    lt_ref, lt_alt = level_tier(ref.get("Tier")), level_tier(alt.get("Tier"))
    t_ref, t_alt = clean(ref.get("Tier")) or "-", clean(alt.get("Tier")) or "-"
    if lt_ref is None or lt_alt is None:
        alasan.append(("➖", "Data tier belum lengkap"))
    elif lt_ref == lt_alt:
        dapat += W_TIER
        alasan.append(("✅", f"Tier sama ({t_alt})"))
    elif abs(lt_ref - lt_alt) == 1:
        dapat += W_TIER * 0.5
        alasan.append(("➖", f"Tier berdekatan ({t_alt} vs {t_ref})"))
    else:
        alasan.append(("➖", f"Beda tier cukup jauh ({t_alt} vs {t_ref})"))

    # --- Chipset ---
    maks += W_CHIPSET
    c_ref, c_alt = clean(ref.get("Chipset")), clean(alt.get("Chipset"))
    lc_ref, lc_alt = level_chipset(c_ref), level_chipset(c_alt)
    if c_ref and c_alt and c_ref.lower() == c_alt.lower():
        dapat += W_CHIPSET
        alasan.append(("✅", f"Chipset sama ({c_alt})"))
    elif lc_ref is None or lc_alt is None:
        alasan.append(("➖", "Data chipset belum lengkap"))
    else:
        beda = abs(lc_ref - lc_alt)
        poin = (1.0 if beda == 0 else 0.75 if beda <= 0.5 else
                0.5 if beda <= 1 else 0.25 if beda <= 1.5 else 0.0)
        dapat += W_CHIPSET * poin
        if poin >= 0.75:
            alasan.append(("✅", f"Chipset sekelas ({c_alt} ≈ {c_ref})"))
        else:
            alasan.append(("➖", f"Chipset beda kelas ({c_alt} vs {c_ref})"))

    # --- Brand (khusus produk toko kosong) ---
    if mode == "toko":
        maks += W_BRAND
        if str(alt.get("Brand")) == str(ref.get("Brand")):
            dapat += W_BRAND
            alasan.append(("✅", f"Brand sama ({alt.get('Brand')})"))

    # --- Bentuk: hanya relevan kalau salah satu HP lipat ---
    lipat_ref = adalah_lipat(ref.get("Nama_Lengkap"))
    lipat_alt = adalah_lipat(alt.get("Nama_Lengkap"))
    if lipat_ref or lipat_alt:
        maks += W_BENTUK
        if lipat_ref == lipat_alt:
            dapat += W_BENTUK
            alasan.append(("✅", "Sama-sama HP lipat"))
        else:
            alasan.append(("➖", "Bentuk berbeda (HP lipat vs HP biasa)"))

    # --- Positioning: kemiripan Target_User (kedua produk harus punya datanya) ---
    stop = {"dan", "atau", "yang", "untuk", "hp", "suka", "pengguna"}
    ta = set(re.findall(r"[a-z]+", (clean(ref.get("Target_User")) or "").lower())) - stop
    tb = set(re.findall(r"[a-z]+", (clean(alt.get("Target_User")) or "").lower())) - stop
    if ta and tb:
        maks += W_POSISI
        mirip = len(ta & tb) / len(ta | tb)
        dapat += W_POSISI * min(1.0, mirip * 2)
        if mirip > 0:
            alasan.append(("✅", "Target pengguna mirip: " + ", ".join(sorted(ta & tb))))

    skor = min(100, round(dapat / maks * 100)) if maks > 0 else 0
    return {"skor": skor, "alasan": alasan, "selisih": selisih}


def cari_alternatif(ref, pool, mode, tol, top_n, prioritas):
    kandidat = pool[pool["Nama_Lengkap"] != ref["Nama_Lengkap"]]
    hasil = []
    for _, row in kandidat.iterrows():
        try:
            sel = float(row["Harga"]) - float(ref["Harga"])
        except (TypeError, ValueError):
            continue
        if pd.isna(sel) or abs(sel) > tol:
            continue
        h = hitung_kecocokan(ref, row, mode, prioritas, tol)
        h["row"] = row
        hasil.append(h)
    hasil.sort(key=lambda x: (-x["skor"], abs(x["selisih"])))
    return hasil[:top_n]


def poin_singkat(row, prioritas, n=2):
    daftar = [clean(row.get(f"Kelebihan_{i}")) for i in range(1, 4)]
    daftar = [d for d in daftar if d]
    if prioritas:
        pola = [p for key in prioritas for p in POLA[key]]
        daftar.sort(key=lambda t: 0 if any(re.search(p, t.lower()) for p in pola) else 1)
    return [ringkas(d) for d in daftar[:n]]


def gabung_teks(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " dan " + items[-1]


def kecil(t):
    """Huruf kecil di awal kalimat sambungan, kecuali singkatan (AMOLED, iPhone)."""
    return t if len(t) < 2 or t[1].isupper() else t[0].lower() + t[1:]


def buat_script(ref_nama, alt_row, mode, selisih):
    """Script 3 bagian dari data produk asli. Tidak mengklaim hal yang tidak ada di data."""
    kondisi = "memang belum kami jual di Digiplus" if mode == "kompetitor" else "saat ini belum tersedia di Digiplus"
    tier = clean(alt_row.get("Tier"))
    kelas = f"di kelas {tier} dengan kisaran harga yang cukup dekat" if tier else "dengan kisaran harga yang cukup dekat"
    opening = (f"Baik Kak, untuk {ref_nama} {kondisi}. Tapi supaya Kakak tidak perlu cari ke tempat lain, "
               f"saya punya satu alternatif {kelas}, yang menurut saya layak dipertimbangkan.")

    alt_nama = alt_row["Nama_Lengkap"]
    poin = [kecil(ringkas(p)) for p in (clean(alt_row.get(f"Kelebihan_{i}")) for i in (1, 2, 3)) if p]
    chip = clean(alt_row.get("Chipset"))
    rec = f"Ini {alt_nama}."
    if poin:
        rec += f" Yang menonjol: {gabung_teks(poin)}."
    if chip:
        rec += f" Chipsetnya {chip}."
    target = clean(alt_row.get("Target_User"))
    if target:
        rec += f" Produk ini biasanya cocok untuk {kecil(target)}."
    if selisih < -500000:
        rec += f" Untuk harganya, ada selisih {rp(abs(selisih))} lebih hemat dibanding {ref_nama}."
    elif selisih > 500000:
        rec += f" Untuk harganya, ada selisih sekitar {rp(selisih)} dari {ref_nama}, dan menurut saya itu layak Kakak pertimbangkan."
    else:
        rec += f" Untuk harganya, berada di kisaran yang hampir sama dengan {ref_nama}."
    rec += " Jadi walaupun produknya berbeda, kebutuhan Kakak tetap bisa kita bantu cari yang paling pas."

    closing = ("Kalau Kakak berkenan, saya tunjukkan unitnya dan kita bandingkan langsung ya. "
               "Boleh saya tahu, hal apa yang paling Kakak pentingkan di HP ini? Supaya saya bisa bantu arahkan lebih tepat.")
    return {"opening": opening, "recommendation": rec, "closing": closing}


def tabel_banding(ref, alt):
    baris = [
        ("Harga", rp(ref["Harga"]), rp(alt["Harga"])),
        ("Tier", clean(ref.get("Tier")) or "-", clean(alt.get("Tier")) or "-"),
        ("Chipset", clean(ref.get("Chipset")) or "-", clean(alt.get("Chipset")) or "-"),
    ]
    m_ref, m_alt = ambil_mah(teks_produk(ref)), ambil_mah(teks_produk(alt))
    baris.append(("Baterai", fmt_mah(m_ref) if m_ref else "-", fmt_mah(m_alt) if m_alt else "-"))
    baris.append(("Cocok untuk", clean(ref.get("Target_User")) or "-",
                  clean(alt.get("Target_User")) or "-"))
    baris = [b for b in baris if not (b[1] == "-" and b[2] == "-")]
    df = pd.DataFrame(baris, columns=["Spesifikasi", ref["Nama_Lengkap"], alt["Nama_Lengkap"]])
    return df.set_index("Spesifikasi")
SKIP_SHEETS = ["Panduan", "Master", "Notes", "Template", "Sheet1", "Log"]


def baca_worksheet(ws):
    """Ubah 1 worksheet Google Sheets jadi DataFrame (baris 1 = header)."""
    nilai = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    if len(nilai) < 2:
        return pd.DataFrame()
    header = [str(h).strip() for h in nilai[0]]
    lebar = len(header)
    baris = [(list(r) + [""] * (lebar - len(r)))[:lebar] for r in nilai[1:]]
    df = pd.DataFrame(baris, columns=header)
    return df.replace("", pd.NA)


def susun_data(sheets_dict):
    """Pisahkan sheet Kompetitor dari sheet produk toko, lalu bersihkan."""
    sheets_dict = dict(sheets_dict)
    df_kompetitor = sheets_dict.pop("Kompetitor", pd.DataFrame())
    valid = {n: s for n, s in sheets_dict.items()
             if n not in SKIP_SHEETS and not s.empty and "Brand" in s.columns}
    if not valid:
        raise ValueError("Belum ada data produk toko.")
    df_toko = pd.concat(valid.values(), ignore_index=True)
    df_toko = df_toko.dropna(subset=["Brand", "Model"])
    df_toko["Harga"] = pd.to_numeric(df_toko["Harga"], errors="coerce")
    if not df_kompetitor.empty:
        df_kompetitor = df_kompetitor.dropna(subset=["Brand", "Model"])
        df_kompetitor["Harga"] = pd.to_numeric(df_kompetitor["Harga"], errors="coerce")
    return df_toko, df_kompetitor
# <<< LOGIKA <<<

# ============================================
# 2. LOGGING (Google Sheets, fallback ke CSV lokal)
# ============================================
WIB = timezone(timedelta(hours=7))
LOG_HEADER = [
    "Timestamp", "Attempt_ID", "Event", "Produk_Dicari", "Mode",
    "Jumlah_Rekomendasi", "Alternatif_1", "Alternatif_2", "Alternatif_3", "Hasil",
]
LOCAL_LOG_FILE = "log_switch_selling.csv"
TARGET_ATTEMPTS = 200


@st.cache_resource
def get_log_sheet():
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(st.secrets["gsheets"]["spreadsheet_id"])
        try:
            ws = sh.worksheet("Log")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="Log", rows=1000, cols=len(LOG_HEADER))
        if ws.row_values(1) != LOG_HEADER:
            # header lama punya kolom "Sales": rapikan ke header baru (kolom Event tetap di kolom C)
            ws.update(range_name="A1", values=[LOG_HEADER + [""]])
        return ws, None
    except Exception as e:
        return None, str(e)


def tulis_log(row):
    ws, _ = get_log_sheet()
    if ws is not None:
        try:
            ws.append_row(row, value_input_option="USER_ENTERED")
            return True
        except Exception:
            pass
    file_baru = not os.path.exists(LOCAL_LOG_FILE)
    with open(LOCAL_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if file_baru:
            w.writerow(LOG_HEADER)
        w.writerow(row)
    return False


def catat_attempt(attempt_id, produk, mode, nama_alt):
    alt = (list(nama_alt) + ["", "", ""])[:3]
    row = [datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"), attempt_id, "attempt",
           produk, mode, len(nama_alt), alt[0], alt[1], alt[2], ""]
    return tulis_log(row)


def catat_outcome(attempt_id, produk, mode, hasil):
    row = [datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"), attempt_id, "outcome",
           produk, mode, "", "", "", "", hasil]
    return tulis_log(row)


@st.cache_data(ttl=30)
def hitung_total_attempt():
    ws, _ = get_log_sheet()
    try:
        if ws is not None:
            return ws.col_values(3).count("attempt")
        if os.path.exists(LOCAL_LOG_FILE):
            return int((pd.read_csv(LOCAL_LOG_FILE)["Event"] == "attempt").sum())
    except Exception:
        pass
    return 0


# ============================================
# 3. LOAD DATA
# ============================================
@st.cache_resource
def get_data_book():
    """Buka spreadsheet data produk. Pakai [gsheets] data_spreadsheet_id kalau ada,
    kalau tidak pakai spreadsheet yang sama dengan Log."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc = gspread.authorize(creds)
        sid = st.secrets["gsheets"].get("data_spreadsheet_id") or st.secrets["gsheets"]["spreadsheet_id"]
        return gc.open_by_key(sid), None
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=60)
def load_data():
    """Return (df_toko, df_kompetitor, sumber, catatan).
    Utama: Google Sheets. Cadangan: data_hp.xlsx (dengan catatan peringatan)."""
    catatan = None
    book, err = get_data_book()
    if book is not None:
        try:
            sheets = {ws.title: baca_worksheet(ws) for ws in book.worksheets()}
            df_toko, df_komp = susun_data(sheets)
            return df_toko, df_komp, "Google Sheets", None
        except ValueError:
            catatan = "Google Sheets belum berisi data produk (tab Samsung, Iphone, dst). Sementara memakai data_hp.xlsx."
        except Exception as e:
            catatan = f"Gagal membaca Google Sheets ({e}). Sementara memakai data_hp.xlsx, harga bisa jadi bukan yang terbaru."
    sheets_dict = pd.read_excel("data_hp.xlsx", sheet_name=None)
    df_toko, df_komp = susun_data(sheets_dict)
    return df_toko, df_komp, "Excel (data_hp.xlsx)", catatan


try:
    df_toko, df_kompetitor, sumber_data, catatan_data = load_data()
except FileNotFoundError:
    st.error("⚠️ Data produk tidak ditemukan. Isi tab produk di Google Sheets atau upload data_hp.xlsx.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error baca Excel: {e}")
    st.stop()

df_toko["Nama_Lengkap"] = df_toko.apply(gabung_nama, axis=1)
if not df_kompetitor.empty:
    df_kompetitor["Nama_Lengkap"] = df_kompetitor.apply(gabung_nama, axis=1)

pilihan_toko = df_toko["Nama_Lengkap"].unique().tolist()
pilihan_kompetitor = (
    df_kompetitor["Nama_Lengkap"].unique().tolist() if not df_kompetitor.empty else []
)
pilihan_unik = sorted(pilihan_toko + pilihan_kompetitor)

# ============================================
# 4. HEADER, PENCARIAN, HASIL (UI)
# ============================================
def esc(x):
    return html.escape(str(x))


def kategori_poin(teks):
    """Label kartu hanya kalau teksnya jelas; selain itu 'KEY SELLING POINT'."""
    t = teks.lower()
    for label, pola in [("CAMERA", POLA["kamera"]), ("BATTERY", POLA["baterai"]),
                        ("DISPLAY", POLA["layar"]), ("PERFORMANCE", POLA["performa"])]:
        if any(re.search(p, t) for p in pola):
            return label
    return "KEY SELLING POINT"


def gambar_produk(row):
    for kolom in ["Image_URL", "Image", "Foto", "Product_Image"]:
        u = clean(row.get(kolom))
        if u and u.lower().startswith("http"):
            return u
    return None


def render_header():
    st.markdown(
        '<div class="dp-head"><div><div class="dp-brand">DIGIPLUS</div>'
        '<div class="dp-title">SMART SALES ASSISTANT</div></div>'
        '<div class="dp-tag">SALES ENABLEMENT PLATFORM</div></div>'
        '<div class="dp-sub">Turn unavailable requests into selling opportunities.</div>',
        unsafe_allow_html=True)


def render_status(nama, mode):
    if mode == "toko":
        label, desk, kelas = "CURRENTLY UNAVAILABLE", "Produk Digiplus yang sedang tidak tersedia", "dp-s-warn"
    else:
        label, desk, kelas = "NOT SOLD AT DIGIPLUS", "Produk kompetitor yang tidak kami jual", "dp-s-red"
    st.markdown(
        f'<div class="dp-status {kelas}"><span class="dp-dot"></span><div>'
        f'<div class="dp-slabel">{label}</div><div class="dp-sname">{esc(nama)}</div>'
        f'<div class="dp-sdesc">{desk}. Berikut alternatif paling relevan.</div></div></div>',
        unsafe_allow_html=True)


def render_showcase(ref, h, rank, terbatas):
    row = h["row"]
    nama, skor, sel = row["Nama_Lengkap"], h["skor"], h["selisih"]
    img = gambar_produk(row)
    if img:
        visual = f'<img class="dp-img" src="{esc(img)}" alt="{esc(nama)}">'
    else:  # tanpa foto: kartu informasi yang rapi
        visual = (f'<div class="dp-mono"><div class="dp-mono-b">{esc(row.get("Brand", ""))}</div>'
                  f'<div class="dp-mono-c">{esc(clean(row.get("Chipset")) or "")}</div></div>')
    if sel > 0:
        badge = f'<span class="dp-badge dp-up">{esc(rp_selisih(sel))}</span>'
    elif sel < 0:
        badge = f'<span class="dp-badge dp-down">{esc(rp_selisih(sel))} lebih hemat</span>'
    else:
        badge = '<span class="dp-badge">Harga sama</span>'
    chips = "".join(f'<span class="dp-chip">{esc(c)}</span>' for c in
                    [clean(row.get("Tier")), clean(row.get("Chipset"))] if c)
    target = clean(row.get("Target_User"))
    judul = "BEST MATCH" if rank == 0 else f"ALTERNATIVE {rank + 1}"
    st.markdown(
        f'<div class="dp-card dp-hero"><div class="dp-label">{judul}</div>{visual}'
        f'<div class="dp-name">{esc(nama)}</div>'
        f'<div class="dp-price">{esc(rp(row["Harga"]))} {badge}</div>'
        f'<div class="dp-chips">{chips}</div>'
        f'<div class="dp-score"><div class="dp-score-t"><span>MATCH SCORE</span><b>{skor}/100</b></div>'
        f'<div class="dp-bar"><div style="width:{skor}%"></div></div></div>'
        + (f'<div class="dp-target">Target pengguna: {esc(target)}</div>' if target else "")
        + (f'<div class="dp-note">Skor berdasarkan data terbatas.</div>' if terbatas else "")
        + '</div>', unsafe_allow_html=True)


def render_poin(row):
    poin = [clean(row.get(f"Kelebihan_{i}")) for i in (1, 2, 3)]
    poin = [p for p in poin if p]
    if not poin:
        return
    st.markdown('<div class="dp-h">Yang bisa kita jual</div>', unsafe_allow_html=True)
    kartu = "".join(
        f'<div class="dp-pt"><div class="dp-pn">{i:02d}</div><div class="dp-pk">{kategori_poin(p)}</div>'
        f'<div class="dp-pv">{esc(p)}</div></div>' for i, p in enumerate(poin, 1))
    st.markdown(f'<div class="dp-pts">{kartu}</div>', unsafe_allow_html=True)


def render_alasan(h):
    st.markdown('<div class="dp-h">Why this product</div>', unsafe_allow_html=True)
    ringkas_alasan = h["alasan"][:4]
    st.markdown('<div class="dp-why">' + "".join(
        f'<div class="dp-w {"ok" if i == "✅" else "no"}"><i></i>{esc(t)}</div>' for i, t in ringkas_alasan)
        + '</div>', unsafe_allow_html=True)
    with st.expander("How was this score calculated?"):
        st.caption("Skor = harga, tier, chipset, bentuk (lipat/biasa), brand, dan kemiripan target pengguna. "
                   "Komponen tanpa data tidak dihitung, jadi skor tetap adil tapi bisa berbasis data terbatas.")
        for i, t in h["alasan"]:
            st.markdown(f"{i} {t}")


def render_script(ref_nama, row, mode, sel):
    s = buat_script(ref_nama, row, mode, sel)
    st.markdown('<div class="dp-h">Sales script</div>', unsafe_allow_html=True)
    st.caption("Tekan ikon copy di pojok kanan setiap bagian.")
    for judul, kunci in [("OPENING", "opening"), ("RECOMMENDATION", "recommendation"), ("CLOSING", "closing")]:
        st.markdown(f'<div class="dp-sl">{judul}</div>', unsafe_allow_html=True)
        try:
            st.code(s[kunci], language=None, wrap_lines=True)
        except TypeError:
            st.code(s[kunci], language=None)


def render_banding(ref, row):
    def baris(label, a, b):
        return (f'<div class="dp-cl">{esc(label)}</div><div class="dp-cv">{esc(a)}</div>'
                f'<div class="dp-cv dp-cb">{esc(b)}</div>')
    ma, mb = ambil_mah(teks_produk(ref)), ambil_mah(teks_produk(row))
    poin = lambda r: " • ".join(p for p in (clean(r.get(f"Kelebihan_{i}")) for i in (1, 2, 3)) if p) or "-"
    isi = (baris("Harga", rp(ref["Harga"]), rp(row["Harga"]))
           + baris("Tier", clean(ref.get("Tier")) or "-", clean(row.get("Tier")) or "-")
           + baris("Chipset", clean(ref.get("Chipset")) or "-", clean(row.get("Chipset")) or "-")
           + baris("Baterai", fmt_mah(ma) if ma else "-", fmt_mah(mb) if mb else "-")
           + baris("Target", clean(ref.get("Target_User")) or "-", clean(row.get("Target_User")) or "-")
           + baris("Selling points", poin(ref), poin(row)))
    st.markdown('<div class="dp-h">Comparison</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="dp-card dp-cmp"><div></div><div class="dp-ch">Diminta<br><b>{esc(ref["Nama_Lengkap"])}</b></div>'
        f'<div class="dp-ch dp-cb">Alternatif<br><b>{esc(row["Nama_Lengkap"])}</b></div>{isi}</div>',
        unsafe_allow_html=True)


def render_outcome(attempt_id, produk, mode):
    st.markdown('<div class="dp-h">Hasil percakapan</div>', unsafe_allow_html=True)
    sudah = st.session_state.get(f"outcome_{attempt_id}")
    if sudah:
        st.markdown(f'<div class="dp-done">Tercatat: <b>{esc(sudah)}</b></div>', unsafe_allow_html=True)
        return
    c1, c2, c3 = st.columns(3)
    pilihan = None
    if c1.button("Customer tertarik", key="o1"):
        pilihan = "Tertarik lihat alternatif"
    if c2.button("Switch berhasil / terjual", key="o2"):
        pilihan = "Switch berhasil"
    if c3.button("Customer tidak jadi", key="o3"):
        pilihan = "Tidak jadi"
    if pilihan:
        catat_outcome(attempt_id, produk, mode, pilihan)
        st.session_state[f"outcome_{attempt_id}"] = pilihan
        st.rerun()


def render_pilot():
    total = hitung_total_attempt()
    pct = min(100, total / TARGET_ATTEMPTS * 100)
    st.markdown(
        f'<div class="dp-pilot"><div class="dp-pl">SWITCH-SELLING PILOT</div>'
        f'<div class="dp-pn2">{total} <span>/ {TARGET_ATTEMPTS} ATTEMPTS</span></div>'
        f'<div class="dp-bar"><div style="width:{pct:.0f}%"></div></div></div>', unsafe_allow_html=True)


# --- Sidebar: hanya pengaturan lanjutan (sembunyi secara default) ---
with st.sidebar:
    st.markdown("### Pengaturan lanjutan")
    max_selisih = st.slider("Toleransi selisih harga (Rp), produk toko kosong",
                            500000, 5000000, 2500000, 500000)
    top_n = st.slider("Jumlah alternatif", 2, 6, 4)
    st.caption(f"Sumber data produk: {sumber_data}")
    if catatan_data:
        st.warning(catatan_data)
    if get_log_sheet()[0] is None:
        st.caption("Google Sheets belum terhubung. Log disimpan sementara di file lokal.")
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

render_header()


def search_hp(searchterm: str):
    if not searchterm:
        return pilihan_unik
    return [hp for hp in pilihan_unik if searchterm.lower() in hp.lower()]


pilihan_customer = st_searchbox(
    search_hp, label="Search product or competitor",
    placeholder="Search product or competitor...", key="search_hp",
    default_options=pilihan_unik)

if pilihan_customer:
    try:
        if pilihan_customer in pilihan_toko:
            mode = "toko"
            ref = df_toko[df_toko["Nama_Lengkap"] == pilihan_customer].iloc[0]
        elif pilihan_customer in pilihan_kompetitor:
            mode = "kompetitor"
            ref = df_kompetitor[df_kompetitor["Nama_Lengkap"] == pilihan_customer].iloc[0]
        else:
            st.error("Produk tidak ditemukan di database.")
            st.stop()
        if pd.isna(pd.to_numeric(ref["Harga"], errors="coerce")):
            st.error("Harga produk ini belum diisi, sehingga alternatif belum bisa dicari.")
            st.stop()

        harga_ref = float(ref["Harga"])
        tol = max(float(max_selisih), 0.15 * harga_ref) if mode == "toko" else 0.3 * harga_ref
        hasil = cari_alternatif(ref, df_toko, mode, tol, top_n, [])

        # Logging otomatis anonim: 1 attempt per pencarian (saat produk berubah)
        if st.session_state.get("last_logged_product") != pilihan_customer:
            st.session_state["attempt_id"] = uuid.uuid4().hex[:8]
            st.session_state["last_logged_product"] = pilihan_customer
            st.session_state["alt_pilih"] = "Best Match"
            catat_attempt(st.session_state["attempt_id"], pilihan_customer, mode,
                          [h["row"]["Nama_Lengkap"] for h in hasil])
            hitung_total_attempt.clear()

        render_status(pilihan_customer, mode)

        if not hasil:
            st.info("Belum ada alternatif dalam rentang harga ini. Coba naikkan toleransi di Pengaturan lanjutan.")
        else:
            labels = ["Best Match"] + [f"Alternative {i + 1}" for i in range(1, len(hasil))]
            if st.session_state.get("alt_pilih") not in labels:
                st.session_state["alt_pilih"] = labels[0]
            try:
                zona = st.container(key="showcase")
            except TypeError:
                zona = st.container()
            with zona:
                kiri, kanan = st.columns([2.2, 1])
                with kanan:
                    st.markdown('<div class="dp-label">SELECT</div>', unsafe_allow_html=True)
                    st.radio("Pilih alternatif", labels, key="alt_pilih", label_visibility="collapsed")
                idx = labels.index(st.session_state["alt_pilih"])
                h = hasil[idx]
                terbatas = any("belum lengkap" in t for _, t in h["alasan"])
                with kiri:
                    render_showcase(ref, h, idx, terbatas)
            render_poin(h["row"])
            render_alasan(h)
            render_script(pilihan_customer, h["row"], mode, h["selisih"])
            render_banding(ref, h["row"])
            render_outcome(st.session_state.get("attempt_id"), pilihan_customer, mode)
    except Exception as e:  # jangan tampilkan error teknis ke sales
        print("UI error:", repr(e))
        st.error("Terjadi kendala saat menampilkan rekomendasi. Coba refresh data atau pilih produk lain.")
else:
    st.session_state.pop("last_logged_product", None)
    st.markdown('<div class="dp-empty">Ketik nama HP yang dicari customer.<br>'
                '<span>Jangan berhenti di "tidak ada". Tunjukkan apa yang bisa dijual.</span></div>',
                unsafe_allow_html=True)

render_pilot()
