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

# Biru (#4DA6FF) = highlight interaktif. Merah Digiplus (#E31E24) hanya aksen kecil.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;800&display=swap');
html, body, .stApp, button, input, textarea, [class*="st-"] {font-family: 'Roboto', Arial, sans-serif !important;}
.stApp {background: radial-gradient(900px 420px at 50% -8%, rgba(77,166,255,.17), transparent 65%), linear-gradient(180deg,#050812,#080C16 55%,#0B1220); color:#F3F6FB;}
header[data-testid="stHeader"] {background: transparent;} #MainMenu, footer {visibility: hidden;}
.block-container {max-width: 1060px; padding: 2rem 1rem 4rem;}
hr, .dp-sep {border:none; height:1px; background: linear-gradient(90deg, transparent, rgba(150,200,255,.25), transparent); margin:1.2rem 0;}
.dp-top {display:flex; align-items:center; gap:.9rem;}
.dp-logo {width:42px; height:42px; border-radius:11px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.3rem;
          background: linear-gradient(145deg, rgba(77,166,255,.25), rgba(255,255,255,.04)); border:1px solid rgba(150,200,255,.3);
          box-shadow: 0 0 22px rgba(77,166,255,.25); position:relative;}
.dp-logo::after {content:""; position:absolute; right:-3px; bottom:-3px; width:9px; height:9px; border-radius:50%; background:#E31E24;}
.dp-title {font-size:2rem; font-weight:700; letter-spacing:-.01em; margin:0;}
.dp-sub {font-size:.98rem; font-weight:400; color:#B4C0D4; margin:.5rem 0 0;}
.dp-h2 {font-size:1.45rem; font-weight:500; margin:1.6rem 0 .2rem;}
.dp-it {font-style:italic; font-weight:300; color:#B4C0D4; margin-bottom:1.1rem;}
.dp-glass {background: rgba(255,255,255,.045); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
           border:1px solid rgba(150,200,255,.12); border-radius:14px; padding:1.1rem 1.25rem;
           box-shadow: 0 10px 40px rgba(0,0,0,.35), 0 0 30px rgba(80,150,255,.08);}
.dp-ch {font-size:1.02rem; font-weight:500; color:#8ED8FF; margin-bottom:.9rem;}
.dp-probe {background: rgba(176,150,60,.10); border-color: rgba(230,205,120,.20); box-shadow: 0 10px 40px rgba(0,0,0,.35), 0 0 26px rgba(200,170,70,.07);}
.dp-probe .dp-ch {color:#EBDDA0;}
.dp-pt {display:flex; gap:.6rem; margin:.1rem 0 .95rem; line-height:1.55; font-size:1rem; font-weight:400;}
.dp-script {font-style:italic; line-height:1.7; font-size:1rem; font-weight:300; color:#F5F1E4;}
.dp-reco {display:block; padding:1rem 1.25rem; border-radius:14px; backdrop-filter: blur(16px);
          background: linear-gradient(135deg, rgba(14,96,68,.55), rgba(8,52,42,.55)); border:1px solid rgba(90,225,165,.30);
          box-shadow: 0 0 34px rgba(60,200,140,.15); margin:1rem 0 1.3rem;}
.dp-rl {font-size:.74rem; letter-spacing:.2em; font-weight:500; color:#9FE8C6;}
.dp-rt {font-size:1.35rem; font-weight:700; color:#fff; margin-top:.15rem;} .dp-rs {font-size:.82rem; color:#BFE9D6; margin-top:.2rem; font-weight:300;}
.dp-ref {display:grid; grid-template-columns: repeat(3,1fr); gap:1rem; padding:.4rem 0 .6rem;}
.dp-rk {font-size:.72rem; letter-spacing:.18em; text-transform:uppercase; color:#8794AB; font-weight:500;}
.dp-rv {font-size:1.9rem; font-weight:500; color:#fff; text-shadow: 0 0 24px rgba(77,166,255,.35); margin-top:.15rem;}
.dp-alt {font-size:1.6rem; font-weight:700; margin:1.1rem 0 .25rem;} .dp-meta {color:#A9B6CB; font-size:.95rem; margin-bottom:1rem; font-weight:300;}
.dp-meta b {color:#8ED8FF; font-weight:500;}
.dp-done {border:1px solid rgba(90,225,165,.35); color:#9FE8C6; padding:.8rem 1rem; border-radius:12px; background:rgba(14,96,68,.2);}
.dp-pilot {margin-top:2.4rem;} .dp-pl {font-size:.7rem; letter-spacing:.24em; color:#8794AB;} .dp-pn2 {font-size:1.5rem; font-weight:300;} .dp-pn2 span {font-size:.72rem; letter-spacing:.18em; color:#8794AB;}
.dp-bar {height:4px; border-radius:99px; background:rgba(255,255,255,.1); margin-top:.5rem; overflow:hidden;} .dp-bar > div {height:100%; background:linear-gradient(90deg,#4DA6FF,#8FE9FF); box-shadow:0 0 10px #4DA6FF;}
/* search bar */
div[data-baseweb="select"] > div {background: rgba(255,255,255,.05) !important; border:1px solid rgba(150,200,255,.2) !important; border-radius:12px !important; min-height:3.2rem; transition: all .2s ease;}
div[data-baseweb="select"] > div:hover {border-color: rgba(143,233,255,.45) !important;}
div[data-baseweb="select"] > div:focus-within {border-color:#8FE9FF !important; box-shadow: 0 0 0 1px rgba(143,233,255,.5), 0 0 24px rgba(77,166,255,.28) !important;}
/* tabs */
.stTabs [data-baseweb="tab-list"] {gap:.3rem; overflow-x:auto; flex-wrap:nowrap; border-bottom:1px solid rgba(150,200,255,.12);}
.stTabs [data-baseweb="tab"] {background:transparent; color:#8E9BB0; height:auto; padding:.65rem 1.05rem; white-space:nowrap; border-radius:10px 10px 0 0; transition: all .2s ease;}
.stTabs [data-baseweb="tab"]:hover {color:#fff; background: rgba(77,166,255,.06);}
.stTabs [aria-selected="true"] {color:#fff !important; background: rgba(77,166,255,.11); text-shadow: 0 0 14px rgba(77,166,255,.55);}
.stTabs [data-baseweb="tab-highlight"] {background:#4DA6FF !important; height:2px !important; box-shadow:0 0 12px #4DA6FF;}
.stTabs [data-baseweb="tab-border"] {background: transparent !important;}
div.stButton > button {width:100%; min-height:3rem; border-radius:12px; background: rgba(255,255,255,.05); color:#fff; border:1px solid rgba(150,200,255,.18); transition: all .2s ease;}
div.stButton > button:hover {border-color:#4DA6FF; background: rgba(77,166,255,.12); color:#fff; box-shadow:0 0 18px rgba(77,166,255,.2);}
@media (max-width: 768px) {.dp-title {font-size:1.45rem;} .dp-rv {font-size:1.15rem;} .dp-ref {gap:.5rem;} .dp-alt {font-size:1.3rem;} .dp-reco .dp-rt {font-size:1.15rem;}}
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
    """Script jualan natural 4-7 kalimat. Hanya memakai data produk, tanpa klaim 'sama persis'."""
    kondisi = "memang belum kami jual di Digiplus" if mode == "kompetitor" else "memang sedang kosong"
    alt_nama = alt_row["Nama_Lengkap"]
    tier = clean(alt_row.get("Tier"))
    kal = [f"Kak, {ref_nama} {kondisi}."]
    kal.append(f"Tapi saya punya satu alternatif yang menarik untuk dipertimbangkan: {alt_nama}"
               + (f", di kelas {tier}." if tier else "."))
    poin = [kecil(ringkas(p)) for p in (clean(alt_row.get(f"Kelebihan_{i}")) for i in (1, 2, 3)) if p]
    if poin:
        kal.append(f"Yang menonjol, {gabung_teks(poin)}.")
    chip = clean(alt_row.get("Chipset"))
    if chip:
        kal.append(f"Dapurnya memakai {chip}.")
    target = clean(alt_row.get("Target_User"))
    if target:
        kal.append(f"Produk ini biasanya diminati {kecil(target)}.")
    if selisih < -500000:
        kal.append(f"Dari sisi harga juga lebih hemat {rp(abs(selisih))} dibanding {ref_nama}.")
    elif selisih > 500000:
        kal.append(f"Ada selisih sekitar {rp(selisih)} dari {ref_nama}, dan menurut saya sepadan untuk dipertimbangkan.")
    else:
        kal.append(f"Harganya juga berada di kisaran yang hampir sama dengan {ref_nama}.")
    kal.append("Kalau Kakak berkenan, saya bisa tunjukkan unitnya langsung supaya kita bisa bandingkan bareng-bareng.")
    return " ".join(kal)


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
# 4. UI (struktur mengikuti referensi: judul > pencarian > banner > info acuan > tab alternatif)
# ============================================
def esc(x):
    return html.escape(str(x))


def render_header():
    st.markdown(
        '<div class="dp-top"><div class="dp-logo">D</div><div class="dp-title">Digiplus Smart Sales Assistant</div></div>'
        '<div class="dp-sub">Produk kosong? Jangan Khawatir Kita Masih Bisa Jual Yang Lain!</div><div class="dp-sep"></div>',
        unsafe_allow_html=True)


def render_alternatif(ref, h, mode):
    """Isi satu tab: judul, harga+skor, kelebihan (kiri), ide probing (kanan)."""
    row = h["row"]
    nama = row["Nama_Lengkap"]
    sel = h["selisih"]
    tanda = "+" if sel > 0 else ""
    st.markdown(f'<div class="dp-alt">🎯 Alternatif: {esc(nama)}</div>'
                f'<div class="dp-meta">💰 Harga: <b>{esc(rp(row["Harga"]))}</b> ({tanda}{esc(rp(sel))} dari {esc(ref["Nama_Lengkap"])})'
                f' &nbsp;|&nbsp; 🎯 Skor Kecocokan: <b>{h["skor"]}/100</b></div>', unsafe_allow_html=True)
    kiri, kanan = st.columns(2, gap="medium")
    poin = [clean(row.get(f"Kelebihan_{i}")) for i in (1, 2, 3)]
    isi = "".join(f'<div class="dp-pt"><span>✅</span><span>{esc(p)}</span></div>' for p in poin if p) \
        or '<div class="dp-pt">Data kelebihan produk belum diisi.</div>'
    with kiri:
        st.markdown(f'<div class="dp-glass"><div class="dp-ch">📊 Kelebihan {esc(nama)}</div>{isi}</div>', unsafe_allow_html=True)
    with kanan:
        st.markdown(f'<div class="dp-glass dp-probe"><div class="dp-ch">💬 Ide Probing</div>'
                    f'<div class="dp-script">{esc(buat_script(ref["Nama_Lengkap"], row, mode, sel))}</div></div>',
                    unsafe_allow_html=True)
    if any("belum lengkap" in t for _, t in h["alasan"]):
        st.caption("Catatan: skor ini berdasarkan data yang terbatas (tier atau chipset belum lengkap).")


def render_outcome(attempt_id, produk, mode):
    st.markdown('<div class="dp-sep"></div>', unsafe_allow_html=True)
    sudah = st.session_state.get(f"outcome_{attempt_id}")
    if sudah:
        st.markdown(f'<div class="dp-done">Hasil tercatat: <b>{esc(sudah)}</b></div>', unsafe_allow_html=True)
        return
    st.caption("Hasil percakapan dengan customer (opsional)")
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
    st.markdown(f'<div class="dp-pilot"><div class="dp-pl">SWITCH-SELLING PILOT</div>'
                f'<div class="dp-pn2">{total} <span>/ {TARGET_ATTEMPTS} ATTEMPTS</span></div>'
                f'<div class="dp-bar"><div style="width:{pct:.0f}%"></div></div></div>', unsafe_allow_html=True)


# Sidebar minimal (tersembunyi): hanya sumber data dan refresh
with st.sidebar:
    st.caption(f"Sumber data produk: {sumber_data}")
    if catatan_data:
        st.warning(catatan_data)
    if get_log_sheet()[0] is None:
        st.caption("Google Sheets belum terhubung. Log disimpan sementara di file lokal.")
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

render_header()
st.markdown('<div class="dp-h2">🔎 HP apa yang sedang kosong?</div>'
            '<div class="dp-it">Biar aku bantu cariin penggantinya lengkap dengan cara jualan 😊</div>', unsafe_allow_html=True)


def search_hp(searchterm: str):
    if not searchterm:
        return pilihan_unik
    return [hp for hp in pilihan_unik if searchterm.lower() in hp.lower()]


pilihan_customer = st_searchbox(
    search_hp, label="🔎 Cari HP yang sedang kosong:", placeholder="Ketik atau pilih nama HP...",
    key="search_hp", default_options=pilihan_unik)

TOP_N = 4          # jumlah tab alternatif
TOL_RP = 2500000   # toleransi harga dasar untuk produk toko (minimal 15% dari harga)

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
        tol = max(float(TOL_RP), 0.15 * harga_ref) if mode == "toko" else 0.3 * harga_ref
        hasil = cari_alternatif(ref, df_toko, mode, tol, TOP_N, [])

        # Logging otomatis anonim: 1 attempt per pencarian (saat produk berubah)
        if st.session_state.get("last_logged_product") != pilihan_customer:
            st.session_state["attempt_id"] = uuid.uuid4().hex[:8]
            st.session_state["last_logged_product"] = pilihan_customer
            catat_attempt(st.session_state["attempt_id"], pilihan_customer, mode,
                          [h["row"]["Nama_Lengkap"] for h in hasil])
            hitung_total_attempt.clear()

        if not hasil:
            st.info("Belum ada alternatif dalam rentang harga ini. Data produk mungkin perlu dilengkapi.")
        else:
            ket = "sedang kosong di Digiplus" if mode == "toko" else "tidak dijual di Digiplus"
            st.markdown(f'<div class="dp-reco"><div class="dp-rl">🎯 REKOMENDASI SWITCH SELLING:</div>'
                        f'<div class="dp-rt">Segera alihkan ke {esc(hasil[0]["row"]["Nama_Lengkap"])}!</div>'
                        f'<div class="dp-rs">{esc(pilihan_customer)} {ket}.</div></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="dp-ref"><div><div class="dp-rk">Harga Acuan</div><div class="dp-rv">{esc(rp(harga_ref))}</div></div>'
                f'<div><div class="dp-rk">Tier</div><div class="dp-rv">{esc(clean(ref.get("Tier")) or "-")}</div></div>'
                f'<div><div class="dp-rk">Brand</div><div class="dp-rv">{esc(clean(ref.get("Brand")) or "-")}</div></div></div>'
                '<div class="dp-sep"></div>', unsafe_allow_html=True)
            tabs = st.tabs([f"📱 {h['row']['Nama_Lengkap']}" for h in hasil])
            for tab, h in zip(tabs, hasil):
                with tab:
                    render_alternatif(ref, h, mode)
            render_outcome(st.session_state.get("attempt_id"), pilihan_customer, mode)
    except Exception as e:  # jangan tampilkan error teknis ke sales
        print("UI error:", repr(e))
        st.error("Terjadi kendala saat menampilkan rekomendasi. Coba refresh data atau pilih produk lain.")
else:
    st.session_state.pop("last_logged_product", None)
    st.info("👆 Ketik atau pilih nama HP di kolom pencarian untuk mulai.")

render_pilot()
