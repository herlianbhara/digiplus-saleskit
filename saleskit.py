import re
import csv
import os
import uuid
import html
from datetime import datetime, timezone, timedelta

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from streamlit_searchbox import st_searchbox

st.set_page_config(
    page_title="Digiplus Smart Sales Assistant",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================
# SPLASH SCREEN — cinematic intro (sekali per session)
# ============================================
SPLASH_DURATION_MS = 2600


def show_splash():
    if st.session_state.get("_splash_shown"):
        return
    st.session_state["_splash_shown"] = True
    dur = SPLASH_DURATION_MS
    components.html(f"""
    <script>
    (function() {{
        try {{
            const doc = window.parent.document;

            const oldStyle = doc.getElementById('dp-splash-style');
            if (oldStyle) oldStyle.remove();
            const oldSplash = doc.getElementById('dp-splash');
            if (oldSplash) oldSplash.remove();

            const style = doc.createElement('style');
            style.id = 'dp-splash-style';
            style.textContent = `
                #dp-splash {{
                    position: fixed !important;
                    inset: 0 !important;
                    z-index: 999999 !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    background:
                        radial-gradient(900px 420px at 50% 40%, rgba(77,166,255,.15), transparent 65%),
                        radial-gradient(700px 320px at 50% 60%, rgba(142,216,255,.06), transparent 70%),
                        linear-gradient(180deg, #050812, #080C16 55%, #0B1220) !important;
                    color: #F3F6FB !important;
                    font-family: 'Roboto', Arial, sans-serif !important;
                    animation: dp-splash-in 0.4s ease-out both !important;
                    pointer-events: all !important;
                }}
                #dp-splash.dp-out {{
                    animation: dp-splash-out 0.5s ease-in forwards !important;
                    pointer-events: none !important;
                }}
                #dp-splash .dp-sp-inner {{
                    text-align: center;
                    max-width: 560px;
                    padding: 2rem;
                }}
                #dp-splash .dp-sp-logo {{
                    width: 76px; height: 76px;
                    margin: 0 auto 1.6rem;
                    border-radius: 20px;
                    display: flex; align-items: center; justify-content: center;
                    color: #FFFFFF;
                    background: linear-gradient(145deg, rgba(77,166,255,.32), rgba(255,255,255,.06));
                    border: 1px solid rgba(142,216,255,.38);
                    box-shadow: 0 0 50px rgba(77,166,255,.45), inset 0 1px 0 rgba(255,255,255,.10);
                    position: relative;
                    animation: dp-sp-logo 0.75s cubic-bezier(.2,.8,.2,1) 0.1s both;
                }}
                #dp-splash .dp-sp-logo::after {{
                    content: "";
                    position: absolute;
                    right: -4px; bottom: -4px;
                    width: 14px; height: 14px;
                    border-radius: 50%;
                    background: #E31E24;
                    box-shadow: 0 0 14px rgba(227,30,36,.65);
                }}
                #dp-splash .dp-sp-logo svg {{
                    width: 68%; height: 68%;
                    display: block;
                    filter: drop-shadow(0 0 8px rgba(142,216,255,.6));
                }}
                #dp-splash .dp-sp-eyebrow {{
                    font-size: .7rem;
                    letter-spacing: .38em;
                    color: #8ED8FF;
                    text-transform: uppercase;
                    font-weight: 600;
                    opacity: 0;
                    animation: dp-sp-up 0.55s ease-out 0.45s both;
                }}
                #dp-splash .dp-sp-title {{
                    font-size: 2.1rem;
                    font-weight: 800;
                    color: #FFFFFF;
                    margin-top: .65rem;
                    letter-spacing: -.02em;
                    line-height: 1.2;
                    opacity: 0;
                    animation: dp-sp-up 0.55s ease-out 0.65s both;
                }}
                #dp-splash .dp-sp-line {{
                    width: 90px; height: 1px;
                    margin: 1.5rem auto;
                    background: linear-gradient(90deg, transparent, #4DA6FF, transparent);
                    box-shadow: 0 0 14px #4DA6FF;
                    opacity: 0;
                    animation: dp-sp-up 0.55s ease-out 0.85s both;
                }}
                #dp-splash .dp-sp-tag {{
                    font-size: .92rem;
                    font-style: italic;
                    color: #B4C0D4;
                    opacity: 0;
                    animation: dp-sp-up 0.55s ease-out 1.05s both;
                }}
                #dp-splash .dp-sp-credit {{
                    margin-top: .55rem;
                    font-size: .78rem;
                    color: #8E9BB0;
                    letter-spacing: .02em;
                    opacity: 0;
                    animation: dp-sp-up 0.55s ease-out 1.25s both;
                }}
                #dp-splash .dp-sp-credit b {{
                    color: #E8EEF8;
                    font-weight: 600;
                }}
                #dp-splash .dp-sp-dots {{
                    margin-top: 2.2rem;
                    display: flex;
                    gap: .4rem;
                    justify-content: center;
                    opacity: 0;
                    animation: dp-sp-up 0.55s ease-out 1.45s both;
                }}
                #dp-splash .dp-sp-dot {{
                    width: 6px; height: 6px;
                    border-radius: 50%;
                    background: rgba(142,216,255,.35);
                    animation: dp-sp-pulse 1.2s ease-in-out infinite;
                }}
                #dp-splash .dp-sp-dot:nth-child(2) {{ animation-delay: .15s; }}
                #dp-splash .dp-sp-dot:nth-child(3) {{ animation-delay: .3s; }}
                @keyframes dp-splash-in {{
                    from {{ opacity: 0; }}
                    to {{ opacity: 1; }}
                }}
                @keyframes dp-splash-out {{
                    from {{ opacity: 1; }}
                    to {{ opacity: 0; }}
                }}
                @keyframes dp-sp-logo {{
                    from {{ opacity: 0; transform: scale(0.65); }}
                    to {{ opacity: 1; transform: scale(1); }}
                }}
                @keyframes dp-sp-up {{
                    from {{ opacity: 0; transform: translateY(10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                @keyframes dp-sp-pulse {{
                    0%, 100% {{ opacity: .35; transform: scale(1); }}
                    50% {{ opacity: 1; transform: scale(1.3); background: #8ED8FF; }}
                }}
            `;
            doc.head.appendChild(style);

            const splash = doc.createElement('div');
            splash.id = 'dp-splash';
            splash.innerHTML = `
                <div class="dp-sp-inner">
                    <div class="dp-sp-logo">
                        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="dpScreen" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#8FE9FF"/>
                                    <stop offset="100%" stop-color="#4DA6FF"/>
                                </linearGradient>
                                <linearGradient id="dpBody" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" stop-color="#FFFFFF"/>
                                    <stop offset="100%" stop-color="#B4DDFF"/>
                                </linearGradient>
                            </defs>

                            <rect x="24" y="6" width="52" height="88" rx="10" ry="10"
                                  fill="url(#dpBody)"/>

                            <rect x="28" y="16" width="44" height="66" rx="6" ry="6"
                                  fill="#0A1424"/>

                            <rect x="32" y="20" width="36" height="58" rx="4" ry="4"
                                  fill="url(#dpScreen)" opacity="0.85"/>

                            <line x1="44" y1="11" x2="56" y2="11"
                                  stroke="#0A1424" stroke-width="2" stroke-linecap="round"/>

                            <circle cx="50" cy="88" r="3.5"
                                    fill="#0A1424" stroke="rgba(142,216,255,.6)" stroke-width="0.8"/>
                        </svg>
                    </div>
                    <div class="dp-sp-eyebrow">DIGIPLUS · MAPTECH</div>
                    <div class="dp-sp-title">Smart Sales Assistant</div>
                    <div class="dp-sp-line"></div>
                    <div class="dp-sp-tag">From "We don't have it" → "Here's what we have."</div>
                    <div class="dp-sp-credit">created by <b>Herlian Bhara</b></div>
                    <div class="dp-sp-dots">
                        <div class="dp-sp-dot"></div>
                        <div class="dp-sp-dot"></div>
                        <div class="dp-sp-dot"></div>
                    </div>
                </div>
            `;
            doc.body.appendChild(splash);

            setTimeout(() => {{
                splash.classList.add('dp-out');
                setTimeout(() => {{
                    try {{ splash.remove(); }} catch (e) {{}}
                }}, 550);
            }}, {dur});
        }} catch (err) {{
            console.warn('Splash error:', err);
        }}
    }})();
    </script>
    """, height=0, scrolling=False)


show_splash()


# ============================================
# CSS — Glacier / Frosted Glass / Ice Blue
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;800;900&display=swap');

html, body, .stApp, button, input, textarea, [class*="st-"] {
    font-family: 'Roboto', Arial, sans-serif !important;
}

/* ============ LOCK HORIZONTAL SCROLL ============ */
html, body {
    overflow-x: hidden;
    overflow-x: clip !important;
    overflow-y: visible !important;
    max-width: 100vw;
}
.stApp {
    overflow-x: hidden;
    overflow-x: clip !important;
    max-width: 100vw;
}
[data-testid="stAppViewContainer"] {
    overflow-x: hidden;
    overflow-x: clip !important;
}
[data-testid="stMain"] {
    overflow-x: hidden;
    overflow-x: clip !important;
}
.block-container {
    overflow-x: clip;
    max-width: 100%;
}
section.main {
    overflow-x: clip !important;
}

/* ============ HIDE STREAMLIT CHROME ============ */
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stAppDeployButton"] { display: none !important; }
[data-testid="manage-app-button"] { display: none !important; }
.stDeployButton { display: none !important; }
[class*="viewerBadge"] { display: none !important; }
[class*="ViewerBadge"] { display: none !important; }
#MainMenu { visibility: hidden; display: none !important; }
footer { visibility: hidden; display: none !important; }
[data-testid="stToolbarActions"] { display: none !important; }

/* ============ BASE ============ */
.stApp {
    background:
        radial-gradient(900px 420px at 50% -10%, rgba(77,166,255,.10), transparent 65%),
        radial-gradient(700px 320px at 50% -5%, rgba(142,216,255,.05), transparent 70%),
        linear-gradient(180deg, #050812, #080C16 55%, #0B1220);
    color: #F3F6FB;
}
.block-container { max-width: 1060px; padding: 1rem 1rem 4rem; }

hr, .dp-sep {
    border: none; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(150,200,255,.22), transparent);
    margin: 1.2rem 0;
}

/* ============ HEADER ============ */
.dp-head { text-align: center; padding: 2.2rem 0 1rem; }
.dp-title {
    font-size: 2.1rem; font-weight: 700; letter-spacing: -.01em;
    margin: 0; color: #FFFFFF; line-height: 1.25;
}
.dp-sub {
    font-size: 1rem; font-weight: 400; color: #B4C0D4;
    margin: .75rem auto 0; max-width: 620px; line-height: 1.55;
}
.dp-sub-part2 {
    display: inline-block;
    font-size: .95rem;
    opacity: .92;
    margin-top: .15rem;
}
.dp-sep { margin: 1.6rem 0 1.4rem; }

/* ============ SECTION HEADINGS ============ */
.dp-h2 { font-size: 1.45rem; font-weight: 600; margin: 1.6rem 0 .2rem; color: #FFFFFF; }
.dp-it { font-style: italic; font-weight: 300; color: #B4C0D4; margin-bottom: 1.1rem; }

/* ============ GLASS CARDS ============ */
.dp-glass {
    background: rgba(255,255,255,.035);
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(142,216,255,.12);
    border-radius: 14px; padding: 1.1rem 1.25rem;
    box-shadow: 0 12px 40px rgba(0,0,0,.30), 0 0 30px rgba(80,150,255,.05);
}
.dp-ch { font-size: 1.02rem; font-weight: 500; color: #8ED8FF; margin-bottom: .9rem; }
.dp-probe { background: rgba(20,45,75,.35); border-color: rgba(142,216,255,.18); }
.dp-probe .dp-ch { color: #8ED8FF; }
.dp-pt {
    display: flex; gap: .6rem; margin: .1rem 0 .95rem;
    line-height: 1.55; font-size: 1rem; font-weight: 400; color: #E8EEF8;
}
.dp-script {
    font-style: italic; line-height: 1.7; font-size: 1rem;
    font-weight: 300; color: #E8EEF8;
    word-break: break-word;
    overflow-wrap: anywhere;
}

/* ============ RECOMMENDATION CARD ============ */
.dp-reco {
    display: block; padding: 1rem 1.25rem; border-radius: 14px;
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    background: linear-gradient(135deg, rgba(20,45,75,0.90), rgba(8,22,42,0.95));
    border: 1px solid rgba(142,216,255,0.35);
    box-shadow: 0 0 35px rgba(77,166,255,0.15);
    margin: 1rem 0 1.3rem;
    transition: all .3s ease;
}
.dp-rl { font-size: .74rem; letter-spacing: .2em; font-weight: 600; color: #8ED8FF; }
.dp-rt {
    font-size: 1.35rem; font-weight: 700; color: #FFFFFF; margin-top: .15rem;
    word-break: break-word; overflow-wrap: anywhere;
}
.dp-rs { font-size: .82rem; color: #9AA6B8; margin-top: .2rem; font-weight: 300; }

/* ============ REFERENCE STRIP ============ */
.dp-ref {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem; padding: .4rem 0 .6rem;
}
.dp-rk {
    font-size: .72rem; letter-spacing: .18em; text-transform: uppercase;
    color: #8794AB; font-weight: 500;
}
.dp-rv {
    font-size: 1.9rem; font-weight: 500; color: #FFFFFF;
    text-shadow: 0 0 24px rgba(77,166,255,.30); margin-top: .15rem;
    word-break: break-word; overflow-wrap: anywhere;
}

/* ============ ALTERNATIVE HEADER ============ */
.dp-alt {
    font-size: 1.6rem; font-weight: 700; margin: 1.1rem 0 .25rem; color: #FFFFFF;
    word-break: break-word; overflow-wrap: anywhere;
}
.dp-meta { color: #A9B6CB; font-size: .95rem; margin-bottom: .4rem; font-weight: 300; }
.dp-meta b { color: #8ED8FF; font-weight: 500; }
.dp-why {
    font-size: .85rem; color: #8E9BB0; margin: 0 0 1rem;
    font-weight: 300; line-height: 1.55;
}
.dp-why b { color: #8ED8FF; font-weight: 500; }

/* ============ OUTCOME ============ */
.dp-done {
    border: 1px solid rgba(142,216,255,.35); color: #8ED8FF;
    padding: .8rem 1rem; border-radius: 12px; background: rgba(20,45,75,.25);
}
.dp-ask { margin: .4rem 0 1rem; }
.dp-ask-title { font-size: 1rem; font-weight: 500; color: #E8EEF8; margin-bottom: .2rem; }
.dp-ask-sub { font-size: .85rem; font-weight: 300; color: #8E9BB0; font-style: italic; }

/* ============ PILOT ============ */
.dp-pilot { margin-top: 2.4rem; }
.dp-pl { font-size: .7rem; letter-spacing: .24em; color: #8794AB; }
.dp-pn2 { font-size: 1.5rem; font-weight: 300; color: #FFFFFF; }
.dp-pn2 span { font-size: .72rem; letter-spacing: .18em; color: #8794AB; }
.dp-bar {
    height: 4px; border-radius: 99px; background: rgba(255,255,255,.10);
    margin-top: .5rem; overflow: hidden;
}
.dp-bar > div {
    height: 100%;
    background: linear-gradient(90deg, #4DA6FF, #8FE9FF);
    box-shadow: 0 0 10px #4DA6FF;
}

/* ============ SEARCH (searchbox) ============ */
div[data-baseweb="select"] > div {
    background: rgba(20,32,52,.55) !important;
    border: 1px solid rgba(142,216,255,.20) !important;
    border-radius: 12px !important;
    min-height: 3.2rem;
    transition: all .2s ease;
}
div[data-baseweb="select"] > div:hover { border-color: rgba(143,233,255,.45) !important; }
div[data-baseweb="select"] > div:focus-within {
    border-color: #8FE9FF !important;
    box-shadow: 0 0 0 1px rgba(143,233,255,.5), 0 0 24px rgba(77,166,255,.28) !important;
}

/* ============ HIDE RADIO BULATAN ============ */
[data-testid="stRadio"] label > div:first-child,
[data-testid="stRadio"] label > div[role="presentation"],
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
[data-testid="stRadio"] [data-baseweb="radio"] > div[role="presentation"],
[data-testid="stRadio"] label input[type="radio"],
[data-testid="stRadio"] label [data-testid="stMarkdownContainer"] ~ div {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    position: absolute !important;
    left: -9999px !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* ============ RADIO AS TABS ============ */
[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: .3rem !important;
    overflow-x: auto;
    padding: 0 0 .5rem 0;
    border-bottom: 1px solid rgba(150,200,255,.12);
    margin-bottom: 1.2rem;
    scrollbar-width: thin;
    max-width: 100% !important;
    box-sizing: border-box;
}
[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar { height: 4px; }
[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar-thumb {
    background: rgba(142,216,255,.2); border-radius: 2px;
}
[data-testid="stRadio"] label {
    background: transparent !important;
    color: #8E9BB0 !important;
    padding: .65rem 1.05rem !important;
    white-space: nowrap;
    border-radius: 10px 10px 0 0;
    transition: all .2s ease;
    cursor: pointer;
    margin: 0 !important;
    border: none !important;
    min-height: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0 !important;
}
[data-testid="stRadio"] label:hover {
    color: #FFFFFF !important;
    background: rgba(77,166,255,.06) !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    color: #FFFFFF !important;
    background: rgba(77,166,255,.11) !important;
    text-shadow: 0 0 14px rgba(77,166,255,.55);
    box-shadow: inset 0 -2px 0 #4DA6FF, 0 0 12px rgba(77,166,255,.25);
}
[data-testid="stRadio"] label p {
    font-size: .9rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
}
[data-testid="stRadio"] > label:first-child { display: none !important; }

/* ============ BUTTONS ============ */
div.stButton > button {
    width: 100%; min-height: 3rem; border-radius: 12px;
    background: rgba(255,255,255,.05); color: #FFFFFF;
    border: 1px solid rgba(150,200,255,.18);
    transition: all .2s ease; font-weight: 500;
    word-break: break-word;
}
div.stButton > button:hover {
    border-color: #4DA6FF;
    background: rgba(77,166,255,.12);
    color: #FFFFFF;
    box-shadow: 0 0 18px rgba(77,166,255,.20);
}

/* ============ MOBILE ============ */
@media (max-width: 768px) {
    .block-container { padding: 0.5rem 0.9rem 4rem; }
    .dp-head { padding: 1.4rem 0 0.8rem; }
    .dp-title { font-size: 1.5rem; }
    .dp-sub { font-size: .92rem; margin-top: .5rem; }
    .dp-sub-part2 { font-size: .88rem; }
    .dp-ref {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .5rem;
    }
    .dp-rv { font-size: 1rem; word-break: break-word; overflow-wrap: anywhere; }
    .dp-rt { word-break: break-word; overflow-wrap: anywhere; }
    .dp-alt { font-size: 1.3rem; }
    .dp-reco .dp-rt { font-size: 1.15rem; }
    [data-testid="stRadio"] label { padding: .55rem .85rem !important; }
    [data-testid="stRadio"] label p { font-size: .82rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ============================================
# JS SAFETY NET — reset scroll
# ============================================
components.html("""
<script>
(function() {
    const doc = window.parent.document;
    const resetScroll = () => {
        const targets = [
            doc.documentElement,
            doc.body,
            doc.querySelector('.stApp'),
            doc.querySelector('[data-testid="stAppViewContainer"]'),
            doc.querySelector('[data-testid="stMain"]'),
            doc.querySelector('[data-testid="stVerticalBlock"]')
        ];
        targets.forEach(el => {
            if (el) {
                el.scrollLeft = 0;
                el.scrollTo && el.scrollTo({ left: 0, behavior: 'instant' });
            }
        });
    };
    resetScroll();
    doc.addEventListener('click', (e) => {
        if (e.target && e.target.closest && e.target.closest('[data-testid="stRadio"]')) {
            setTimeout(resetScroll, 30);
            setTimeout(resetScroll, 150);
            setTimeout(resetScroll, 400);
        }
    }, true);
    doc.addEventListener('scroll', (e) => {
        if (e.target === doc.documentElement || e.target === doc.body) {
            resetScroll();
        }
    }, true);
    const observer = new MutationObserver(() => resetScroll());
    observer.observe(doc.body, { childList: true, subtree: false });
})();
</script>
""", height=0)


# ============================================
# 0. OVERRIDE KHUSUS
# ============================================
OVERRIDE_TOP = {
    "Poco X8 5G": "Xiaomi Redmi Note 17 Pro 5G",
}


# ============================================
# 1. BOBOT SKOR
# ============================================
W_HARGA = 25
W_TIER = 15
W_CHIPSET = 20
W_BENTUK = 20
W_BRAND = 5
W_POSISI = 10


def clean(v):
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


def hitung_kecocokan(ref, alt, mode, tol):
    dapat, maks, alasan = 0.0, 0, []

    selisih = float(alt["Harga"]) - float(ref["Harga"])
    maks += W_HARGA
    p = W_HARGA * max(0.0, 1 - abs(selisih) / tol) if tol > 0 else 0.0
    dapat += p
    if p >= 0.6 * W_HARGA:
        alasan.append(("✅", f"Harga dekat, selisih {rp_selisih(selisih)}"))
    else:
        alasan.append(("➖", f"Selisih harga cukup jauh ({rp_selisih(selisih)})"))

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

    if mode == "toko":
        maks += W_BRAND
        if str(alt.get("Brand")) == str(ref.get("Brand")):
            dapat += W_BRAND
            alasan.append(("✅", f"Brand sama ({alt.get('Brand')})"))

    lipat_ref = adalah_lipat(ref.get("Nama_Lengkap"))
    lipat_alt = adalah_lipat(alt.get("Nama_Lengkap"))
    if lipat_ref or lipat_alt:
        maks += W_BENTUK
        if lipat_ref == lipat_alt:
            dapat += W_BENTUK
            alasan.append(("✅", "Sama-sama HP lipat"))
        else:
            alasan.append(("➖", "Bentuk berbeda (HP lipat vs HP biasa)"))

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


def cari_alternatif(ref, pool, mode, tol, top_n):
    kandidat = pool[pool["Nama_Lengkap"] != ref["Nama_Lengkap"]]
    hasil = []
    for _, row in kandidat.iterrows():
        try:
            sel = float(row["Harga"]) - float(ref["Harga"])
        except (TypeError, ValueError):
            continue
        if pd.isna(sel) or abs(sel) > tol:
            continue
        h = hitung_kecocokan(ref, row, mode, tol)
        h["row"] = row
        hasil.append(h)
    hasil.sort(key=lambda x: (-x["skor"], abs(x["selisih"])))
    return hasil[:top_n]


def gabung_teks(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " dan " + items[-1]


def kecil(t):
    return t if len(t) < 2 or t[1].isupper() else t[0].lower() + t[1:]


def buat_script(ref_nama, alt_row, mode, selisih, h=None):
    kondisi = ("memang sedang kosong di Digiplus" if mode == "toko"
               else "memang belum kami jual di Digiplus")
    alt_nama = alt_row["Nama_Lengkap"]
    tier = clean(alt_row.get("Tier"))
    target = clean(alt_row.get("Target_User"))
    chip = clean(alt_row.get("Chipset"))
    poin = [clean(alt_row.get(f"Kelebihan_{i}")) for i in (1, 2, 3)]
    poin = [p for p in poin if p]

    kal = [f"Kak, {ref_nama} {kondisi}."]

    if target:
        target_ringkas = target.split(",")[0].strip().lower()
        kal.append(
            f"Kalau Kakak sedang cari HP untuk {target_ringkas}, "
            "saya punya satu alternatif menarik untuk dipertimbangkan."
        )
    else:
        kal.append("Tapi saya punya satu alternatif menarik untuk dipertimbangkan.")

    rekom = f"Produknya {alt_nama}"
    if tier:
        rekom += f", di kelas {tier}"
    kal.append(rekom + ".")

    if poin:
        kal.append(f"Yang menonjol, {gabung_teks([kecil(ringkas(p)) for p in poin])}.")

    spec_match = []
    chip_match = False
    if h:
        for ikon, teks in h.get("alasan", []):
            if ikon != "✅":
                continue
            tl = teks.lower()
            if "chipset" in tl:
                spec_match.append(kecil(teks))
                chip_match = True
            elif "tier sama" in tl:
                spec_match.append(kecil(teks))

    if chip_match and spec_match:
        kal.append(
            f"Kebetulan spesifikasi intinya juga sejalan — {gabung_teks(spec_match[:2])}. "
            "Jadi dari sisi kebutuhan, tidak jauh berbeda dengan yang Kakak cari."
        )
    elif spec_match:
        kal.append(
            f"Menariknya, {gabung_teks(spec_match[:2])} — "
            "jadi secara kelas produk, sepadan dengan yang Kakak cari."
        )
    elif chip:
        kal.append(f"Dari sisi prosesor, produk ini pakai {chip}.")

    if selisih < -500000:
        kal.append(
            f"Bahkan harganya lebih hemat {rp(abs(selisih))} dibanding {ref_nama}, "
            "jadi Kakak dapat spesifikasi yang sepadan dengan harga lebih ringan."
        )
    elif selisih > 500000:
        kal.append(
            f"Memang ada selisih sekitar {rp(selisih)} dari {ref_nama}, "
            "tapi tambahan itu sepadan dengan peningkatan yang Kakak dapat, "
            "bukan sekadar beda harga."
        )
    else:
        kal.append(
            f"Harganya di kisaran yang sama dengan {ref_nama}, "
            "jadi tidak ada trade-off harga yang perlu dipikirkan."
        )

    kal.append(
        "Kalau Kakak berkenan, saya bisa tunjukkan unitnya langsung "
        "supaya bisa kita bandingkan bareng-bareng."
    )
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


# ============================================
# 2. LOGGING
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
SKIP_SHEETS = ["Panduan", "Master", "Notes", "Template", "Sheet1", "Log"]


def baca_worksheet(ws):
    nilai = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    if len(nilai) < 2:
        return pd.DataFrame()
    header = [str(h).strip() for h in nilai[0]]
    lebar = len(header)
    baris = [(list(r) + [""] * (lebar - len(r)))[:lebar] for r in nilai[1:]]
    df = pd.DataFrame(baris, columns=header)
    return df.replace("", pd.NA)


def susun_data(sheets_dict):
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


@st.cache_resource
def get_data_book():
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
    catatan = None
    book, err = get_data_book()
    if book is not None:
        try:
            sheets = {ws.title: baca_worksheet(ws) for ws in book.worksheets()}
            df_toko, df_komp = susun_data(sheets)
            return df_toko, df_komp, "Google Sheets", None
        except ValueError:
            catatan = ("Google Sheets belum berisi data produk. "
                       "Sementara memakai data_hp.xlsx.")
        except Exception as e:
            catatan = (f"Gagal membaca Google Sheets ({e}). "
                       "Sementara memakai data_hp.xlsx, harga bisa jadi bukan yang terbaru.")
    sheets_dict = pd.read_excel("data_hp.xlsx", sheet_name=None)
    df_toko, df_komp = susun_data(sheets_dict)
    return df_toko, df_komp, "Excel (data_hp.xlsx)", catatan


try:
    df_toko, df_kompetitor, sumber_data, catatan_data = load_data()
except FileNotFoundError:
    st.error("⚠️ Data produk tidak ditemukan. Isi tab produk di Google Sheets atau upload data_hp.xlsx.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error baca data: {e}")
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
# 4. UI RENDERERS
# ============================================
def esc(x):
    return html.escape(str(x))


def render_header():
    st.markdown(
        '<div class="dp-head">'
        '<div class="dp-title">Digiplus Smart Sales Assistant</div>'
        '<div class="dp-sub">Produk kosong?<br>'
        '<span class="dp-sub-part2">Jangan Khawatir Kita Masih Bisa Jual Yang Lain!</span>'
        '</div>'
        '</div>'
        '<div class="dp-sep"></div>',
        unsafe_allow_html=True,
    )


def render_alternatif(ref, h, mode):
    row = h["row"]
    nama = row["Nama_Lengkap"]
    sel = h["selisih"]
    tanda = "+" if sel > 0 else ""

    st.markdown(
        f'<div class="dp-alt">🎯 Alternatif: {esc(nama)}</div>'
        f'<div class="dp-meta">💰 Harga: <b>{esc(rp(row["Harga"]))}</b> '
        f'({tanda}{esc(rp(sel))} dari {esc(ref["Nama_Lengkap"])})'
        f' &nbsp;|&nbsp; 🎯 Skor Kecocokan: <b>{h["skor"]}/100</b></div>',
        unsafe_allow_html=True,
    )

    alasan_plus = [t for ik, t in h["alasan"] if ik == "✅"]
    if alasan_plus:
        st.markdown(
            f'<div class="dp-why">💡 <b>Kenapa direkomendasikan:</b> '
            f'{" · ".join(esc(t) for t in alasan_plus[:3])}</div>',
            unsafe_allow_html=True,
        )

    kiri, kanan = st.columns(2, gap="medium")

    poin = [clean(row.get(f"Kelebihan_{i}")) for i in (1, 2, 3)]
    isi = "".join(
        f'<div class="dp-pt"><span>✅</span><span>{esc(p)}</span></div>' for p in poin if p
    ) or '<div class="dp-pt">Data kelebihan produk belum diisi.</div>'

    with kiri:
        st.markdown(
            f'<div class="dp-glass"><div class="dp-ch">📊 Kelebihan {esc(nama)}</div>{isi}</div>',
            unsafe_allow_html=True,
        )
    with kanan:
        script = buat_script(ref["Nama_Lengkap"], row, mode, sel, h)
        st.markdown(
            f'<div class="dp-glass dp-probe">'
            f'<div class="dp-ch">💬 Ide Probing</div>'
            f'<div class="dp-script">{esc(script)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if any("belum lengkap" in t for _, t in h["alasan"]):
        st.caption("Catatan: skor berdasarkan data terbatas (tier atau chipset belum lengkap).")


def render_outcome(attempt_id, produk, mode):
    st.markdown('<div class="dp-sep"></div>', unsafe_allow_html=True)
    sudah = st.session_state.get(f"outcome_{attempt_id}")
    if sudah:
        st.markdown(
            f'<div class="dp-done">✅ Hasil tercatat: <b>{esc(sudah)}</b></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="dp-ask">'
        '<div class="dp-ask-title">📝 Hasil percakapan dengan customer</div>'
        '<div class="dp-ask-sub">Tolong isi hasilnya untuk perbaikan kami ke depannya 🙏</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    pilihan = None
    if c1.button("🤔 Tertarik, tapi masih ragu", key="o1", use_container_width=True):
        pilihan = "Tertarik namun masih ragu"
    if c2.button("🎉 Berhasil menjual", key="o2", use_container_width=True):
        pilihan = "Berhasil menjual"
    if c3.button("😔 Belum berhasil", key="o3", use_container_width=True):
        pilihan = "Belum berhasil"

    if pilihan:
        catat_outcome(attempt_id, produk, mode, pilihan)
        st.session_state[f"outcome_{attempt_id}"] = pilihan
        st.rerun()


def render_pilot():
    total = hitung_total_attempt()
    pct = min(100, total / TARGET_ATTEMPTS * 100)
    st.markdown(
        f'<div class="dp-pilot">'
        f'<div class="dp-pl">SWITCH-SELLING PILOT</div>'
        f'<div class="dp-pn2">{total} <span>/ {TARGET_ATTEMPTS} ATTEMPTS</span></div>'
        f'<div class="dp-bar"><div style="width:{pct:.0f}%"></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================
# 5. SIDEBAR
# ============================================
with st.sidebar:
    st.caption(f"Sumber data produk: {sumber_data}")
    if catatan_data:
        st.warning(catatan_data)
    if get_log_sheet()[0] is None:
        st.caption("Google Sheets belum terhubung. Log disimpan sementara di file lokal.")
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()


# ============================================
# 6. HEADER + SEARCH
# ============================================
render_header()
st.markdown(
    '<div class="dp-h2">🔎 HP apa yang sedang kosong?</div>'
    '<div class="dp-it">Biar aku bantu cariin penggantinya lengkap dengan cara jualan 😊</div>',
    unsafe_allow_html=True,
)


def search_hp(searchterm: str):
    if not searchterm:
        return pilihan_unik
    return [hp for hp in pilihan_unik if searchterm.lower() in hp.lower()]


pilihan_customer = st_searchbox(
    search_hp,
    label="🔎 Cari HP yang sedang kosong:",
    placeholder="Ketik atau pilih nama HP...",
    key="search_hp",
    default_options=pilihan_unik,
)

TOP_N = 4
TOL_RP = 2500000


# ============================================
# 7. LOGIC UTAMA
# ============================================
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
        hasil = cari_alternatif(ref, df_toko, mode, tol, TOP_N)

        if st.session_state.get("last_logged_product") != pilihan_customer:
            st.session_state["attempt_id"] = uuid.uuid4().hex[:8]
            st.session_state["last_logged_product"] = pilihan_customer
            catat_attempt(
                st.session_state["attempt_id"], pilihan_customer, mode,
                [h["row"]["Nama_Lengkap"] for h in hasil],
            )
            hitung_total_attempt.clear()

        if not hasil:
            st.info("Belum ada alternatif dalam rentang harga ini. Data produk mungkin perlu dilengkapi.")
        else:
            target_override = OVERRIDE_TOP.get(pilihan_customer)
            if target_override:
                for i, h in enumerate(hasil):
                    if h["row"]["Nama_Lengkap"] == target_override and i > 0:
                        hasil.insert(0, hasil.pop(i))
                        break

            ss_key = f"selected_alt_{pilihan_customer}"
            radio_key = f"radio_{pilihan_customer}"

            if radio_key in st.session_state:
                label_dipilih = st.session_state[radio_key]
                for i, h in enumerate(hasil):
                    if f"📱 {h['row']['Nama_Lengkap']}" == label_dipilih:
                        st.session_state[ss_key] = i
                        break

            if ss_key not in st.session_state:
                st.session_state[ss_key] = 0

            idx = min(st.session_state.get(ss_key, 0), len(hasil) - 1)
            if idx < 0:
                idx = 0
            st.session_state[ss_key] = idx
            h_selected = hasil[idx]

            ket = "sedang kosong di Digiplus" if mode == "toko" else "tidak dijual di Digiplus"
            st.markdown(
                f'<div class="dp-reco">'
                f'<div class="dp-rl">🎯 REKOMENDASI SWITCH SELLING</div>'
                f'<div class="dp-rt">Segera alihkan ke {esc(h_selected["row"]["Nama_Lengkap"])}!</div>'
                f'<div class="dp-rs">{esc(pilihan_customer)} {ket}.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="dp-ref">'
                f'<div><div class="dp-rk">Harga Acuan</div>'
                f'<div class="dp-rv">{esc(rp(harga_ref))}</div></div>'
                f'<div><div class="dp-rk">Tier</div>'
                f'<div class="dp-rv">{esc(clean(ref.get("Tier")) or "-")}</div></div>'
                f'<div><div class="dp-rk">Brand</div>'
                f'<div class="dp-rv">{esc(clean(ref.get("Brand")) or "-")}</div></div>'
                f'</div>'
                '<div class="dp-sep"></div>',
                unsafe_allow_html=True,
            )

            labels = [f"📱 {h['row']['Nama_Lengkap']}" for h in hasil]
            st.radio(
                "Pilih alternatif",
                labels,
                index=idx,
                horizontal=True,
                key=radio_key,
                label_visibility="collapsed",
            )

            render_alternatif(ref, h_selected, mode)

            render_outcome(st.session_state.get("attempt_id"), pilihan_customer, mode)
    except Exception as e:
        print("UI error:", repr(e))
        st.error("Terjadi kendala saat menampilkan rekomendasi. Coba refresh data atau pilih produk lain.")
else:
    st.session_state.pop("last_logged_product", None)
    st.info("👆 Ketik atau pilih nama HP di kolom pencarian untuk mulai.")

render_pilot()
