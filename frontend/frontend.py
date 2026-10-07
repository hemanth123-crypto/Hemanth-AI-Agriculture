"""
frontend/frontend.py
AI-Powered Agriculture Crop Advisory Assistant — Streamlit Frontend
Replicates all pages and API behaviour of the existing HTML/CSS/JS SPA.
Backend API base: http://localhost:8000
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_BASE = "http://localhost:8000"

DEMO_EMAIL = "demo@agriadvisor.ai"
DEMO_PASSWORD = "AgriTech2026!"

CURATED_CROPS = [
    {"name": "Rice",      "emoji": "🌾", "suitability": 92, "yieldAvg": 4.35, "risk": "Low",      "season": "Kharif",        "water": "High",     "soil": "Clayey / Alluvial"},
    {"name": "Wheat",     "emoji": "🌿", "suitability": 88, "yieldAvg": 4.10, "risk": "Low",      "season": "Rabi",          "water": "Medium",   "soil": "Well-drained Loam"},
    {"name": "Cotton",    "emoji": "🌱", "suitability": 84, "yieldAvg": 2.45, "risk": "Moderate", "season": "Kharif",        "water": "Medium",   "soil": "Black Cotton Soil"},
    {"name": "Maize",     "emoji": "🌽", "suitability": 86, "yieldAvg": 3.80, "risk": "Low",      "season": "Kharif/Rabi",   "water": "Medium",   "soil": "Fertile Loam"},
    {"name": "Sugarcane", "emoji": "🎋", "suitability": 80, "yieldAvg": 75.0, "risk": "Moderate", "season": "Whole Year",    "water": "High",     "soil": "Deep Alluvial Loam"},
    {"name": "Chickpea",  "emoji": "🧆", "suitability": 82, "yieldAvg": 1.85, "risk": "Low",      "season": "Rabi",          "water": "Low",      "soil": "Sandy Loam to Clay"},
    {"name": "Groundnut", "emoji": "🥜", "suitability": 85, "yieldAvg": 2.20, "risk": "Low",      "season": "Kharif/Summer", "water": "Low-Med",  "soil": "Sandy Loam"},
    {"name": "Soybean",   "emoji": "🌱", "suitability": 83, "yieldAvg": 2.15, "risk": "Moderate", "season": "Kharif",        "water": "Medium",   "soil": "Well-drained Black Soil"},
    {"name": "Mustard",   "emoji": "🌼", "suitability": 87, "yieldAvg": 1.95, "risk": "Low",      "season": "Rabi",          "water": "Low",      "soil": "Light to Medium Loam"},
    {"name": "Barley",    "emoji": "🌾", "suitability": 81, "yieldAvg": 3.20, "risk": "Low",      "season": "Rabi",          "water": "Low",      "soil": "Sandy Loam / Saline"},
    {"name": "Millets",   "emoji": "🌾", "suitability": 90, "yieldAvg": 1.70, "risk": "Low",      "season": "Kharif",        "water": "Very Low", "soil": "Shallow Sandy / Red"},
    {"name": "Jute",      "emoji": "🌿", "suitability": 78, "yieldAvg": 2.65, "risk": "Moderate", "season": "Kharif",        "water": "High",     "soil": "Alluvial Delta Soil"},
]

STATES = [
    "Andhra Pradesh","Assam","Bihar","Chhattisgarh","Gujarat","Haryana",
    "Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
    "Maharashtra","Manipur","Meghalaya","Odisha","Punjab","Rajasthan",
    "Tamil Nadu","Telangana","Uttar Pradesh","Uttarakhand","West Bengal",
]
SEASONS = ["Kharif", "Rabi", "Whole Year", "Summer", "Winter", "Autumn"]
CROPS_LIST = [c["name"] for c in CURATED_CROPS]

# ─────────────────────────────────────────────
# PAGE CONFIG & GLOBAL CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Agriculture Crop Advisory Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #020c06 0%, #041209 40%, #021006 100%) !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e2ffe0 !important;
  }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #030f07 0%, #041510 100%) !important;
    border-right: 1px solid #1a3a22 !important;
  }
  [data-testid="stHeader"] { background: transparent !important; }
  .block-container { padding-top: 1.5rem !important; max-width: 1280px; }

  h1, h2, h3 { font-family: 'Outfit', sans-serif !important; color: #39D98A !important; }
  h1 { font-size: 2rem !important; font-weight: 800 !important; }
  h2 { font-size: 1.4rem !important; font-weight: 700 !important; }
  h3 { font-size: 1.1rem !important; font-weight: 600 !important; }
  p, li, label, div { color: #b8d4b0 !important; }
  code { font-family: 'JetBrains Mono', monospace !important; color: #39D98A !important; }

  .agri-card {
    background: rgba(4,20,10,0.75);
    border: 1px solid rgba(57,217,138,0.18);
    border-radius: 14px; padding: 20px 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(8px);
    transition: border-color 0.25s;
  }
  .agri-card:hover { border-color: rgba(57,217,138,0.38); }

  .stButton > button {
    background: linear-gradient(135deg, #16a34a, #22c55e) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 10px 24px !important; transition: all 0.2s !important;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #15803d, #16a34a) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 18px rgba(34,197,94,0.35) !important;
  }

  .stTextInput > div > input, .stTextArea > div > textarea,
  .stSelectbox > div > div, .stNumberInput > div > input {
    background: rgba(4,20,10,0.8) !important;
    border: 1px solid rgba(57,217,138,0.25) !important;
    border-radius: 10px !important; color: #e2ffe0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
  }

  .advisory-box {
    background: rgba(2,12,6,0.9);
    border: 1px solid rgba(57,217,138,0.3);
    border-radius: 12px; padding: 20px 24px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; color: #a8d8a8 !important;
    white-space: pre-wrap; max-height: 420px; overflow-y: auto;
  }

  .login-hero {
    background: linear-gradient(135deg, rgba(4,25,12,0.95), rgba(2,15,8,0.98));
    border: 1px solid rgba(57,217,138,0.2);
    border-radius: 18px; padding: 40px 36px; text-align: center;
  }
  .brand-title { font-size: 2.2rem; font-weight: 800; color: #39D98A !important; font-family: 'Outfit',sans-serif; }
  .brand-sub   { color: #6aaa7a !important; font-size: 0.95rem; margin-top: 6px; }

  hr { border-color: rgba(57,217,138,0.15) !important; }
  .stSpinner > div { border-top-color: #39D98A !important; }
  .stAlert { border-radius: 10px !important; }

  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: #020c06; }
  ::-webkit-scrollbar-thumb { background: #1a4a2a; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "logged_in":     False,
        "user_name":     "",
        "user_email":    "",
        "page":          "Dashboard",
        "last_advisory": None,
        "query_history": [],
        "adv_query":     "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────
def api_post(endpoint: str, payload: dict):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=60)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach backend. Make sure `py run.py` is running at localhost:8000."
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, f"API Error: {detail}"
    except Exception as e:
        return None, str(e)

def api_get(endpoint: str):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=30)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach backend. Make sure `py run.py` is running at localhost:8000."
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
def page_login():
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div class="login-hero">
          <div style="font-size:3rem">🌱</div>
          <div class="brand-title">CropShield AI Platform</div>
          <div class="brand-sub">AI Agriculture Advisory Assistant</div>
          <p style="margin-top:14px;font-size:0.88rem;color:#5a9a6a">
            Hybrid RAG &nbsp;·&nbsp; ML Yield Prediction &nbsp;·&nbsp; 8-Agent Orchestration
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        mode = st.radio("Mode", ["Sign In", "Quick Demo"], horizontal=True, label_visibility="collapsed")

        with st.form("login_form"):
            if mode == "Quick Demo":
                st.info(f"Demo credentials: `{DEMO_EMAIL}` / `{DEMO_PASSWORD}`")
                email    = DEMO_EMAIL
                password = DEMO_PASSWORD
            else:
                email    = st.text_input("Email Address", placeholder="agronomist@example.com")
                password = st.text_input("Password", type="password", placeholder="Min. 6 characters")

            submitted = st.form_submit_button("🚀 Login to Dashboard", use_container_width=True)

        if submitted:
            e = email.strip().lower()
            ok, name = False, "Agricultural Specialist"
            if e == DEMO_EMAIL.lower() and password == DEMO_PASSWORD:
                ok, name = True, "Agricultural Specialist"
            elif e == "officer@agriadvisor.ai" and password == DEMO_PASSWORD:
                ok, name = True, "Extension Officer"
            elif len(password) >= 6:
                ok, name = True, email.split("@")[0].title()

            if ok:
                st.session_state.logged_in  = True
                st.session_state.user_email = email.strip()
                st.session_state.user_name  = name
                st.session_state.page       = "Dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials. Use demo credentials or a password >= 6 characters.")

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        badges = [
            ("🔍", "Hybrid RAG",    "Dense + Sparse FAISS"),
            ("🤖", "8-Agent AI",   "Deterministic Pipeline"),
            ("📊", "ML Prediction","Random Forest Yield"),
            ("🛡️", "Guardrails",   "LLM-as-a-Judge"),
        ]
        for col, (icon, title, sub) in zip([c1, c2, c3, c4], badges):
            col.markdown(f"""
            <div class="agri-card" style="text-align:center;padding:16px">
              <div style="font-size:1.6rem">{icon}</div>
              <div style="color:#39D98A;font-weight:700;font-size:0.9rem;margin-top:6px">{title}</div>
              <div style="color:#6aaa7a;font-size:0.75rem">{sub}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 8px 20px">
          <div style="font-size:1.4rem;font-weight:800;color:#39D98A;font-family:'Outfit',sans-serif">
            🌱 CropShield AI
          </div>
          <div style="color:#6aaa7a;font-size:0.75rem;margin-top:2px">Agricultural Decision Intelligence</div>
          <hr style="margin:12px 0;border-color:rgba(57,217,138,0.15)">
          <div style="color:#9aaa9a;font-size:0.74rem">Logged in as</div>
          <div style="color:#e2ffe0;font-weight:600;font-size:0.86rem">{st.session_state.user_name}</div>
          <div style="color:#6aaa7a;font-size:0.72rem">{st.session_state.user_email}</div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("🏠", "Dashboard"),
            ("🔍", "Crop Advisory"),
            ("📋", "Case Explorer"),
            ("🌱", "Crop Recommendation"),
            ("📈", "Yield Prediction"),
            ("⚠️",  "Risk & Impact Analysis"),
            ("💬", "Feedback"),
            ("🧪", "System Evaluation"),
        ]
        for icon, page in pages:
            if st.button(f"{icon}  {page}", key=f"nav_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()

        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "Dashboard"
            st.rerun()

        # Health status
        health, _ = api_get("/health")
        if health:
            st.sidebar.success(f"✅ Backend v{health.get('version','1.0.0')} · {health.get('vector_store_cases',0)} cases")
        else:
            st.sidebar.error("❌ Backend Offline — run `py run.py`")


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
def page_dashboard():
    st.markdown("## 🏠 Dashboard")
    st.caption("AI-powered agricultural intelligence at a glance.")

    health, _ = api_get("/health")
    cases  = health.get("vector_store_cases", 1500) if health else 1500
    ml_ok  = health.get("suitability_model_loaded", True) if health else True

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📦 Historical Cases", f"{cases:,}")
    m2.metric("🤖 AI Agents",        "8")
    m3.metric("📊 ML Models",        "2 Active" if ml_ok else "Offline")
    m4.metric("⚡ Avg Response",     "< 60 ms")

    st.markdown("---")
    st.markdown("### 🌾 Crop Knowledge Base")

    search_crop = st.text_input("🔎 Filter crops…", placeholder="Rice, Wheat, Cotton…", label_visibility="collapsed")
    filtered = [c for c in CURATED_CROPS if search_crop.lower() in c["name"].lower()] if search_crop else CURATED_CROPS

    cols = st.columns(4)
    for i, crop in enumerate(filtered):
        rc = "#22c55e" if crop["risk"] == "Low" else ("#ef4444" if crop["risk"] == "High" else "#facc15")
        with cols[i % 4]:
            st.markdown(f"""
            <div class="agri-card">
              <div style="font-size:1.8rem">{crop['emoji']}</div>
              <div style="font-size:1rem;font-weight:700;color:#39D98A;margin:6px 0 4px">{crop['name']}</div>
              <div style="margin-bottom:8px">
                <span style="background:rgba(57,217,138,0.1);border:1px solid rgba(57,217,138,0.2);
                             border-radius:6px;padding:2px 8px;font-size:0.72rem;color:#39D98A">
                  {crop['season']}
                </span>
                <span style="background:rgba(0,0,0,0.2);border:1px solid {rc};
                             border-radius:6px;padding:2px 8px;font-size:0.72rem;color:{rc};margin-left:4px">
                  {crop['risk']} Risk
                </span>
              </div>
              <div style="font-size:0.78rem;color:#8ab88a;line-height:1.6">
                <b style="color:#c8e8c0">Suitability:</b> {crop['suitability']}%<br>
                <b style="color:#c8e8c0">Avg Yield:</b> {crop['yieldAvg']} t/ha<br>
                <b style="color:#c8e8c0">Water:</b> {crop['water']}<br>
                <b style="color:#c8e8c0">Soil:</b> {crop['soil']}
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("🔍 Run Advisory Query",  use_container_width=True): st.session_state.page = "Crop Advisory";        st.rerun()
    if qa2.button("🌱 Crop Recommendation", use_container_width=True): st.session_state.page = "Crop Recommendation";  st.rerun()
    if qa3.button("📈 Yield Prediction",    use_container_width=True): st.session_state.page = "Yield Prediction";     st.rerun()
    if qa4.button("🧪 Run Evaluation",      use_container_width=True): st.session_state.page = "System Evaluation";   st.rerun()


# ─────────────────────────────────────────────
# CROP ADVISORY  POST /api/query
# ─────────────────────────────────────────────
def page_advisory():
    st.markdown("## 🔍 Crop Advisory Query")
    st.caption("Ask any agricultural question — powered by hybrid RAG + 8-agent pipeline.")

    EXAMPLES = [
        "Which crops performed well in Andhra Pradesh during Kharif with pH 6.5?",
        "Suggest crops for Punjab Rabi season with high nitrogen and low rainfall.",
        "What yield can I expect for Rice in West Bengal with 1200mm rainfall?",
        "Alternative crops for Cotton in Gujarat with black soil and medium water.",
    ]
    st.markdown("**💡 Example prompts — click to use:**")
    ec = st.columns(4)
    labels = ["📌 Rice — AP Kharif", "📌 Punjab Rabi", "📌 Rice Yield WB", "📌 Cotton Alt GJ"]
    for col, lbl, ex in zip(ec, labels, EXAMPLES):
        if col.button(lbl, use_container_width=True):
            st.session_state.adv_query = ex
            st.rerun()

    st.markdown("---")

    with st.form("advisory_form"):
        query = st.text_area(
            "Your agricultural query",
            value=st.session_state.adv_query,
            placeholder="e.g. Which crops performed well in Andhra Pradesh during Kharif with pH 6.5?",
            height=100,
        )
        with st.expander("🎛️ Advanced Filters (optional)"):
            fc1, fc2, fc3 = st.columns(3)
            f_state  = fc1.selectbox("State",  ["Any"] + STATES)
            f_season = fc2.selectbox("Season", ["Any"] + SEASONS)
            f_topk   = fc3.slider("Top-K Results", 3, 15, 5)
        submitted = st.form_submit_button("🚀 Get AI Advisory", use_container_width=True)

    if submitted:
        if not query.strip():
            st.warning("Please enter a query."); return

        payload = {"query": query.strip(), "top_k": f_topk}
        filters = {}
        if f_state  != "Any": filters["state"]  = f_state
        if f_season != "Any": filters["season"] = f_season
        if filters: payload["filters"] = filters

        stages = [
            "Analyzing agricultural conditions…",
            "Hybrid RAG search across 1,500 cases…",
            "Evaluating crop suitability & yield…",
            "Running risk & impact analysis…",
            "LLM Judge validation…",
        ]
        progress = st.progress(0)
        msg_ph   = st.empty()
        for i, stage in enumerate(stages):
            msg_ph.caption(f"⚙️ {stage}")
            progress.progress((i + 1) / len(stages))
            time.sleep(0.25)
        msg_ph.empty(); progress.empty()

        with st.spinner("Finalizing advisory…"):
            data, err = api_post("/api/query", payload)

        if err:
            st.error(f"⚠️ {err}"); return

        # Save state
        st.session_state.last_advisory = data
        st.session_state.adv_query = ""
        st.session_state.query_history.insert(0, {
            "query": query.strip(),
            "ts":    datetime.now().strftime("%Y-%m-%d %H:%M"),
            "crops": [c["crop"] for c in data.get("recommended_crops", [])],
        })

        st.success("✅ Advisory generated successfully")
        st.markdown("---")

        # Interpreted conditions
        conds = data.get("interpreted_conditions", {})
        if conds:
            st.markdown("### 🧠 Interpreted Agronomic Conditions")
            pairs = [
                ("Crop",        conds.get("crop")),
                ("Season",      conds.get("season")),
                ("State",       conds.get("state")),
                ("Soil Type",   conds.get("soil_type")),
                ("pH",          conds.get("ph")),
                ("Rainfall",    f"{conds['rainfall']} mm" if conds.get("rainfall") else None),
                ("Temperature", f"{conds['temperature']} °C" if conds.get("temperature") else None),
                ("Humidity",    f"{conds['humidity']} %" if conds.get("humidity") else None),
            ]
            valid = [(l, v) for l, v in pairs if v]
            cols  = st.columns(min(len(valid), 4))
            for col, (label, val) in zip(cols * 4, valid):
                col.metric(label, val)

        # Recommended crops
        recs = data.get("recommended_crops", [])
        if recs:
            st.markdown("### 🌾 Recommended Crops")
            for rec in recs:
                rl = str(rec.get("risk_level", "")).upper()
                rc = "#22c55e" if rl == "LOW" else ("#ef4444" if rl == "HIGH" else "#facc15")
                score = rec.get("suitability_score", 0)
                st.markdown(f"""
                <div class="agri-card">
                  <div style="display:flex;align-items:center;gap:12px">
                    <div style="font-size:1.8rem">🌱</div>
                    <div style="flex:1">
                      <div style="font-size:1.1rem;font-weight:700;color:#39D98A">{rec.get('crop','—')}</div>
                      <span style="border:1px solid {rc};border-radius:6px;padding:2px 8px;font-size:0.75rem;color:{rc}">
                        {rec.get('risk_level','—')} Risk
                      </span>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:1.6rem;font-weight:800;color:#39D98A">{score*100:.0f}%</div>
                      <div style="font-size:0.74rem;color:#6aaa7a">Suitability</div>
                    </div>
                  </div>
                  <p style="margin-top:10px;font-size:0.85rem;color:#9ab89a">{rec.get('recommendation_reason','')}</p>
                  <div style="font-size:0.82rem;color:#8ab88a">
                    Hist. Avg Yield: <b style="color:#39D98A">{rec.get('historical_avg_yield','—')} t/ha</b>
                  </div>
                </div>""", unsafe_allow_html=True)

        # Similar cases table
        cases = data.get("similar_cases", [])
        if cases:
            import pandas as pd
            st.markdown("### 📋 Similar Historical Cases")
            df = pd.DataFrame(cases)
            show = [c for c in ["case_id","crop","season","state","yield","ph","rainfall","similarity_score"] if c in df.columns]
            df_show = df[show].copy()
            if "similarity_score" in df_show.columns:
                df_show["similarity_score"] = df_show["similarity_score"].apply(lambda x: f"{x:.3f}")
            st.dataframe(df_show, use_container_width=True, hide_index=True)

        # Yield prediction
        yp = data.get("yield_prediction", {})
        if yp:
            st.markdown("### 📈 Yield Prediction")
            y1, y2, y3 = st.columns(3)
            y1.metric("Predicted Yield", f"{yp.get('predicted_yield','—')} t/ha")
            ci = yp.get("confidence_interval_80", [])
            if ci: y2.metric("80% CI", f"{ci[0]} – {ci[1]} t/ha")
            y3.metric("Crop", yp.get("crop", "—"))
            for f in yp.get("key_influencing_factors", []):
                st.markdown(f"- **{f['factor']}** → importance: `{f['importance']:.2f}`")

        # Risk analysis
        risk = data.get("risk_analysis", {})
        if risk:
            st.markdown("### ⚠️ Risk Analysis")
            rl = str(risk.get("overall_risk","")).upper()
            rc = "#22c55e" if rl=="LOW" else ("#ef4444" if rl=="HIGH" else "#facc15")
            st.markdown(f'<span style="color:{rc};font-size:1.1rem;font-weight:700">● {risk.get("overall_risk","—")} Overall Risk</span>', unsafe_allow_html=True)
            for rf in risk.get("risk_factors", []):
                st.markdown(f"- {rf}")

        # Impact analysis
        impact = data.get("impact_analysis", {})
        if impact:
            st.markdown("### 🔬 Impact Analysis")
            for ins in impact.get("insights", []):
                st.markdown(f"- {ins}")

        # Validation
        val = data.get("validation", {})
        if val:
            st.markdown("### 🛡️ LLM Judge Validation")
            v1, v2, v3 = st.columns(3)
            v1.metric("Passed",         "✅ Yes" if val.get("passed") else "❌ No")
            v2.metric("Judge Score",    f"{val.get('llm_judge_score',0)*100:.0f}%")
            v3.metric("Groundedness",   val.get("groundedness","—"))
            if val.get("notes"): st.caption(val["notes"])

        # Formatted advisory
        advisory_text = data.get("formatted_advisory","")
        if advisory_text:
            with st.expander("📄 Full Formatted Advisory"):
                st.markdown(f'<div class="advisory-box">{advisory_text}</div>', unsafe_allow_html=True)

        if data.get("disclaimer"):
            st.info(f"ℹ️ {data['disclaimer']}")


# ─────────────────────────────────────────────
# CASE EXPLORER  POST /api/search
# ─────────────────────────────────────────────
def page_cases():
    st.markdown("## 📋 Historical Case Explorer")
    st.caption("Hybrid semantic + keyword search over 1,500 verified agricultural cases.")

    with st.form("search_form"):
        query = st.text_input("Search query", placeholder="e.g. High yield Sugarcane Maharashtra drip irrigation")
        c1, c2, c3, c4 = st.columns(4)
        f_state  = c1.selectbox("State",  ["Any"] + STATES)
        f_season = c2.selectbox("Season", ["Any"] + SEASONS)
        f_crop   = c3.selectbox("Crop",   ["Any"] + CROPS_LIST)
        f_topk   = c4.slider("Top-K", 3, 20, 10)
        submitted = st.form_submit_button("🔍 Search Cases", use_container_width=True)

    if submitted:
        if not query.strip():
            st.warning("Enter a search query."); return
        payload = {"query": query.strip(), "top_k": f_topk}
        if f_state  != "Any": payload["state"]  = f_state
        if f_season != "Any": payload["season"] = f_season
        if f_crop   != "Any": payload["crop"]   = f_crop

        with st.spinner("Searching historical database…"):
            data, err = api_post("/api/search", payload)

        if err: st.error(f"⚠️ {err}"); return

        cases = data.get("cases", [])
        st.success(f"✅ Retrieved **{data.get('total_retrieved', len(cases))}** matching cases")
        if cases:
            import pandas as pd
            df = pd.DataFrame(cases)
            show = [c for c in ["case_id","crop","season","state","yield","ph","rainfall","rrf_score"] if c in df.columns]
            st.dataframe(df[show], use_container_width=True, hide_index=True)
        else:
            st.info("No cases matched. Try relaxing your filters.")


# ─────────────────────────────────────────────
# CROP RECOMMENDATION  POST /api/recommendation
# ─────────────────────────────────────────────
def page_recommendation():
    st.markdown("## 🌱 Crop Recommendation")
    st.caption("Get crop suitability rankings for your soil & weather conditions.")

    with st.form("rec_form"):
        c1, c2 = st.columns(2)
        state  = c1.selectbox("State",  STATES)
        season = c2.selectbox("Season", SEASONS)

        st.markdown("**Soil Nutrients (kg/ha)**")
        n1, n2, n3 = st.columns(3)
        N = n1.number_input("Nitrogen (N)",   min_value=0.0, max_value=500.0, value=120.0, step=1.0)
        P = n2.number_input("Phosphorus (P)", min_value=0.0, max_value=500.0, value=60.0,  step=1.0)
        K = n3.number_input("Potassium (K)",  min_value=0.0, max_value=500.0, value=40.0,  step=1.0)

        st.markdown("**Climate**")
        cl1, cl2, cl3 = st.columns(3)
        ph   = cl1.number_input("Soil pH",        min_value=3.0,  max_value=11.0,   value=6.5,  step=0.1)
        rain = cl2.number_input("Rainfall (mm)",   min_value=0.0,  max_value=3000.0, value=800.0,step=10.0)
        temp = cl3.number_input("Temperature (°C)",min_value=5.0,  max_value=50.0,   value=25.0, step=0.5)
        submitted = st.form_submit_button("🌱 Get Recommendations", use_container_width=True)

    if submitted:
        payload = {"state": state, "season": season, "n": N, "p": P, "k": K,
                   "ph": ph, "rainfall": rain, "temperature": temp}
        with st.spinner("Ranking crop candidates…"):
            data, err = api_post("/api/recommendation", payload)

        if err: st.error(f"⚠️ {err}"); return

        candidates = data.get("candidates", [])
        if not candidates:
            st.info("No candidates returned. Try different conditions."); return

        st.success(f"✅ {len(candidates)} crop candidates ranked for **{state}** — **{season}** season")
        for i, cand in enumerate(candidates, 1):
            rl = str(cand.get("risk_level","")).upper()
            rc = "#22c55e" if rl=="LOW" else ("#ef4444" if rl=="HIGH" else "#facc15")
            score = cand.get("suitability_probability", 0)
            st.markdown(f"""
            <div class="agri-card">
              <div style="display:flex;align-items:center;gap:14px">
                <div style="font-size:1.5rem;font-weight:800;color:#39D98A">#{i}</div>
                <div style="flex:1">
                  <div style="font-size:1.05rem;font-weight:700;color:#39D98A">{cand.get('crop','—')}</div>
                  <span style="border:1px solid {rc};border-radius:6px;padding:2px 8px;font-size:0.75rem;color:{rc}">
                    {cand.get('risk_level','—')} Risk
                  </span>
                </div>
                <div style="text-align:right">
                  <div style="font-size:1.6rem;font-weight:800;color:#39D98A">{score*100:.0f}%</div>
                  <div style="font-size:0.74rem;color:#6aaa7a">Suitability</div>
                </div>
              </div>
              <div style="margin-top:10px;height:6px;background:rgba(57,217,138,0.1);border-radius:6px">
                <div style="width:{score*100:.0f}%;height:100%;background:linear-gradient(90deg,#16a34a,#22c55e);border-radius:6px"></div>
              </div>
              <div style="margin-top:8px;font-size:0.82rem;color:#8ab88a">
                Hist. Avg Yield: <b style="color:#39D98A">{cand.get('historical_avg_yield','—')} t/ha</b>
              </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# YIELD PREDICTION  POST /api/prediction
# ─────────────────────────────────────────────
def page_yield():
    st.markdown("## 📈 ML Yield Prediction")
    st.caption("Random Forest Regressor — bounded predictions with 80% confidence interval.")

    with st.form("yield_form"):
        c1, c2, c3 = st.columns(3)
        crop   = c1.selectbox("Crop",   CROPS_LIST)
        state  = c2.selectbox("State",  STATES)
        season = c3.selectbox("Season", SEASONS)

        st.markdown("**Agronomic Inputs**")
        a1, a2, a3 = st.columns(3)
        area = a1.number_input("Area (ha)",        min_value=0.1,  max_value=500.0,  value=5.0,   step=0.5)
        rain = a2.number_input("Rainfall (mm)",    min_value=0.0,  max_value=3000.0, value=900.0, step=10.0)
        temp = a3.number_input("Temperature (°C)", min_value=5.0,  max_value=50.0,   value=27.0,  step=0.5)

        b1, b2, b3 = st.columns(3)
        N    = b1.number_input("Nitrogen (N)",     min_value=0.0,  max_value=500.0, value=100.0, step=1.0)
        P    = b2.number_input("Phosphorus (P)",   min_value=0.0,  max_value=500.0, value=50.0,  step=1.0)
        K    = b3.number_input("Potassium (K)",    min_value=0.0,  max_value=500.0, value=50.0,  step=1.0)

        d1, d2, d3 = st.columns(3)
        ph   = d1.number_input("Soil pH",          min_value=3.0,  max_value=11.0,  value=6.8,   step=0.1)
        hum  = d2.number_input("Humidity (%)",     min_value=10.0, max_value=100.0, value=65.0,  step=1.0)
        fert = d3.number_input("Fertilizer (kg/ha)",min_value=0.0, max_value=1000.0,value=200.0, step=5.0)
        pest = st.number_input("Pesticide (kg/ha)", min_value=0.0, max_value=100.0, value=10.0,  step=0.5)

        submitted = st.form_submit_button("📈 Predict Yield", use_container_width=True)

    if submitted:
        payload = {
            "crop": crop, "state": state, "season": season,
            "area": area, "n": N, "p": P, "k": K,
            "ph": ph, "rainfall": rain, "temperature": temp,
            "humidity": hum, "fertilizer": fert, "pesticide": pest,
        }
        with st.spinner("Running Random Forest regressor…"):
            data, err = api_post("/api/prediction", payload)

        if err: st.error(f"⚠️ {err}"); return

        st.success("✅ Yield prediction complete")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("🌾 Predicted Yield", f"{data.get('predicted_yield','—')} t/ha")
        ci = data.get("expected_range_80_ci", data.get("confidence_interval_80", []))
        if ci: r2.metric("80% CI Range", f"{ci[0]} – {ci[1]} t/ha")
        r3.metric("Std Dev", f"± {data.get('standard_deviation','—')} t/ha")
        r4.metric("Crop", data.get("crop","—"))

        fi = data.get("top_feature_importances", {})
        if fi and isinstance(fi, dict):
            import pandas as pd
            st.markdown("### 🔬 Feature Importances")
            df = pd.DataFrame(list(fi.items()), columns=["Feature","Importance"]).sort_values("Importance",ascending=False)
            st.bar_chart(df.set_index("Feature"))
        elif fi and isinstance(fi, list):
            st.markdown("### 🔬 Key Influencing Factors")
            for f in fi:
                st.markdown(f"- **{f.get('factor',f.get('feature','?'))}** → `{f.get('importance',0):.2f}`")


# ─────────────────────────────────────────────
# RISK & IMPACT ANALYSIS  POST /api/analysis
# ─────────────────────────────────────────────
def page_risk():
    st.markdown("## ⚠️ Risk & Impact Analysis")
    st.caption("Identify limiting factors and agronomic stress for specific crop conditions.")

    with st.form("risk_form"):
        c1, c2, c3 = st.columns(3)
        crop = c1.selectbox("Crop",            CROPS_LIST)
        ph   = c2.number_input("Soil pH",       min_value=3.0,  max_value=11.0,   value=6.5,  step=0.1)
        rain = c3.number_input("Rainfall (mm)", min_value=0.0,  max_value=3000.0, value=750.0,step=10.0)
        temp = st.number_input("Temperature (°C)", min_value=5.0, max_value=50.0, value=28.0, step=0.5)
        submitted = st.form_submit_button("⚠️ Analyze Risk & Factors", use_container_width=True)

    if submitted:
        payload = {"crop": crop, "ph": ph, "rainfall": rain, "temperature": temp}
        with st.spinner("Analyzing agronomic risk factors…"):
            data, err = api_post("/api/analysis", payload)

        if err: st.error(f"⚠️ {err}"); return

        st.success(f"✅ Analysis complete for **{data.get('crop', crop)}**")
        for lf in data.get("limiting_factors", []):
            st.warning(f"⚡ {lf}")
        for rec in data.get("recommendations", []):
            st.success(f"✅ {rec}")
        if not data.get("limiting_factors") and not data.get("recommendations"):
            st.info("Conditions appear optimal. No major limiting factors detected.")


# ─────────────────────────────────────────────
# FEEDBACK  POST /api/feedback
# ─────────────────────────────────────────────
def page_feedback():
    st.markdown("## 💬 Submit Advisory Feedback")
    st.caption("Rate the advisory quality to help improve the system.")

    last = st.session_state.last_advisory or {}
    prefill_query = last.get("query","")
    prefill_crop  = (last.get("recommended_crops",[{}])[0].get("crop","")) if last.get("recommended_crops") else ""

    with st.form("feedback_form"):
        query    = st.text_area("Query you evaluated", value=prefill_query, height=80)
        c1, c2  = st.columns(2)
        rating   = c1.slider("Star Rating ⭐", 1, 5, 5)
        category = c2.selectbox("Feedback Category", [
            "ACCURATE","PARTIALLY_ACCURATE","INACCURATE",
            "HELPFUL","NEEDS_IMPROVEMENT","EXCELLENT",
        ])
        crop_eval = st.selectbox("Crop evaluated",
                                  [""] + CROPS_LIST,
                                  index=(CROPS_LIST.index(prefill_crop)+1) if prefill_crop in CROPS_LIST else 0)
        comments  = st.text_area("Comments / Notes",
                                  placeholder="e.g. Matches regional extension officer recommendations.",
                                  height=100)
        submitted = st.form_submit_button("📨 Submit Feedback", use_container_width=True)

    if submitted:
        if not query.strip():
            st.warning("Please provide the query you are evaluating."); return
        payload = {
            "query":                      query.strip(),
            "rating":                     rating,
            "feedback_category":          category,
            "comments":                   comments.strip(),
            "recommended_crop_evaluated": crop_eval or None,
        }
        with st.spinner("Submitting feedback…"):
            data, err = api_post("/api/feedback", payload)
        if err: st.error(f"⚠️ {err}"); return
        st.success(f"✅ Feedback recorded! ID: `{data.get('feedback_id','—')}`")
        st.balloons()


# ─────────────────────────────────────────────
# SYSTEM EVALUATION
# ─────────────────────────────────────────────
def page_evaluation():
    st.markdown("## 🧪 System Evaluation Benchmark")
    st.caption("Automated evaluation — IR metrics, ML accuracy, LLM Judge, Guardrails.")

    col_run, col_load = st.columns(2)

    with col_run:
        st.markdown("### ▶️ Run Benchmark")
        if st.button("🚀 Run Automated Benchmark", use_container_width=True):
            with st.spinner("Running evaluation suite (20–60 s)…"):
                data, err = api_post("/api/evaluate", {})
            if err: st.error(f"⚠️ {err}")
            else:   _render_eval(data)

    with col_load:
        st.markdown("### 📊 Latest Report")
        if st.button("📥 Load Latest Report", use_container_width=True):
            with st.spinner("Fetching latest report…"):
                data, err = api_get("/api/evaluation/latest")
            if err:   st.error(f"⚠️ {err}")
            elif data: _render_eval(data)
            else:      st.info("No report found. Run a benchmark first.")

    st.markdown("---")
    st.markdown("### 📖 Metrics Reference")
    import pandas as pd
    st.dataframe(pd.DataFrame({
        "Metric":    ["Precision@5","Recall@5","MRR","Hit Rate@5","Yield R²","Guardrail Detection","LLM Judge Score"],
        "Target":    ["> 0.80",     "> 0.75",  "> 0.90","> 0.95","> 0.98","100%","              > 0.90"],
        "Component": ["Hybrid RAG","Vector Index","RRF Reranker","E2E Retrieval","Random Forest","Security Layer","Validation Agent"],
    }), use_container_width=True, hide_index=True)


def _render_eval(data: dict):
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Precision@5",   str(data.get("precision_at_5",  data.get("precision@5","—"))))
    r2.metric("Recall@5",      str(data.get("recall_at_5",     data.get("recall@5","—"))))
    r3.metric("MRR",           str(data.get("mrr","—")))
    r4.metric("Hit Rate@5",    str(data.get("hit_rate_at_5",   data.get("hit_rate@5","—"))))
    r5, r6, r7, r8 = st.columns(4)
    r5.metric("Yield R²",      str(data.get("yield_r2","—")))
    r6.metric("Latency (ms)",  str(data.get("latency_ms","—")))
    r7.metric("Guardrail Det.",str(data.get("guardrail_detection_rate","—")))
    r8.metric("Status",        str(data.get("status","—")).upper())
    if data.get("report_md_path") or data.get("report_json_path"):
        st.caption(f"📁 {data.get('report_md_path', data.get('report_json_path',''))}")


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()

    page = st.session_state.page
    if   page == "Dashboard":              page_dashboard()
    elif page == "Crop Advisory":          page_advisory()
    elif page == "Case Explorer":          page_cases()
    elif page == "Crop Recommendation":    page_recommendation()
    elif page == "Yield Prediction":       page_yield()
    elif page == "Risk & Impact Analysis": page_risk()
    elif page == "Feedback":               page_feedback()
    elif page == "System Evaluation":      page_evaluation()
    else:
        st.info(f"Page '{page}' not found.")


if __name__ == "__main__":
    main()
