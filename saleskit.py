import re
import csv
import os
import uuid
import html
from datetime import datetime, timezone, timedelta

import streamlit as st
import pandas as pd
from streamlit_searchbox import st_searchbox

st.set_page_config(
    page_title="Digiplus Smart Sales Assistant",
    page_icon="🔁",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================
# TAMPILAN (CSS) - ganti #6366F1 kalau mau ganti warna aksen
# ============================================
st.markdown(
    """
<style>
.block-container {padding-top: 2rem; padding-bottom: 4rem;}
.ssa-hero {border-left: 5px solid #6366F1; background: rgba(99,102,241,.12);
           border-radius: 14px; padding: 16px 18px; margin: 8px 0 12px 0;}
.ssa-label {font-size: .85rem; opacity: .75; margin-bottom: 2px;}
.ssa-name {font-size: 1.6rem; font-weight: 700; line-height: 1.25;}
.ssa-price {font-size: 1.15rem; margin-top: 6px;}
.ssa-badge {display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: .85rem; font-weight: 600; margin-left: 6px;}
.ssa-up {background: rgba(245,158,11,.2); color: #F59E0B;}
.ssa-down {background: rgba(34,197,94,.2); color: #22C55E;}
.ssa-same {background: rgba(148,163,184,.25);}
.ssa-bar {height: 10px; border-radius: 999px; background: rgba(148,163,184,.3);
          margin-top: 12px; overflow: hidden;}
.ssa-bar > div {height: 100%; background: linear-gradient(90deg, #6366F1, #22C55E);}
.ssa-score {font-size: .85rem; opacity: .8; margin-top: 4px;}
div.stButton > button {width: 100%; min-height: 3rem; border-radius: 12px;}
</style>
""",
    unsafe_allow_html=True,
)

# >>> LOGIKA (fungsi murni, tanpa Streamlit) >>>
# ============================================
# 1. BOBOT SKOR (total maksimal 100)
# ============================================
W_HARGA = 25
W_TIER = 20
W_CHIPSET = 20
W_BRAND = 5      # hanya untuk mode "toko" (produk toko kosong)
W_KEBUTUHAN = 30  # hanya dihitung kalau sales memilih prioritas customer

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
    if "tensor" in s:
        return 4.5
    if "apple" in s or re.search(r"\ba\d{2}\b", s):
        return 5
    if "helio" in s:
        return 2
    if "unisoc" in s:
        return 1.5
    return None


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

    # --- Kebutuhan customer (hanya kalau sales memilih prioritas) ---
    if prioritas:
        maks += W_KEBUTUHAN
        kuat_list = []
        for key in prioritas:
            kuat = kekuatan_prioritas(key, alt, lc_alt)
            kuat_list.append(kuat)
            nama_p = [k.split(" ", 1)[1].lower() for k, v in PRIORITAS.items() if v == key][0]
            bukti = cari_bukti(key, alt)
            if kuat >= 0.5 and bukti:
                alasan.append(("✅", f"Cocok untuk {nama_p}: {bukti}"))
            elif kuat >= 0.5:
                alasan.append(("✅", f"Cocok untuk {nama_p}"))
            else:
                alasan.append(("➖", f"Data {nama_p} belum terlalu kuat di produk ini"))
        dapat += W_KEBUTUHAN * (sum(kuat_list) / len(kuat_list))

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


def buat_script(ref_nama, alt_row, mode, prioritas_label, prioritas, selisih):
    """Return (script_buka, script_tawar): alur Acknowledge-Probe lalu Bridge-Recommend-Close."""
    kondisi = "belum kami jual" if mode == "kompetitor" else "lagi kosong"
    if prioritas_label:
        buka = (f"Oke Kak, {ref_nama} {kondisi}. Kalau saya tangkap, yang Kakak butuhkan "
                f"terutama {gabung_teks(prioritas_label)}, betul ya?")
    else:
        buka = (f"Oke Kak, {ref_nama} {kondisi}. Boleh tahu, Kakak paling butuh yang mana: "
                f"performa, baterai, atau kamera?")

    alt_nama = alt_row["Nama_Lengkap"]
    poin = poin_singkat(alt_row, prioritas)
    if prioritas_label:
        tawar = f"Kalau begitu saya rekomendasi {alt_nama}, Kak."
    else:
        tawar = f"Kalau begitu, ada {alt_nama} yang bisa jadi pilihan, Kak."
    if poin:
        tawar += f" Plusnya: {gabung_teks(poin)}."

    if selisih < -500000:
        tawar += f" Harganya malah lebih hemat {rp(abs(selisih))}."
    elif selisih > 500000:
        tawar += f" Selisihnya sekitar {rp(selisih)}, tapi spesifikasinya sepadan."
    else:
        tawar += " Harganya hampir sama, Kak."
    tawar += " Mau saya tunjukkan langsung?"
    return buka, tawar


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
    "Timestamp", "Attempt_ID", "Event", "Sales", "Produk_Dicari", "Mode",
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
        if not ws.row_values(1):
            ws.append_row(LOG_HEADER)
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


def catat_attempt(attempt_id, sales, produk, mode, nama_alt):
    alt = (list(nama_alt) + ["", "", ""])[:3]
    row = [
        datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
        attempt_id, "attempt", sales or "-", produk, mode,
        len(nama_alt), alt[0], alt[1], alt[2], "",
    ]
    return tulis_log(row)


def catat_outcome(attempt_id, sales, produk, mode, hasil):
    row = [
        datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
        attempt_id, "outcome", sales or "-", produk, mode,
        "", "", "", "", hasil,
    ]
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
# 4. SIDEBAR (progress pilot + pengaturan lanjutan)
# ============================================
with st.sidebar:
    st.markdown("### 📈 Progress Pilot")
    total_attempt = hitung_total_attempt()
    st.metric("Switch-selling attempts", f"{total_attempt} / {TARGET_ATTEMPTS}")
    st.progress(min(total_attempt / TARGET_ATTEMPTS, 1.0))

    ws_status, _ = get_log_sheet()
    if ws_status is None:
        st.caption("⚠️ Google Sheets belum terhubung, log disimpan sementara di file lokal.")
    else:
        st.caption("✅ Log tersimpan otomatis ke Google Sheets.")

    st.caption(f"📦 Sumber data produk: **{sumber_data}**")
    if catatan_data:
        st.warning(catatan_data)

    st.markdown("---")
    with st.expander("⚙️ Pengaturan lanjutan"):
        max_selisih = st.slider(
            "Toleransi selisih harga (Rp), untuk produk toko kosong:",
            min_value=500000, max_value=5000000, value=2500000, step=500000,
        )
        top_n = st.slider("Jumlah rekomendasi:", 1, 6, 3)

    if st.button("🔄 Refresh Data Sekarang"):
        st.cache_data.clear()
        st.success("✅ Data berhasil di-refresh!")
        st.rerun()

# ============================================
# 5. HEADER + INPUT
# ============================================
st.title("Digiplus Smart Sales Assistant")
st.caption("Produk kosong? Jangan khawatir, kita masih bisa jual yang lain! 🛍️")

nama_sales = st.text_input(
    "👤 Nama sales", key="nama_sales", placeholder="Isi namamu dulu, contoh: Lian"
)


def search_hp(searchterm: str):
    if not searchterm:
        return pilihan_unik
    return [hp for hp in pilihan_unik if searchterm.lower() in hp.lower()]


pilihan_customer = st_searchbox(
    search_hp,
    label="🔎 Customer cari HP apa?",
    placeholder="Ketik atau pilih nama HP...",
    key="search_hp",
    default_options=pilihan_unik,
)


def pilih_prioritas():
    opsi = list(PRIORITAS.keys())
    label = "🎯 Prioritas customer (tap yang disebut customer, boleh lebih dari satu)"
    if hasattr(st, "pills"):
        pilih = st.pills(label, opsi, selection_mode="multi", key="prioritas")
    else:
        pilih = st.multiselect(label, opsi, key="prioritas")
    pilih = pilih or []
    return [PRIORITAS[p] for p in pilih], [p.split(" ", 1)[1].lower() for p in pilih]


def hero_html(nama, harga, selisih, skor):
    if selisih > 0:
        badge = f'<span class="ssa-badge ssa-up">{html.escape(rp_selisih(selisih))}</span>'
    elif selisih < 0:
        badge = f'<span class="ssa-badge ssa-down">{html.escape(rp_selisih(selisih))} lebih hemat</span>'
    else:
        badge = '<span class="ssa-badge ssa-same">harga sama</span>'
    return (
        '<div class="ssa-hero">'
        '<div class="ssa-label">🥇 Rekomendasi utama</div>'
        f'<div class="ssa-name">{html.escape(nama)}</div>'
        f'<div class="ssa-price">{html.escape(rp(harga))} {badge}</div>'
        f'<div class="ssa-bar"><div style="width:{skor}%"></div></div>'
        f'<div class="ssa-score">Kecocokan {skor}/100</div>'
        "</div>"
    )


def tampil_script(teks):
    try:
        st.code(teks, language=None, wrap_lines=True)
    except TypeError:
        st.code(teks, language=None)


# ============================================
# 6. LOGIC UTAMA
# ============================================
if pilihan_customer:
    if pilihan_customer in pilihan_toko:
        mode = "toko"
        pool = df_toko
        ref = df_toko[df_toko["Nama_Lengkap"] == pilihan_customer].iloc[0]
    elif pilihan_customer in pilihan_kompetitor:
        mode = "kompetitor"
        pool = df_toko
        ref = df_kompetitor[df_kompetitor["Nama_Lengkap"] == pilihan_customer].iloc[0]
    else:
        st.error(f"❌ Produk **{pilihan_customer}** tidak ditemukan di database.")
        st.stop()

    if pd.isna(ref["Harga"]):
        st.error("⚠️ Harga produk ini belum diisi di Excel, jadi alternatif belum bisa dicari.")
        st.stop()

    tol = float(max_selisih) if mode == "toko" else 0.3 * float(ref["Harga"])

    # --- Logging: 1 attempt per pencarian (hanya saat produk berubah) ---
    if st.session_state.get("last_logged_product") != pilihan_customer:
        st.session_state["prioritas"] = []
        st.session_state["attempt_id"] = uuid.uuid4().hex[:8]
        st.session_state["last_logged_product"] = pilihan_customer
        awal = cari_alternatif(ref, pool, mode, tol, top_n, [])
        masuk_sheet = catat_attempt(
            st.session_state["attempt_id"], nama_sales, pilihan_customer, mode,
            [h["row"]["Nama_Lengkap"] for h in awal],
        )
        hitung_total_attempt.clear()
        st.toast("✅ Attempt tercatat" if masuk_sheet
                 else "⚠️ Tercatat di file lokal (Sheets belum terhubung)")

    if not (nama_sales or "").strip():
        st.caption("⚠️ Isi **Nama sales** di atas supaya aktivitasmu tercatat atas namamu.")

    # --- Status produk yang dicari ---
    if mode == "toko":
        st.info(f"⏳ **{pilihan_customer}** lagi kosong. Ini pilihan penggantinya:")
    else:
        st.warning(f"🚫 **{pilihan_customer}** tidak dijual di Digiplus. Tapi ada yang kebutuhannya mirip:")

    info_ref = [rp(ref["Harga"])]
    if clean(ref.get("Tier")):
        info_ref.append(clean(ref.get("Tier")))
    if clean(ref.get("Chipset")):
        info_ref.append(clean(ref.get("Chipset")))
    st.caption("Acuan: " + " • ".join(info_ref))

    # --- Prioritas customer ---
    prioritas, prioritas_label = pilih_prioritas()

    hasil = cari_alternatif(ref, pool, mode, tol, top_n, prioritas)

    if not hasil:
        st.warning(
            f"Belum ada alternatif untuk {pilihan_customer} dalam rentang harga ini. "
            "Coba naikkan toleransi di sidebar (Pengaturan lanjutan) atau tambah data produk."
        )
    else:
        utama = hasil[0]
        row_u = utama["row"]

        st.markdown(
            hero_html(row_u["Nama_Lengkap"], row_u["Harga"], utama["selisih"], utama["skor"]),
            unsafe_allow_html=True,
        )

        st.markdown("**Kenapa produk ini?**")
        for ikon, teks in utama["alasan"]:
            st.markdown(f"{ikon} {teks}")

        # --- Script siap ucap ---
        buka, tawar = buat_script(
            pilihan_customer, row_u, mode, prioritas_label, prioritas, utama["selisih"]
        )
        st.markdown("### 💬 Script siap ucap")
        st.caption("Alur: Acknowledge → Probe → Bridge → Recommend → Close. Tekan ikon copy di pojok kanan.")
        st.markdown("**1. Buka & gali kebutuhan**")
        tampil_script(buka)
        st.markdown("**2. Tawarkan alternatif**")
        tampil_script(tawar)

        # --- Perbandingan ---
        with st.expander(f"📊 Bandingkan {pilihan_customer} vs {row_u['Nama_Lengkap']}"):
            st.table(tabel_banding(ref, row_u))
            semua_poin = [clean(row_u.get(f"Kelebihan_{i}")) for i in range(1, 4)]
            for t in [t for t in semua_poin if t]:
                st.markdown(f"✅ {t}")

        # --- Alternatif lain ---
        if len(hasil) > 1:
            st.markdown("### Alternatif lain")
            for i, h in enumerate(hasil[1:], start=2):
                r = h["row"]
                judul = f"#{i}  {r['Nama_Lengkap']} • {rp(r['Harga'])} • {h['skor']}/100"
                with st.expander(judul):
                    st.caption(f"Selisih harga: {rp_selisih(h['selisih'])}")
                    for ikon, teks in h["alasan"]:
                        st.markdown(f"{ikon} {teks}")
                    _, tawar_i = buat_script(
                        pilihan_customer, r, mode, prioritas_label, prioritas, h["selisih"]
                    )
                    tampil_script(tawar_i)

        # --- Hasil percakapan ---
        st.markdown("---")
        st.markdown("#### 📝 Hasil percakapan dengan customer (opsional)")
        attempt_id = st.session_state.get("attempt_id")
        sudah_isi = st.session_state.get(f"outcome_{attempt_id}")

        if sudah_isi:
            st.success(f"Tercatat: **{sudah_isi}**. Makasih! 🙏")
        else:
            c1, c2, c3 = st.columns(3)
            pilihan_hasil = None
            if c1.button("👀 Tertarik lihat alternatif"):
                pilihan_hasil = "Tertarik lihat alternatif"
            if c2.button("🎉 Switch berhasil / terjual"):
                pilihan_hasil = "Switch berhasil"
            if c3.button("🚪 Customer tidak jadi"):
                pilihan_hasil = "Tidak jadi"

            if pilihan_hasil:
                catat_outcome(attempt_id, nama_sales, pilihan_customer, mode, pilihan_hasil)
                st.session_state[f"outcome_{attempt_id}"] = pilihan_hasil
                st.rerun()

else:
    # reset supaya produk yang sama bisa dicari lagi dan dihitung sebagai attempt baru
    st.session_state.pop("last_logged_product", None)
    st.info("👆 Ketik atau pilih nama HP di kolom pencarian untuk mulai.")
    if not df_kompetitor.empty:
        st.caption(
            f"💡 Database: **{len(pilihan_toko)}** produk toko + "
            f"**{len(pilihan_kompetitor)}** produk kompetitor"
        )
