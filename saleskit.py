import re
import csv
import os
import uuid
import html
from datetime import datetime, timezone, timedelta

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
from streamlit_searchbox import st_searchbox

st.set_page_config(
    page_title="Digiplus Smart Sales Assistant",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================
# SPLASH SCREEN
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
                    position: fixed !important; inset: 0 !important; z-index: 999999 !important;
                    display: flex !important; align-items: center !important; justify-content: center !important;
                    background:
                        radial-gradient(900px 420px at 50% 40%, rgba(77,166,255,.15), transparent 65%),
                        radial-gradient(700px 320px at 50% 60%, rgba(142,216,255,.06), transparent 70%),
                        linear-gradient(180deg, #050812, #080C16 55%, #0B1220) !important;
                    color: #F3F6FB !important; font-family: 'Roboto', Arial, sans-serif !important;
                    animation: dp-splash-in 0.4s ease-out both !important; pointer-events: all !important;
                }}
                #dp-splash.dp-out {{ animation: dp-splash-out 0.5s ease-in forwards !important; pointer-events: none !important; }}
                #dp-splash .dp-sp-inner {{ text-align: center; max-width: 560px; padding: 2rem; }}
                #dp-splash .dp-sp-logo {{
                    width: 76px; height: 76px; margin: 0 auto 1.6rem; border-radius: 20px;
                    display: flex; align-items: center; justify-content: center; color: #FFFFFF;
                    background: linear-gradient(145deg, rgba(77,166,255,.32), rgba(255,255,255,.06));
                    border: 1px solid rgba(142,216,255,.38);
                    box-shadow: 0 0 50px rgba(77,166,255,.45), inset 0 1px 0 rgba(255,255,255,.10);
                    position: relative; animation: dp-sp-logo 0.75s cubic-bezier(.2,.8,.2,1) 0.1s both;
                }}
                #dp-splash .dp-sp-logo::after {{
                    content: ""; position: absolute; right: -4px; bottom: -4px;
                    width: 14px; height: 14px; border-radius: 50%;
                    background: #E31E24; box-shadow: 0 0 14px rgba(227,30,36,.65);
                }}
                #dp-splash .dp-sp-logo svg {{ width: 68%; height: 68%; display: block; filter: drop-shadow(0 0 8px rgba(142,216,255,.6)); }}
                #dp-splash .dp-sp-eyebrow {{ font-size: .7rem; letter-spacing: .38em; color: #8ED8FF; text-transform: uppercase; font-weight: 600; opacity: 0; animation: dp-sp-up 0.55s ease-out 0.45s both; }}
                #dp-splash .dp-sp-title {{ font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin-top: .65rem; letter-spacing: -.02em; line-height: 1.2; opacity: 0; animation: dp-sp-up 0.55s ease-out 0.65s both; }}
                #dp-splash .dp-sp-line {{ width: 90px; height: 1px; margin: 1.5rem auto; background: linear-gradient(90deg, transparent, #4DA6FF, transparent); box-shadow: 0 0 14px #4DA6FF; opacity: 0; animation: dp-sp-up 0.55s ease-out 0.85s both; }}
                #dp-splash .dp-sp-tag {{ font-size: .92rem; font-style: italic; color: #B4C0D4; opacity: 0; animation: dp-sp-up 0.55s ease-out 1.05s both; }}
                #dp-splash .dp-sp-credit {{ margin-top: .55rem; font-size: .78rem; color: #8E9BB0; opacity: 0; animation: dp-sp-up 0.55s ease-out 1.25s both; }}
                #dp-splash .dp-sp-credit b {{ color: #E8EEF8; font-weight: 600; }}
                #dp-splash .dp-sp-dots {{ margin-top: 2.2rem; display: flex; gap: .4rem; justify-content: center; opacity: 0; animation: dp-sp-up 0.55s ease-out 1.45s both; }}
                #dp-splash .dp-sp-dot {{ width: 6px; height: 6px; border-radius: 50%; background: rgba(142,216,255,.35); animation: dp-sp-pulse 1.2s ease-in-out infinite; }}
                #dp-splash .dp-sp-dot:nth-child(2) {{ animation-delay: .15s; }}
                #dp-splash .dp-sp-dot:nth-child(3) {{ animation-delay: .3s; }}
                @keyframes dp-splash-in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
                @keyframes dp-splash-out {{ from {{ opacity: 1; }} to {{ opacity: 0; }} }}
                @keyframes dp-sp-logo {{ from {{ opacity: 0; transform: scale(0.65); }} to {{ opacity: 1; transform: scale(1); }} }}
                @keyframes dp-sp-up {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                @keyframes dp-sp-pulse {{ 0%, 100% {{ opacity: .35; transform: scale(1); }} 50% {{ opacity: 1; transform: scale(1.3); background: #8ED8FF; }} }}
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
                                    <stop offset="0%" stop-color="#8FE9FF"/><stop offset="100%" stop-color="#4DA6FF"/>
                                </linearGradient>
                                <linearGradient id="dpBody" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" stop-color="#FFFFFF"/><stop offset="100%" stop-color="#B4DDFF"/>
                                </linearGradient>
                            </defs>
                            <rect x="24" y="6" width="52" height="88" rx="10" ry="10" fill="url(#dpBody)"/>
                            <rect x="28" y="16" width="44" height="66" rx="6" ry="6" fill="#0A1424"/>
                            <rect x="32" y="20" width="36" height="58" rx="4" ry="4" fill="url(#dpScreen)" opacity="0.85"/>
                            <line x1="44" y1="11" x2="56" y2="11" stroke="#0A1424" stroke-width="2" stroke-linecap="round"/>
                            <circle cx="50" cy="88" r="3.5" fill="#0A1424" stroke="rgba(142,216,255,.6)" stroke-width="0.8"/>
                        </svg>
                    </div>
                    <div class="dp-sp-eyebrow">DIGIPLUS · MAPTECH</div>
                    <div class="dp-sp-title">Smart Sales Assistant</div>
                    <div class="dp-sp-line"></div>
                    <div class="dp-sp-tag">From "We don't have it" → "Here's what we have."</div>
                    <div class="dp-sp-credit">created by <b>Herlian Bhara</b></div>
                    <div class="dp-sp-dots">
                        <div class="dp-sp-dot"></div><div class="dp-sp-dot"></div><div class="dp-sp-dot"></div>
                    </div>
                </div>
            `;
            doc.body.appendChild(splash);

            setTimeout(() => {{
                splash.classList.add('dp-out');
                setTimeout(() => {{ try {{ splash.remove(); }} catch (e) {{}} }}, 550);
            }}, {dur});
        }} catch (err) {{ console.warn('Splash error:', err); }}
    }})();
    </script>
    """, height=0, scrolling=False)


show_splash()


# ============================================
# CSS
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;800;900&display=swap');

html, body, .stApp, button, input, textarea, [class*="st-"] {
    font-family: 'Roboto', Arial, sans-serif !important;
}

/* LOCK HORIZONTAL SCROLL */
html, body { overflow-x: hidden; overflow-x: clip !important; overflow-y: visible !important; max-width: 100vw; }
.stApp { overflow-x: hidden; overflow-x: clip !important; max-width: 100vw; }
[data-testid="stAppViewContainer"] { overflow-x: hidden; overflow-x: clip !important; }
[data-testid="stMain"] { overflow-x: hidden; overflow-x: clip !important; }
.block-container { overflow-x: clip; max-width: 100%; }
section.main { overflow-x: clip !important; }

/* HIDE STREAMLIT CHROME */
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

/* BASE */
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

/* KEYFRAMES */
@keyframes dpFadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes dpFadeIn { from { opacity: 0; } to { opacity: 1; } }

/* HEADER */
.dp-head { text-align: center; padding: 2.2rem 0 1rem; animation: dpFadeUp 0.55s ease-out both; }
.dp-title { font-size: 2.1rem; font-weight: 700; letter-spacing: -.01em; margin: 0; color: #FFFFFF; line-height: 1.25; }
.dp-sub { font-size: 1rem; font-weight: 400; color: #B4C0D4; margin: .75rem auto 0; max-width: 620px; line-height: 1.55; }
.dp-sub-part2 { display: inline-block; font-size: .95rem; opacity: .92; margin-top: .15rem; }
.dp-sep { margin: 1.6rem 0 1.4rem; }

/* SECTION HEADINGS */
.dp-h2 { font-size: 1.45rem; font-weight: 600; margin: 1.6rem 0 .2rem; color: #FFFFFF; animation: dpFadeUp 0.5s ease-out 0.05s both; }
.dp-it { font-style: italic; font-weight: 300; color: #B4C0D4; margin-bottom: 1.1rem; animation: dpFadeUp 0.5s ease-out 0.1s both; }

/* GLASS CARDS */
.dp-glass {
    background: rgba(255,255,255,.035); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(142,216,255,.12); border-radius: 14px; padding: 1.1rem 1.25rem;
    box-shadow: 0 12px 40px rgba(0,0,0,.30), 0 0 30px rgba(80,150,255,.05);
    animation: dpFadeUp 0.55s ease-out 0.15s both;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.dp-glass:hover { border-color: rgba(142,216,255,.22); box-shadow: 0 12px 40px rgba(0,0,0,.35), 0 0 36px rgba(80,150,255,.10); }
.dp-ch { font-size: 1.02rem; font-weight: 500; color: #8ED8FF; margin-bottom: .9rem; }
.dp-probe { background: rgba(20,45,75,.35); border-color: rgba(142,216,255,.18); }
.dp-probe .dp-ch { color: #8ED8FF; }
.dp-pt { display: flex; gap: .6rem; margin: .1rem 0 .95rem; line-height: 1.55; font-size: 1rem; font-weight: 400; color: #E8EEF8; }
.dp-script { font-style: italic; line-height: 1.7; font-size: 1rem; font-weight: 300; color: #E8EEF8; word-break: break-word; overflow-wrap: anywhere; }

/* VARIAN TOGGLE (pills) */
.dp-varian-hint {
    font-size: .75rem;
    color: #8E9BB0;
    margin-bottom: .45rem;
    letter-spacing: .02em;
}
[data-testid="stPills"] { margin-bottom: .7rem !important; }
[data-testid="stPills"] button {
    background: rgba(255,255,255,.05) !important;
    color: #8E9BB0 !important;
    border: 1px solid rgba(142,216,255,.15) !important;
    border-radius: 999px !important;
    padding: .35rem .85rem !important;
    font-size: .8rem !important;
    font-weight: 500 !important;
    transition: all .2s ease !important;
}
[data-testid="stPills"] button:hover {
    color: #FFFFFF !important;
    border-color: rgba(143,233,255,.4) !important;
    background: rgba(77,166,255,.1) !important;
}
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[data-selected="true"] {
    background: linear-gradient(135deg, rgba(77,166,255,.2), rgba(143,233,255,.1)) !important;
    color: #FFFFFF !important;
    border-color: #8FE9FF !important;
    box-shadow: 0 0 12px rgba(77,166,255,.3) !important;
}

/* RECOMMENDATION CARD */
.dp-reco {
    display: block; padding: 1rem 1.25rem; border-radius: 14px;
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    background: linear-gradient(135deg, rgba(20,45,75,0.90), rgba(8,22,42,0.95));
    border: 1px solid rgba(142,216,255,0.35); box-shadow: 0 0 35px rgba(77,166,255,0.15);
    margin: 1rem 0 1.3rem; transition: all .3s ease;
    animation: dpFadeUp 0.55s cubic-bezier(.2,.8,.2,1) both;
}
.dp-rl { font-size: .74rem; letter-spacing: .2em; font-weight: 600; color: #8ED8FF; }
.dp-rt { font-size: 1.35rem; font-weight: 700; color: #FFFFFF; margin-top: .15rem; word-break: break-word; overflow-wrap: anywhere; }
.dp-rs { font-size: .82rem; color: #9AA6B8; margin-top: .2rem; font-weight: 300; }

/* REFERENCE STRIP */
.dp-ref { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; padding: .4rem 0 .6rem; animation: dpFadeUp 0.55s ease-out 0.08s both; }
.dp-rk { font-size: .72rem; letter-spacing: .18em; text-transform: uppercase; color: #8794AB; font-weight: 500; }
.dp-rv { font-size: 1.9rem; font-weight: 500; color: #FFFFFF; text-shadow: 0 0 24px rgba(77,166,255,.30); margin-top: .15rem; word-break: break-word; overflow-wrap: anywhere; }

/* ALTERNATIVE HEADER */
.dp-alt { font-size: 1.6rem; font-weight: 700; margin: 1.1rem 0 .25rem; color: #FFFFFF; word-break: break-word; overflow-wrap: anywhere; animation: dpFadeUp 0.5s ease-out both; }
.dp-meta { color: #A9B6CB; font-size: .95rem; margin-bottom: .4rem; font-weight: 300; animation: dpFadeUp 0.5s ease-out 0.05s both; }
.dp-meta b { color: #8ED8FF; font-weight: 500; }
.dp-why { font-size: .85rem; color: #8E9BB0; margin: 0 0 1rem; font-weight: 300; line-height: 1.55; animation: dpFadeUp 0.5s ease-out 0.1s both; }
.dp-why b { color: #8ED8FF; font-weight: 500; }

/* OUTCOME */
.dp-done { border: 1px solid rgba(142,216,255,.35); color: #8ED8FF; padding: .8rem 1rem; border-radius: 12px; background: rgba(20,45,75,.25); animation: dpFadeUp 0.5s ease-out both; }
.dp-ask { margin: .4rem 0 1rem; animation: dpFadeUp 0.5s ease-out both; }
.dp-ask-title { font-size: 1rem; font-weight: 500; color: #E8EEF8; margin-bottom: .2rem; }
.dp-ask-sub { font-size: .85rem; font-weight: 300; color: #8E9BB0; font-style: italic; }

/* PILOT */
.dp-pilot { margin-top: 2.4rem; animation: dpFadeUp 0.6s ease-out 0.2s both; }
.dp-pl { font-size: .7rem; letter-spacing: .24em; color: #8794AB; }
.dp-pn2 { font-size: 1.5rem; font-weight: 300; color: #FFFFFF; }
.dp-pn2 span { font-size: .72rem; letter-spacing: .18em; color: #8794AB; }
.dp-bar { height: 4px; border-radius: 99px; background: rgba(255,255,255,.10); margin-top: .5rem; overflow: hidden; }
.dp-bar > div { height: 100%; background: linear-gradient(90deg, #4DA6FF, #8FE9FF); box-shadow: 0 0 10px #4DA6FF; transition: width 1.2s cubic-bezier(.2,.8,.2,1); }

/* SEARCH */
div[data-baseweb="select"] > div {
    background: rgba(20,32,52,.55) !important;
    border: 1px solid rgba(142,216,255,.20) !important;
    border-radius: 12px !important; min-height: 3.2rem;
    transition: all .25s cubic-bezier(.2,.8,.2,1);
}
div[data-baseweb="select"] > div:hover { border-color: rgba(143,233,255,.45) !important; box-shadow: 0 0 20px rgba(77,166,255,.12); }
div[data-baseweb="select"] > div:focus-within { border-color: #8FE9FF !important; box-shadow: 0 0 0 1px rgba(143,233,255,.5), 0 0 24px rgba(77,166,255,.28) !important; }

/* HIDE RADIO BULATAN */
[data-testid="stRadio"] label > div:first-child,
[data-testid="stRadio"] label > div[role="presentation"],
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
[data-testid="stRadio"] [data-baseweb="radio"] > div[role="presentation"],
[data-testid="stRadio"] label input[type="radio"],
[data-testid="stRadio"] label [data-testid="stMarkdownContainer"] ~ div {
    display: none !important; visibility: hidden !important;
    width: 0 !important; min-width: 0 !important; max-width: 0 !important;
    height: 0 !important; min-height: 0 !important;
    margin: 0 !important; padding: 0 !important;
    position: absolute !important; left: -9999px !important;
    opacity: 0 !important; pointer-events: none !important;
}

/* RADIO AS TABS */
[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important;
    gap: .3rem !important; overflow-x: auto; padding: 0 0 .5rem 0;
    border-bottom: 1px solid rgba(150,200,255,.12); margin-bottom: 1.2rem;
    scrollbar-width: thin; max-width: 100% !important; box-sizing: border-box;
    animation: dpFadeUp 0.5s ease-out 0.12s both;
}
[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar { height: 4px; }
[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar-thumb { background: rgba(142,216,255,.2); border-radius: 2px; }
[data-testid="stRadio"] label {
    background: transparent !important; color: #8E9BB0 !important;
    padding: .65rem 1.05rem !important; white-space: nowrap;
    border-radius: 10px 10px 0 0; transition: all .25s cubic-bezier(.2,.8,.2,1);
    cursor: pointer; margin: 0 !important; border: none !important; min-height: auto !important;
    display: inline-flex !important; align-items: center !important; gap: 0 !important;
}
[data-testid="stRadio"] label:hover { color: #FFFFFF !important; background: rgba(77,166,255,.08) !important; transform: translateY(-2px); }
[data-testid="stRadio"] label:has(input:checked) {
    color: #FFFFFF !important; background: rgba(77,166,255,.11) !important;
    text-shadow: 0 0 14px rgba(77,166,255,.55);
    box-shadow: inset 0 -2px 0 #4DA6FF, 0 0 12px rgba(77,166,255,.25);
}
[data-testid="stRadio"] label p { font-size: .9rem !important; font-weight: 500 !important; margin: 0 !important; }
[data-testid="stRadio"] > label:first-child { display: none !important; }

/* MAIN NAV TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: .4rem !important; overflow-x: auto; flex-wrap: nowrap;
    border-bottom: 1px solid rgba(150,200,255,.12);
    margin-bottom: 1.4rem;
    animation: dpFadeUp 0.5s ease-out both;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #8E9BB0 !important;
    padding: .75rem 1.25rem !important; white-space: nowrap;
    border-radius: 12px 12px 0 0; transition: all .25s ease; font-weight: 500;
}
.stTabs [data-baseweb="tab"]:hover { color: #FFFFFF !important; background: rgba(77,166,255,.06) !important; }
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important; background: rgba(77,166,255,.12) !important;
    text-shadow: 0 0 14px rgba(77,166,255,.55);
}
.stTabs [data-baseweb="tab-highlight"] { background: #4DA6FF !important; height: 2px !important; box-shadow: 0 0 12px #4DA6FF; }
.stTabs [data-baseweb="tab-border"] { background: transparent !important; }

/* BUTTONS */
div.stButton > button {
    width: 100%; min-height: 3rem; border-radius: 12px;
    background: rgba(255,255,255,.05); color: #FFFFFF;
    border: 1px solid rgba(150,200,255,.18);
    transition: all .25s cubic-bezier(.2,.8,.2,1); font-weight: 500; word-break: break-word;
}
div.stButton > button:hover {
    border-color: #4DA6FF; background: rgba(77,166,255,.12); color: #FFFFFF;
    box-shadow: 0 0 22px rgba(77,166,255,.25), 0 8px 20px rgba(0,0,0,.30);
    transform: translateY(-2px);
}
div.stButton > button:active { transform: translateY(0); }

/* DOWNLOAD BUTTON */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, rgba(20,45,75,.85), rgba(8,22,42,.95)) !important;
    color: #8ED8FF !important;
    border: 1px solid rgba(142,216,255,.35) !important;
    transition: all .25s cubic-bezier(.2,.8,.2,1) !important;
    min-height: 3rem !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    width: 100% !important;
    letter-spacing: .02em !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: #4DA6FF !important;
    box-shadow: 0 0 22px rgba(77,166,255,.30), 0 8px 20px rgba(0,0,0,.30) !important;
    transform: translateY(-2px);
    color: #FFFFFF !important;
}

/* ANALYTICS */
.dp-an-h2 { font-size: 1.6rem; font-weight: 700; color: #FFFFFF; margin: 0 0 .35rem; animation: dpFadeUp 0.5s ease-out both; }
.dp-an-it { font-style: italic; font-weight: 300; color: #B4C0D4; margin-bottom: 1.5rem; animation: dpFadeUp 0.5s ease-out 0.05s both; }
.dp-an-empty {
    padding: 3rem 1.5rem; text-align: center;
    background: rgba(255,255,255,.03);
    border: 1px dashed rgba(142,216,255,.22);
    border-radius: 14px; color: #8E9BB0;
    font-size: .95rem; font-weight: 300;
    animation: dpFadeUp 0.5s ease-out both;
}
.dp-kpi-row {
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: .9rem; margin: .5rem 0 1.8rem;
}
.dp-kpi {
    background: rgba(255,255,255,.035);
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(142,216,255,.12);
    border-radius: 14px; padding: 1rem 1.15rem;
    box-shadow: 0 12px 40px rgba(0,0,0,.25), 0 0 30px rgba(80,150,255,.04);
    animation: dpFadeUp 0.55s ease-out both;
    transition: border-color .3s ease, box-shadow .3s ease;
}
.dp-kpi:nth-child(1) { animation-delay: 0.05s; }
.dp-kpi:nth-child(2) { animation-delay: 0.10s; }
.dp-kpi:nth-child(3) { animation-delay: 0.15s; }
.dp-kpi:nth-child(4) { animation-delay: 0.20s; }
.dp-kpi:hover { border-color: rgba(142,216,255,.25); box-shadow: 0 12px 40px rgba(0,0,0,.35), 0 0 36px rgba(80,150,255,.10); }
.dp-kpi-label { font-size: .68rem; letter-spacing: .18em; color: #8794AB; text-transform: uppercase; font-weight: 600; }
.dp-kpi-value { font-size: 2rem; font-weight: 600; color: #FFFFFF; margin-top: .5rem; line-height: 1; letter-spacing: -.02em; }
.dp-kpi-value.blue { color: #8ED8FF; text-shadow: 0 0 22px rgba(142,216,255,.35); }
.dp-kpi-value.green { color: #4ADE80; text-shadow: 0 0 22px rgba(74,222,128,.35); }
.dp-kpi-value.amber { color: #F5B84B; text-shadow: 0 0 22px rgba(245,184,75,.35); }
.dp-kpi-sub { font-size: .75rem; color: #8E9BB0; margin-top: .45rem; font-weight: 300; }
.dp-an-section {
    font-size: .9rem; font-weight: 600; color: #8ED8FF;
    letter-spacing: .02em; margin: .8rem 0 .6rem;
    animation: dpFadeUp 0.5s ease-out both;
}

/* A/B TESTING CARDS */
.dp-ab-grid {
    display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem; margin: .6rem 0 1rem;
}
.dp-ab-card {
    padding: 1.15rem 1.25rem;
    background: rgba(255,255,255,.035);
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(142,216,255,.12);
    border-radius: 14px;
    animation: dpFadeUp 0.55s ease-out both;
    transition: border-color .3s ease, box-shadow .3s ease;
}
.dp-ab-card.a { border-color: rgba(143,233,255,.30); }
.dp-ab-card.b { border-color: rgba(74,222,128,.30); }
.dp-ab-card:hover { box-shadow: 0 12px 40px rgba(0,0,0,.35); }
.dp-ab-label {
    font-size: .66rem; letter-spacing: .22em; text-transform: uppercase;
    font-weight: 700;
}
.dp-ab-label.a { color: #8FE9FF; }
.dp-ab-label.b { color: #4ADE80; }
.dp-ab-name { font-size: .95rem; font-weight: 600; color: #FFFFFF; margin-top: .25rem; }
.dp-ab-rate {
    font-size: 2rem; font-weight: 700; margin-top: .65rem; line-height: 1;
    letter-spacing: -.02em;
}
.dp-ab-card.a .dp-ab-rate { color: #8FE9FF; text-shadow: 0 0 22px rgba(143,233,255,.35); }
.dp-ab-card.b .dp-ab-rate { color: #4ADE80; text-shadow: 0 0 22px rgba(74,222,128,.35); }
.dp-ab-detail { font-size: .78rem; color: #8E9BB0; margin-top: .45rem; font-weight: 300; line-height: 1.5; }

/* CUSTOM LEGEND */
.dp-legend {
    display: flex; flex-wrap: wrap; gap: .35rem .9rem;
    justify-content: center;
    margin-top: .6rem;
    animation: dpFadeUp 0.5s ease-out 0.1s both;
}
.dp-legend-item {
    display: flex; align-items: center; gap: .4rem;
    font-size: .82rem; color: #C4CFDD;
    font-weight: 400;
}
.dp-legend-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dp-legend-count {
    color: #8ED8FF; font-weight: 600; margin-left: .15rem;
}

/* PDF EXPORT SECTION */
.dp-pdf-block {
    margin-top: 2rem;
    padding: 1.4rem 1.4rem 1.2rem;
    background: linear-gradient(135deg, rgba(20,45,75,.55), rgba(8,22,42,.75));
    border: 1px solid rgba(142,216,255,.20);
    border-radius: 16px;
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 12px 40px rgba(0,0,0,.30), 0 0 30px rgba(77,166,255,.06);
    animation: dpFadeUp 0.5s ease-out 0.15s both;
}
.dp-pdf-title {
    font-size: 1rem; font-weight: 600; color: #FFFFFF; margin-bottom: .35rem;
    display: flex; align-items: center; gap: .5rem;
}
.dp-pdf-sub {
    font-size: .85rem; color: #8E9BB0; margin-bottom: 1rem;
    line-height: 1.55; font-weight: 300;
}

/* reduce motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* MOBILE */
@media (max-width: 768px) {
    .block-container { padding: 0.5rem 0.9rem 4rem; }
    .dp-head { padding: 1.4rem 0 0.8rem; }
    .dp-title { font-size: 1.5rem; }
    .dp-sub { font-size: .92rem; margin-top: .5rem; }
    .dp-sub-part2 { font-size: .88rem; }
    .dp-ref { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem; }
    .dp-rv { font-size: 1rem; word-break: break-word; overflow-wrap: anywhere; }
    .dp-rt { word-break: break-word; overflow-wrap: anywhere; }
    .dp-alt { font-size: 1.3rem; }
    .dp-reco .dp-rt { font-size: 1.15rem; }
    [data-testid="stRadio"] label { padding: .55rem .85rem !important; }
    [data-testid="stRadio"] label p { font-size: .82rem !important; }
    [data-testid="stRadio"] label:hover { transform: translateY(-1px); }
    .dp-kpi-row { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .6rem; }
    .dp-kpi { padding: .85rem .95rem; }
    .dp-kpi-value { font-size: 1.5rem; }
    .dp-kpi-value[style] { font-size: .95rem !important; }
    .stTabs [data-baseweb="tab"] { padding: .65rem 1rem !important; font-size: .9rem; }
    .dp-pdf-block { padding: 1.1rem 1rem 1rem; }
    .dp-legend { gap: .3rem .7rem; }
    .dp-legend-item { font-size: .78rem; }
    .dp-ab-grid { grid-template-columns: 1fr; gap: .7rem; }
    .dp-ab-rate { font-size: 1.6rem; }
}
</style>
""", unsafe_allow_html=True)


# ============================================
# JS SAFETY NET
# ============================================
components.html("""
<script>
(function() {
    const doc = window.parent.document;
    const resetScroll = () => {
        const targets = [
            doc.documentElement, doc.body,
            doc.querySelector('.stApp'),
            doc.querySelector('[data-testid="stAppViewContainer"]'),
            doc.querySelector('[data-testid="stMain"]'),
            doc.querySelector('[data-testid="stVerticalBlock"]')
        ];
        targets.forEach(el => {
            if (el) { el.scrollLeft = 0; el.scrollTo && el.scrollTo({ left: 0, behavior: 'instant' }); }
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
})();
</script>
""", height=0)


# ============================================
# OVERRIDE KHUSUS
# ============================================
OVERRIDE_TOP = {
    "Poco X8 5G": "Xiaomi Redmi Note 17 Pro 5G",
}


# ============================================
# BOBOT SKOR
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


def cari_gugur(ref, pool, mode, tol, sudah_dipilih_ids, top_n=5):
    kandidat = pool[~pool["Nama_Lengkap"].isin(sudah_dipilih_ids)]
    kandidat = kandidat[kandidat["Nama_Lengkap"] != ref["Nama_Lengkap"]]
    gugur = []
    for _, row in kandidat.iterrows():
        try:
            sel = float(row["Harga"]) - float(ref["Harga"])
        except (TypeError, ValueError):
            continue
        if pd.isna(sel):
            continue
        h = hitung_kecocokan(ref, row, mode, tol)
        h["row"] = row
        h["selisih"] = sel
        gugur.append(h)
    gugur.sort(key=lambda x: (-x["skor"], abs(x["selisih"])))
    return gugur[:top_n]


def gabung_teks(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " dan " + items[-1]


def kecil(t):
    return t if len(t) < 2 or t[1].isupper() else t[0].lower() + t[1:]


# ============================================
# SCRIPT VARIAN (A/B TESTING)
# ============================================
def buat_script_varian(ref_nama, alt_row, mode, selisih, h=None):
    """Return (varian_a, varian_b) — 2 pendekatan script untuk A/B test.
    
    Varian A · Spesifikasi: fokus chipset, tier, spec match (pendekatan teknis).
    Varian B · Manfaat: fokus use case, aktivitas user, prob personal.
    """
    kondisi = ("memang sedang kosong di Digiplus" if mode == "toko"
               else "memang belum kami jual di Digiplus")
    alt_nama = alt_row["Nama_Lengkap"]
    tier = clean(alt_row.get("Tier"))
    target = clean(alt_row.get("Target_User"))
    chip = clean(alt_row.get("Chipset"))
    poin = [clean(alt_row.get(f"Kelebihan_{i}")) for i in (1, 2, 3)]
    poin = [p for p in poin if p]

    # ============================================
    # VARIAN A — SPESIFIKASI
    # ============================================
    kal_a = [f"Kak, {ref_nama} {kondisi}."]
    if target:
        target_ringkas = target.split(",")[0].strip().lower()
        kal_a.append(f"Kalau Kakak sedang cari HP untuk {target_ringkas}, "
                     "saya punya satu alternatif menarik untuk dipertimbangkan.")
    else:
        kal_a.append("Tapi saya punya satu alternatif menarik untuk dipertimbangkan.")

    rekom = f"Produknya {alt_nama}"
    if tier:
        rekom += f", di kelas {tier}"
    kal_a.append(rekom + ".")

    if poin:
        kal_a.append(f"Yang menonjol, {gabung_teks([kecil(ringkas(p)) for p in poin])}.")

    spec_match = []
    chip_match = False
    if h:
        for ikon, teks in h.get("alasan", []):
            if ikon != "✅":
                continue
            tl = teks.lower()
            if "chipset" in tl:
                spec_match.append(kecil(teks)); chip_match = True
            elif "tier sama" in tl:
                spec_match.append(kecil(teks))

    if chip_match and spec_match:
        kal_a.append(f"Kebetulan spesifikasi intinya juga sejalan — {gabung_teks(spec_match[:2])}. "
                     "Jadi dari sisi kebutuhan, tidak jauh berbeda dengan yang Kakak cari.")
    elif spec_match:
        kal_a.append(f"Menariknya, {gabung_teks(spec_match[:2])} — "
                     "jadi secara kelas produk, sepadan dengan yang Kakak cari.")
    elif chip:
        kal_a.append(f"Dari sisi prosesor, produk ini pakai {chip}.")

    if selisih < -500000:
        kal_a.append(f"Bahkan harganya lebih hemat {rp(abs(selisih))} dibanding {ref_nama}, "
                     "jadi Kakak dapat spesifikasi yang sepadan dengan harga lebih ringan.")
    elif selisih > 500000:
        kal_a.append(f"Memang ada selisih sekitar {rp(selisih)} dari {ref_nama}, "
                     "tapi tambahan itu sepadan dengan peningkatan yang Kakak dapat, "
                     "bukan sekadar beda harga.")
    else:
        kal_a.append(f"Harganya di kisaran yang sama dengan {ref_nama}, "
                     "jadi tidak ada trade-off harga yang perlu dipikirkan.")

    kal_a.append("Kalau Kakak berkenan, saya bisa tunjukkan unitnya langsung "
                 "supaya bisa kita bandingkan bareng-bareng.")
    varian_a = " ".join(kal_a)

    # ============================================
    # VARIAN B — MANFAAT
    # ============================================
    kal_b = [f"Kak, {ref_nama} {kondisi}."]

    if target:
        target_ringkas = target.split(",")[0].strip().lower()
        kal_b.append(f"Sebelum saya tawarkan yang lain, boleh saya tahu dulu — "
                     f"kira-kira HP ini bakal sering dipakai untuk {target_ringkas}, "
                     "atau ada aktivitas lain yang jadi prioritas Kakak?")
    else:
        kal_b.append("Sebelum saya tawarkan yang lain, boleh saya tahu dulu — "
                     "aktivitas apa yang paling sering Kakak lakukan dengan HP sehari-hari?")

    rekom_b = f"Soalnya, ada satu produk yang saya rasa cocok dengan kebutuhan seperti itu — {alt_nama}"
    if tier:
        rekom_b += f", di kelas {tier}"
    kal_b.append(rekom_b + ".")

    if poin:
        kal_b.append(f"Yang bikin saya rekomendasiin, "
                     f"{gabung_teks([kecil(ringkas(p)) for p in poin[:2]])}.")

    if target:
        target_ringkas2 = target.split(",")[0].strip().lower()
        kal_b.append(f"Jadi bukan cuma soal spec-nya mirip, "
                     f"tapi memang dirancang untuk pengguna seperti {target_ringkas2}.")

    if selisih < -500000:
        kal_b.append(f"Dan kabar baiknya, harganya malah lebih ringan {rp(abs(selisih))} "
                     f"dari {ref_nama} — jadi Kakak bisa dapat yang lebih cocok "
                     "dengan budget lebih hemat.")
    elif selisih > 500000:
        kal_b.append(f"Selisih harga sekitar {rp(selisih)} dari {ref_nama}, "
                     "tapi menurut saya worth it karena benefit yang Kakak dapat "
                     "lebih sesuai kebutuhan.")
    else:
        kal_b.append(f"Harganya juga di kisaran yang sama dengan {ref_nama}, "
                     "jadi tidak perlu mikir soal budget.")

    kal_b.append("Gimana, Kak? Mau saya bantu tunjukkan unitnya langsung "
                 "supaya Kakak bisa coba dulu?")
    varian_b = " ".join(kal_b)

    return varian_a, varian_b


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
# LOGGING
# ============================================
WIB = timezone(timedelta(hours=7))
LOG_HEADER = [
    "Timestamp", "Attempt_ID", "Event", "Produk_Dicari", "Mode",
    "Jumlah_Rekomendasi", "Alternatif_1", "Alternatif_2", "Alternatif_3", "Hasil",
    "Varian_Dipakai",
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
            scopes=["https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"],
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(st.secrets["gsheets"]["spreadsheet_id"])
        try:
            ws = sh.worksheet("Log")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="Log", rows=1000, cols=len(LOG_HEADER))
        # Auto-migrate header
        if ws.row_values(1) != LOG_HEADER:
            ws.update(range_name="A1", values=[LOG_HEADER])
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
           produk, mode, len(nama_alt), alt[0], alt[1], alt[2], "", ""]
    return tulis_log(row)


def catat_outcome(attempt_id, produk, mode, hasil, varian=""):
    row = [datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"), attempt_id, "outcome",
           produk, mode, "", "", "", "", hasil, varian]
    return tulis_log(row)


@st.cache_data(ttl=300)
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


@st.cache_data(ttl=300)
def muat_log_df():
    ws, _ = get_log_sheet()
    if ws is not None:
        try:
            values = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
            if not values or len(values) < 2:
                return pd.DataFrame(columns=LOG_HEADER)
            header = [str(h).strip() for h in values[0]]
            rows = values[1:]
            n = len(header)
            rows = [(list(r) + [""] * n)[:n] for r in rows]
            df = pd.DataFrame(rows, columns=header)
            if "Varian_Dipakai" not in df.columns:
                df["Varian_Dipakai"] = ""
            return df
        except Exception:
            pass
    if os.path.exists(LOCAL_LOG_FILE):
        try:
            df = pd.read_csv(LOCAL_LOG_FILE, dtype=str)
            if "Varian_Dipakai" not in df.columns:
                df["Varian_Dipakai"] = ""
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=LOG_HEADER)


# ============================================
# PDF REPORT GENERATOR
# ============================================
def buat_pdf_report(df_log, filter_store=None):
    try:
        from fpdf import FPDF
    except ImportError:
        return None, "Library fpdf2 belum terinstall. Tambahkan 'fpdf2' ke requirements.txt"

    df = df_log.copy()
    attempts = df[df["Event"].astype(str) == "attempt"].copy()
    outcomes = df[df["Event"].astype(str) == "outcome"].copy()

    total_attempts = len(attempts)
    total_outcomes = len(outcomes)
    berhasil_set = {"Berhasil menjual", "Switch berhasil"}
    berhasil = outcomes[outcomes["Hasil"].astype(str).isin(berhasil_set)]
    switch_rate = (len(berhasil) / total_outcomes * 100) if total_outcomes > 0 else 0.0

    produk_unik = 0
    top_produk = "—"
    if "Produk_Dicari" in attempts.columns and total_attempts > 0:
        produk_unik = attempts["Produk_Dicari"].nunique()
        t = attempts["Produk_Dicari"].value_counts()
        if len(t) > 0:
            top_produk = str(t.index[0])

    # Periode: filter timestamp valid
    periode = None
    if "Timestamp" in attempts.columns and total_attempts > 0:
        ts = pd.to_datetime(attempts["Timestamp"], errors="coerce").dropna()
        ts = ts[ts.dt.year >= 2020]
        if not ts.empty:
            awal = ts.min().strftime("%d %b %Y")
            akhir = ts.max().strftime("%d %b %Y")
            periode = f"{awal} - {akhir}" if awal != akhir else awal

    if not periode:
        bulan_id = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                    "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        now = datetime.now(WIB)
        periode = f"{bulan_id[now.month - 1]} {now.year}"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_fill_color(10, 20, 36)
    pdf.rect(0, 0, 210, 50, "F")

    pdf.set_text_color(142, 216, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(15, 12)
    pdf.cell(0, 5, "DIGIPLUS  /  MAPTECH", ln=0)

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(15, 18)
    pdf.cell(0, 12, "Smart Sales Assistant", ln=1)

    pdf.set_text_color(180, 192, 212)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_x(15)
    pdf.cell(0, 6, "Switch-Selling Pilot Report", ln=1)

    pdf.set_text_color(142, 216, 255)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_xy(140, 14)
    pdf.cell(55, 4, "PERIODE", align="R", ln=1)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(140, 18)
    pdf.cell(55, 5, periode, align="R", ln=1)

    store_label = "Digiplus Seluruh Indonesia"
    if filter_store and filter_store not in ("Semua Store", "Digiplus Seluruh Indonesia"):
        store_label = filter_store
    pdf.set_text_color(142, 216, 255)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_xy(140, 27)
    pdf.cell(55, 4, "STORE", align="R", ln=1)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(140, 31)
    if len(store_label) > 30:
        store_label = store_label[:28] + "..."
    pdf.cell(55, 5, store_label, align="R", ln=1)

    pdf.set_xy(15, 60)
    pdf.set_text_color(142, 216, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "RINGKASAN EKSEKUTIF", ln=1)

    kpi_data = [
        ("TOTAL ATTEMPTS", str(total_attempts), f"dari target {TARGET_ATTEMPTS}"),
        ("SWITCH RATE", f"{switch_rate:.0f}%", f"{len(berhasil)} berhasil dari {total_outcomes} outcome"),
        ("PRODUK UNIK DICARI", str(produk_unik), "variasi customer request"),
        ("TOP PRODUK", top_produk, "paling sering dicari"),
    ]
    box_w = 88
    box_h = 28
    gap = 4
    start_y = 68

    for i, (label, value, sub) in enumerate(kpi_data):
        col = i % 2
        row = i // 2
        x = 15 + col * (box_w + gap)
        y = start_y + row * (box_h + gap)

        pdf.set_fill_color(245, 247, 250)
        pdf.rect(x, y, box_w, box_h, "F")
        pdf.set_fill_color(77, 166, 255)
        pdf.rect(x, y, 1.5, box_h, "F")

        pdf.set_text_color(120, 130, 145)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_xy(x + 4, y + 3)
        pdf.cell(0, 4, label, ln=1)

        pdf.set_text_color(10, 20, 36)
        val_display = value
        if len(val_display) > 26:
            val_display = val_display[:24] + "..."
        fnt_size = 16 if len(value) < 8 else 12
        pdf.set_font("Helvetica", "B", fnt_size)
        pdf.set_xy(x + 4, y + 9)
        pdf.cell(0, 8, val_display, ln=1)

        pdf.set_text_color(140, 150, 165)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(x + 4, y + 20)
        pdf.cell(0, 4, sub[:42], ln=1)

    y_now = start_y + 2 * (box_h + gap) + 6
    pdf.set_xy(15, y_now)
    pdf.set_text_color(142, 216, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "TOP 5 ALTERNATIF DIREKOMENDASIKAN", ln=1)

    alt_cols = [c for c in ["Alternatif_1", "Alternatif_2", "Alternatif_3"] if c in attempts.columns]
    all_alt = []
    for col in alt_cols:
        all_alt.extend([str(a).strip() for a in attempts[col].dropna().tolist()
                        if a and str(a).strip()])
    if all_alt:
        top_alt = pd.Series(all_alt).value_counts().head(5)
        y_table = y_now + 7
        for i, (name, count) in enumerate(top_alt.items()):
            row_y = y_table + i * 7
            if i % 2 == 0:
                pdf.set_fill_color(248, 250, 252)
                pdf.rect(15, row_y, 180, 7, "F")
            pdf.set_text_color(10, 20, 36)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_xy(18, row_y + 1.5)
            name_display = str(name)
            if len(name_display) > 55:
                name_display = name_display[:52] + "..."
            pdf.cell(140, 4, name_display, ln=0)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(77, 166, 255)
            pdf.set_xy(160, row_y + 1.5)
            pdf.cell(30, 4, str(count), align="R", ln=0)
        y_now = y_table + len(top_alt) * 7 + 6
    else:
        pdf.set_text_color(140, 150, 165)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_xy(15, y_now + 7)
        pdf.cell(0, 5, "Belum ada data alternatif.", ln=1)
        y_now += 14

    if y_now > 235:
        pdf.add_page()
        y_now = 20
    pdf.set_xy(15, y_now)
    pdf.set_text_color(142, 216, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "DISTRIBUSI OUTCOME", ln=1)

    if not outcomes.empty and "Hasil" in outcomes.columns:
        oc = outcomes["Hasil"].astype(str).value_counts()
        y_table = y_now + 7
        for i, (name, count) in enumerate(oc.items()):
            row_y = y_table + i * 7
            if i % 2 == 0:
                pdf.set_fill_color(248, 250, 252)
                pdf.rect(15, row_y, 180, 7, "F")
            pdf.set_text_color(10, 20, 36)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_xy(18, row_y + 1.5)
            pdf.cell(140, 4, str(name), ln=0)
            pdf.set_font("Helvetica", "B", 9)
            if "berhasil" in str(name).lower():
                pdf.set_text_color(74, 200, 120)
            else:
                pdf.set_text_color(77, 166, 255)
            pdf.set_xy(160, row_y + 1.5)
            pdf.cell(30, 4, str(count), align="R", ln=0)
        y_now = y_table + len(oc) * 7 + 6
    else:
        pdf.set_text_color(140, 150, 165)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_xy(15, y_now + 7)
        pdf.cell(0, 5, "Belum ada outcome.", ln=1)
        y_now += 14

    if y_now > 225:
        pdf.add_page()
        y_now = 20
    pdf.set_xy(15, y_now)
    pdf.set_text_color(142, 216, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "TOP 10 PRODUK PALING DICARI", ln=1)

    if "Produk_Dicari" in attempts.columns and total_attempts > 0:
        tp = attempts["Produk_Dicari"].value_counts().head(10)
        y_table = y_now + 7
        for i, (name, count) in enumerate(tp.items()):
            row_y = y_table + i * 7
            if row_y > 270:
                pdf.add_page()
                y_table = 13
                row_y = 20
            if i % 2 == 0:
                pdf.set_fill_color(248, 250, 252)
                pdf.rect(15, row_y, 180, 7, "F")
            pdf.set_text_color(10, 20, 36)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_xy(18, row_y + 1.5)
            name_display = str(name)
            if len(name_display) > 55:
                name_display = name_display[:52] + "..."
            pdf.cell(140, 4, name_display, ln=0)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(77, 166, 255)
            pdf.set_xy(160, row_y + 1.5)
            pdf.cell(30, 4, str(count), align="R", ln=0)

    waktu_export = datetime.now(WIB).strftime("%d %b %Y, %H:%M WIB")

    if pdf.get_y() > 260:
        pdf.add_page()

    pdf.set_auto_page_break(auto=False)
    pdf.set_y(-22)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 150, 165)
    pdf.cell(0, 5, f"Report dibuat otomatis oleh Digiplus Smart Sales Assistant  -  {waktu_export}",
             align="C", ln=1)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(10, 20, 36)
    pdf.cell(0, 5, "created by Herlian Bhara", align="C", ln=1)
    pdf.set_auto_page_break(auto=True)

    return bytes(pdf.output()), None


# ============================================
# LOAD DATA PRODUK
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
    return df_toko, df_kompet
