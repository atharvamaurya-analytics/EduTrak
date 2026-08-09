import streamlit as st
import pandas as pd
import analytics
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(
    page_title="EduTrak | Analytics Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

analytics.ensure_interventions_table()

# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS & THEME (Obsidian & Amber)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── BASE RESET ── */
html, body, [class*="css"] { font-family: 'Inter', system-ui, -apple-system, sans-serif !important; }
.stApp { background-color: #09090b !important; color: #f4f4f5 !important; }
.main .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1440px !important; }
header[data-testid="stHeader"] { background-color: #09090b !important; border-bottom: 1px solid #27272a !important; }

/* ── SIDEBAR (App Drawer Style) ── */
section[data-testid="stSidebar"] {
    background: #09090b !important;
    border-right: 1px solid #27272a !important;
    width: 280px !important;
}
section[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem !important; }
/* The plain `---` dividers (st.markdown("---")) were rendering as unstyled
   browser-default <hr> — a stray light gray line that didn't match the
   theme's border color anywhere it appeared. Styled to match instead of
   removing, since it's a real section separator (profile → nav → filters). */
hr { border: none !important; border-top: 1px solid #27272a !important; margin: 10px 0 !important; }
section[data-testid="stSidebar"] hr { margin: 8px 0 14px 0 !important; }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, 
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div { color: #a1a1aa !important; }

/* Custom Nav Styling — a robust, ARIA-role-based approach only (the previous
   baseweb-class-chain rules below were removed: they matched a *nested* div
   inside the same <label> this targets, so both sets of padding stacked and
   made the selected pill much taller than the text needed). */
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 0 !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    display: block !important; color: #a1a1aa !important; font-size: 14px !important;
    font-weight: 500 !important; line-height: 1.3 !important; padding: 8px 14px !important;
    border-radius: 8px !important; margin: 1px 0 !important; transition: all 0.2s ease !important; cursor: pointer !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label p,
section[data-testid="stSidebar"] div[role="radiogroup"] label span,
section[data-testid="stSidebar"] div[role="radiogroup"] label div { color: inherit !important; font-weight: inherit !important; margin: 0 !important; padding: 0 !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: #18181b !important; color: #f4f4f5 !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: #18181b !important; color: #fbbf24 !important; font-weight: 600 !important; border-left: 3px solid #fbbf24 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span { color: #fbbf24 !important; font-weight: 600 !important; }

/* ── BENTO GRID METRICS ── */
div[data-testid="stMetric"] {
    background: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    transition: transform 0.2s ease, border-color 0.2s ease !important;
}
div[data-testid="stMetric"]:hover { border-color: #3f3f46 !important; transform: translateY(-2px) !important; }
p[data-testid="stMetricLabel"] { color: #a1a1aa !important; font-size: 12px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
div[data-testid="stMetricValue"] { color: #f4f4f5 !important; font-size: 28px !important; font-weight: 700 !important; }
div[data-testid="stMetricDelta"] { color: #34d399 !important; font-size: 12px !important; font-weight: 600 !important; }

/* ── HEADINGS ── */
h1 { color: #f4f4f5 !important; font-size: 28px !important; font-weight: 700 !important; letter-spacing: -0.5px; margin-bottom: 1.5rem !important; }
h2 { color: #e4e4e7 !important; font-size: 18px !important; font-weight: 600 !important; }
h3 { color: #d4d4d8 !important; font-size: 15px !important; font-weight: 600 !important; }

/* ── TYPOGRAPHY SCALE (body / small / caption) ──
   Keeps text hierarchy consistent everywhere: headings (above) for
   section titles, body for normal copy, small/caption for hints
   and metadata — mirrors the H1(28)/H2(18)/H3(15) step-down. */
p, .stMarkdown p { color: #d4d4d8 !important; font-size: 14px !important; line-height: 1.65 !important; }
small, .stCaption, div[data-testid="stCaptionContainer"] { color: #71717a !important; font-size: 12px !important; }

/* ── BUTTONS ── */
/* Was #fbbf24 (amber-400) — same bright shade used everywhere as an accent,
   which made buttons feel like highlighter-yellow. Deepened to amber-600/700
   so it still reads as "the amber accent" but isn't glaring. */
.stButton > button {
    background: #d97706 !important; color: #fef3c7 !important;
    border: none !important; padding: 10px 24px !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 14px !important;
    transition: all 0.2s ease !important;
}
.stButton > button p, .stButton > button span, .stButton > button div { color: #fef3c7 !important; }
.stButton > button:hover { background: #b45309 !important; box-shadow: 0 0 12px rgba(180, 83, 9, 0.35) !important; transform: translateY(-1px) !important; }
.stButton > button:hover p, .stButton > button:hover span, .stButton > button:hover div { color: #fef3c7 !important; }

/* ── TABS ── */
/* [role="tab"]/[role="tablist"] added as an ARIA-based fallback alongside the
   baseweb selectors — same reasoning as the sidebar nav fix above, in case the
   underlying tab library changed. !important added throughout + p/span text
   color forced so the global `p{color:#d4d4d8}` rule can't wash these out. */
div[data-testid="stTabs"] [data-baseweb="tab-list"],
div[data-testid="stTabs"] [role="tablist"] { gap: 4px !important; border-bottom: 1px solid #27272a !important; }
div[data-testid="stTabs"] [data-baseweb="tab"],
div[data-testid="stTabs"] [role="tab"] {
    height: 40px !important; background-color: transparent !important; border-radius: 6px 6px 0 0 !important;
    color: #71717a !important; padding: 0 16px !important; font-size: 13px !important; font-weight: 500 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] p, div[data-testid="stTabs"] [data-baseweb="tab"] span,
div[data-testid="stTabs"] [role="tab"] p, div[data-testid="stTabs"] [role="tab"] span { color: inherit !important; font-weight: inherit !important; }
div[data-testid="stTabs"] [aria-selected="true"] {
    background-color: #18181b !important; color: #fbbf24 !important;
    border-bottom: 2px solid #fbbf24 !important; font-weight: 600 !important;
}
div[data-testid="stTabs"] [aria-selected="true"] p, div[data-testid="stTabs"] [aria-selected="true"] span { color: #fbbf24 !important; font-weight: 600 !important; }

/* ── INPUT FIELDS ── */
div[data-testid="stTextInput"] > div > div > input, div[data-testid="stSelectbox"] > div > div > div, div[data-testid="stFileUploader"] {
    background-color: #18181b !important; color: #f4f4f5 !important;
    border: 1px solid #27272a !important; border-radius: 8px !important; font-size: 14px !important;
}
div[data-testid="stTextInput"] > div > div > input::placeholder { color: #52525b !important; }
div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label { color: #a1a1aa !important; font-size: 13px !important; font-weight: 500 !important; }

/* ── CARDS & CONTAINERS ── */
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.dashboard-card {
    background: #18181b; border: 1px solid #27272a; border-radius: 12px;
    padding: 24px; margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: border-color 0.2s ease, transform 0.2s ease;
    animation: fadeIn 0.35s ease-out;
}
.dashboard-card:hover { border-color: #3f3f46; transform: translateY(-2px); }
/* ── CHART IMAGES ── uniform height regardless of each chart's own aspect ratio.
   Root cause of the size mismatch: figsize was already identical (6,4) for both
   charts, but matplotlib's tight-bbox cropping trims each PNG differently based
   on its own labels (a pie's radial labels vs a line chart's axis labels), so
   the two images ended up with different final aspect ratios despite equal
   figsize. Forcing a fixed display height sidesteps that entirely. */
div[data-testid="stImage"] img { width: 100% !important; max-height: 500px !important; height: auto !important; object-fit: contain !important; }
.profile-card {
    background: linear-gradient(135deg, #18181b 0%, #09090b 100%);
    border: 1px solid #27272a; border-radius: 16px;
    padding: 28px; margin-bottom: 24px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    animation: fadeIn 0.35s ease-out;
}
.profile-name { font-size: 22px; font-weight: 700; color: #fbbf24; margin-bottom: 4px; }
.profile-tag { font-size: 14px; color: #a1a1aa; }
.badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin: 3px; }
.badge-amber  { background: #451a03; color: #fbbf24; border: 1px solid #78350f; }
.badge-emerald { background: #064e3b; color: #34d399; border: 1px solid #065f46; }
.badge-sky  { background: #0c4a6e; color: #38bdf8; border: 1px solid #075985; }
.badge-rose { background: #4c0519; color: #fda4af; border: 1px solid #881337; }

/* ── EMPTY STATES ── (reusable — icon + message, centred, low-emphasis) */
.empty-state { text-align: center; padding: 40px 20px; color: #52525b; }
.empty-state .empty-icon { font-size: 32px; margin-bottom: 8px; display: block; }
.empty-state .empty-text { font-size: 13px; color: #71717a; }

/* ── SECTION HEADER ── */
.section-header {
    font-size: 13px; font-weight: 600; color: #fbbf24;
    border-left: 3px solid #fbbf24; padding-left: 12px;
    margin: 24px 0 16px 0; letter-spacing: 0.5px; text-transform: uppercase;
}

/* ── INFO BOXES ── */
.custom-info {
    background: #0c4a6e11; border: 1px solid #075985; border-left: 4px solid #38bdf8;
    border-radius: 8px; padding: 14px 18px; margin: 12px 0;
    font-size: 13px; color: #bae6fd !important; line-height: 1.6;
}
.custom-warn {
    background: #42200611; border: 1px solid #713f12; border-left: 4px solid #fbbf24;
    border-radius: 8px; padding: 14px 18px; margin: 12px 0;
    font-size: 13px; color: #fde68a !important; line-height: 1.6;
}
.custom-success {
    background: #064e3b11; border: 1px solid #065f46; border-left: 4px solid #34d399;
    border-radius: 8px; padding: 14px 18px; margin: 12px 0;
    font-size: 13px; color: #a7f3d0 !important; line-height: 1.6;
}
.custom-danger {
    background: #4c051911; border: 1px solid #881337; border-left: 4px solid #f43f5e;
    border-radius: 8px; padding: 14px 18px; margin: 12px 0;
    font-size: 13px; color: #fecdd3 !important; line-height: 1.6;
}

/* ── PROGRESS BARS ── */
.prog-label { font-size: 13px; color: #a1a1aa; margin-bottom: 4px; }
.prog-val   { font-size: 13px; color: #f4f4f5; font-weight: 600; float: right; }

/* ── FOOTER ── */
.footer {
    position: fixed; left: 0; bottom: 0; width: 100%;
    background: #09090b; color: #52525b;
    text-align: center; padding: 12px 0; font-size: 12px;
    border-top: 1px solid #27272a; z-index: 999;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MATPLOTLIB DARK THEME (Matches Obsidian & Amber)
# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# CHART COLOR PALETTE (matches the Obsidian & Amber theme)
# Named so chart colors have one consistent meaning across the whole app:
#   primary   -> the main/"you" series (amber, matches the accent color)
#   secondary -> comparison series, e.g. "Class Avg" (sky blue)
#   positive  -> good/low-risk values (emerald)
#   negative  -> risk/warning values (rose)
# ═══════════════════════════════════════════════════════════════════════════════
CHART_PALETTE = {
    "primary":   "#fbbf24",  # amber — same as the UI accent color
    "secondary": "#38bdf8",  # sky blue — used for comparison series
    "positive":  "#34d399",  # emerald — good outcomes / low risk
    "negative":  "#f43f5e",  # rose — risk / warning values
}

plt.rcParams.update({
    'figure.facecolor': '#09090b',
    'axes.facecolor':   '#18181b',
    'axes.edgecolor':   '#27272a',
    'axes.labelcolor':  '#a1a1aa',
    'xtick.color':      '#a1a1aa',
    'ytick.color':      '#a1a1aa',
    'text.color':       '#f4f4f5',
    'grid.color':       '#27272a',
    'grid.alpha':       0.4,
    'font.family':      'sans-serif',
    'font.sans-serif':  ['Inter', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial']
})

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH & SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
for k, v in [('logged_in', False), ('role', None), ('username', None), ('page', 'Dashboard')]:
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# AI RISK PREDICTOR — Session-state defaults (enable load-by-ID + what-if persistence)
# ═══════════════════════════════════════════════════════════════════════════════
_PREDICTOR_DEFAULTS = {
    'pred_age': 22, 'pred_gender': 'Male', 'pred_device': 'Laptop', 'pred_country': 'Australia',
    'pred_internet': 50.0, 'pred_study_hours': 10.0, 'pred_logins': 7, 'pred_session': 35.0,
    'pred_attendance': 0.75, 'pred_quiz': 60.0, 'pred_grade': 60.0, 'pred_engagement': 6.0,
    'pred_video': 250.0, 'pred_assignments': 5, 'pred_forum': 8, 'pred_quiz_attempts': 5
}
for k, v in _PREDICTOR_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def login():
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.title("🎓 EduTrak")
    st.sidebar.caption("Analytics Portal")
    st.sidebar.markdown("---")
    
    mode = st.sidebar.radio(" ", ["Login", "Sign Up"], horizontal=True, key="login_mode_unique")
    
    if mode == "Login":
        st.sidebar.subheader("Welcome Back")
        with st.sidebar.form(key="login_form"):
            u = st.text_input("Username", key="lu", placeholder="Enter username")
            p = st.text_input("Password", type="password", key="lp", placeholder="Enter password")
            submitted = st.form_submit_button(" Login", use_container_width=True)
            if submitted:
                user = analytics.authenticate_user(u, p)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username  = user[0]
                    st.session_state.role      = user[1]
                    st.rerun()
                else:
                    st.sidebar.error("❌ Invalid credentials")
    else:
        st.sidebar.subheader("Create Account")
        with st.sidebar.form(key="signup_form"):
            nu  = st.text_input("Username", key="su", placeholder="Choose a username")
            np_ = st.text_input("Password", type="password", key="sp", placeholder="Choose a password")
            cp  = st.text_input("Confirm Password", type="password", key="sc", placeholder="Repeat password")
            nr  = st.selectbox("Role", ["Student", "Admin/Instructor"])
            submitted_su = st.form_submit_button("✅ Create Account", use_container_width=True)
            if submitted_su:
                if not nu or not np_: st.sidebar.error("Fill all fields")
                elif np_ != cp: st.sidebar.error("Passwords don't match")
                elif analytics.user_exists(nu): st.sidebar.error("Username already taken")
                else:
                    analytics.create_user(nu, np_, nr)
                    st.sidebar.success("Account created! Please login.")

def logout():
    for k in ['logged_in', 'role', 'username', 'page']:
        st.session_state[k] = None if k != 'logged_in' else False
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def prog_bar(label, val, max_val, color="#fbbf24"):
    pct = min(val / max_val * 100, 100) if max_val else 0
    st.markdown(f"""
    <div style="margin:8px 0">
        <span class="prog-label">{label}</span>
        <span class="prog-val">{val:.1f} / {max_val:.1f}</span>
        <div style="clear:both;background:#09090b;border-radius:6px;height:8px;margin-top:6px;border:1px solid #27272a">
            <div style="width:{pct:.1f}%;background:{color};border-radius:6px;height:8px;
            box-shadow:0 0 10px {color}44;transition:width 0.5s"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def csv_download_button(df, label, filename, key=None):
    """Reusable 'export to CSV' button — used on Risk List, Student Lookup/My Progress, and Interventions."""
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label, data=csv_bytes, file_name=filename, mime='text/csv',
        use_container_width=True, key=key
    )

def risk_badge(label):
    cls = {"Low Risk": "badge-emerald", "Medium Risk": "badge-amber", "High Risk": "badge-rose"}.get(label, "badge-sky")
    return f'<span class="badge {cls}">{label}</span>'

def radar_chart(labels, student_vals, class_vals, title=""):
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    sv = student_vals + student_vals[:1]
    cv = class_vals  + class_vals[:1]
    
    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    ax.set_facecolor('#18181b')
    fig.patch.set_facecolor('#09090b')
    
    ax.plot(angles, sv, 'o-', linewidth=2, color='#fbbf24', label='You')
    ax.fill(angles, sv, alpha=0.15, color='#fbbf24')
    ax.plot(angles, cv, 'o--', linewidth=2, color='#38bdf8', label='Class Avg')
    ax.fill(angles, cv, alpha=0.05, color='#38bdf8')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=9, color='#a1a1aa')
    ax.set_yticklabels([])
    ax.grid(color='#27272a', alpha=0.5)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1),
              facecolor='#18181b', edgecolor='#27272a', labelcolor='#f4f4f5', fontsize=9)
    if title:
        ax.set_title(title, color='#fbbf24', pad=15, fontsize=11, fontweight='600')
    return fig

def render_student_profile(sid, active_behavior_table, active_engagement_table, admin_view=False):
    """
    Renders the full student profile: profile card, Overview/Behavior/Engagement/Compare
    tabs, a CSV export of the record, and — for admin_view only — a 'Flag for Outreach'
    form that writes into the interventions log.
    Shared by 'My Progress' (student looks up their own ID) and 'Student Lookup'
    (admin looks up any ID) so the dashboard logic lives in exactly one place.
    """
    with st.spinner("Loading student data…"):
        sb = analytics.get_student_behavior(sid, active_behavior_table)
        se = analytics.get_student_engagement(sid, active_engagement_table)
    found_b = not sb.empty
    found_e = not se.empty
    if not found_b and not found_e:
        st.error(f"❌ Student ID **{sid}** not found in any dataset.")
        return

    age    = int(sb['Age'].iloc[0])    if found_b and 'Age'    in sb.columns else (int(se['age'].iloc[0])    if found_e else "—")
    gender = sb['Gender'].iloc[0]      if found_b and 'Gender' in sb.columns else (se['gender'].iloc[0]      if found_e else "—")
    country= sb['Country'].iloc[0]     if found_b and 'Country' in sb.columns else (se['country'].iloc[0]    if found_e else "—")
    edu    = sb['Education_Level'].iloc[0] if found_b and 'Education_Level' in sb.columns else "—"
    field  = sb['Field_of_Study'].iloc[0]  if found_b and 'Field_of_Study'  in sb.columns else "—"
    platform = sb['Platform_Used'].iloc[0] if found_b and 'Platform_Used'   in sb.columns else "—"
    device = (sb['Device_Used'].iloc[0] if found_b and 'Device_Used' in sb.columns else se['device_type'].iloc[0] if found_e and 'device_type' in se.columns else "—")
    enroll = sb['Enrollment_Date'].iloc[0] if found_b and 'Enrollment_Date' in sb.columns else "—"

    st.markdown(f"""
    <div class="profile-card">
      <div class="profile-name"> Student #{sid}</div>
      <div class="profile-tag">{age} yrs &nbsp;·&nbsp; {gender} &nbsp;·&nbsp; {country}</div>
      <br>
      <span class="badge badge-sky"> {edu}</span>
      <span class="badge badge-sky">🔬 {field}</span>
      <span class="badge badge-emerald">💻 {platform}</span>
      <span class="badge badge-amber">📱 {device}</span>
      <span class="badge badge-sky">📅 Enrolled: {enroll}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Export + (admin-only) outreach flag ──
    combined = pd.concat([sb.reset_index(drop=True), se.reset_index(drop=True)], axis=1) if (found_b and found_e) else (sb if found_b else se)
    act1, act2 = st.columns([1, 1]) if admin_view else st.columns([1, 3])
    with act1:
        csv_download_button(combined, "⬇️ Export CSV", f"student_{sid}_report.csv", key=f"export_{sid}_{admin_view}")
    if admin_view:
        with act2:
            with st.expander("🚩 Flag for Outreach"):
                with st.form(key=f"flag_form_{sid}"):
                    fpriority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1, key=f"fp_{sid}")
                    fnote = st.text_area("Note", placeholder="e.g. Attendance dropped sharply this month, needs a check-in call.", key=f"fn_{sid}")
                    fsubmit = st.form_submit_button("🚩 Log Outreach Flag", use_container_width=True)
                    if fsubmit:
                        analytics.create_intervention(sid, st.session_state.username, fnote, fpriority)
                        st.success(f"✅ Student {sid} flagged for outreach ({fpriority} priority).")

    tab_overview, tab_behavior, tab_engagement, tab_compare = st.tabs(["📊 Overview", "📘 Behavior", "📈 Engagement", "🆚 Compare"])

    with tab_overview:
        st.markdown('<div class="section-header">Quick Snapshot</div>', unsafe_allow_html=True)
        completion = float(sb['Course_Completion_Rate(%)'].iloc[0]) if found_b and 'Course_Completion_Rate(%)' in sb.columns else None
        final_g    = float(se['final_grade'].iloc[0])                if found_e and 'final_grade' in se.columns else None
        eng_score  = float(se['engagement_score'].iloc[0])           if found_e and 'engagement_score' in se.columns else None
        att_rate   = float(se['attendance_rate'].iloc[0]) * 100      if found_e and 'attendance_rate' in se.columns else None
        dropout    = int(se['dropout'].iloc[0])                       if found_e and 'dropout' in se.columns else None

        m1, m2, m3, m4 = st.columns(4)
        if completion is not None: m1.metric("✅ Course Completion", f"{completion:.1f}%")
        if final_g    is not None: m2.metric("🎯 Final Grade",       f"{final_g:.1f}")
        if eng_score  is not None: m3.metric("⚡ Engagement Score",  f"{eng_score:.2f}")
        if att_rate   is not None: m4.metric("🏫 Attendance",        f"{att_rate:.1f}%")

        if dropout is not None:
            if dropout == 1: st.markdown('<div class="custom-danger">⚠️ <b>High Dropout Risk Detected</b> — Reach out to your instructor for support.</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="custom-success">✅ <b>On Track</b> — No dropout risk detected. Keep up the great work!</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Performance Bars</div>', unsafe_allow_html=True)
        if completion is not None: prog_bar("Course Completion (%)", completion, 100, "#fbbf24")
        if final_g    is not None: prog_bar("Final Grade (out of 100)", final_g, 100, "#34d399")
        if att_rate   is not None: prog_bar("Attendance Rate (%)", att_rate, 100, "#38bdf8")
        if eng_score  is not None: prog_bar("Engagement Score (out of 10)", eng_score, 10, "#f43f5e")

    with tab_behavior:
        if not found_b: st.warning("Behavior data not found.")
        else:
            r = sb.iloc[0]
            st.markdown('<div class="section-header">Learning Behavior Details</div>', unsafe_allow_html=True)
            b_cols = {"Daily Learning Hours": ("Daily_Learning_Hours", "⏱️"), "Quizzes Attempted": ("Quizzes_Attempted", "📝"), "Assignments Submitted": ("Assignments_Submitted", "📋"), "Course Completion Rate": ("Course_Completion_Rate(%)","✅"), "Satisfaction Score (1-5)": ("Satisfaction_Score(1-5)", "⭐")}
            cols_row = st.columns(3)
            i = 0
            for label, (col, icon) in b_cols.items():
                if col in r.index:
                    cols_row[i % 3].metric(f"{icon} {label}", f"{r[col]}")
                    i += 1
            st.markdown('<div class="section-header">Percentile Ranks</div>', unsafe_allow_html=True)
            pcols = st.columns(3)
            for idx_, (label, (col, _)) in enumerate(b_cols.items()):
                if col in r.index:
                    pct = analytics.get_percentile(float(r[col]), active_behavior_table, col)
                    pcols[idx_ % 3].metric(f"📊 {label}", f"Top {100-pct:.0f}%", f"{pct:.0f}th percentile")

    with tab_engagement:
        if not found_e: st.warning("Engagement data not found.")
        else:
            r = se.iloc[0]
            st.markdown('<div class="section-header">Engagement & Academic Details</div>', unsafe_allow_html=True)
            e_metrics = {"Study Hours/Week": ("study_hours_weekly", "📖"), "Logins/Week": ("login_frequency_weekly", "🔐"), "Avg Session (min)": ("avg_session_duration_min", ""), "Video Watch (min)": ("video_watch_time_min", "🎥"), "Assignments": ("assignments_submitted", "📋"), "Forum Posts": ("forum_posts", "💬"), "Avg Quiz Score": ("avg_quiz_score", "🎯"), "Attendance Rate (%)": ("attendance_rate", ""), "Engagement Score": ("engagement_score", "⚡"), "Final Grade": ("final_grade", "🏆")}
            cols_ = st.columns(4)
            for idx_, (label, (col, icon)) in enumerate(e_metrics.items()):
                if col in r.index:
                    v = r[col]
                    disp = f"{float(v)*100:.1f}%" if col == 'attendance_rate' else f"{float(v):.2f}"
                    cols_[idx_ % 4].metric(f"{icon} {label}", disp)

            st.markdown('<div class="section-header">Engagement Radar</div>', unsafe_allow_html=True)
            radar_cols = ['study_hours_weekly','login_frequency_weekly','avg_quiz_score','attendance_rate','engagement_score','final_grade']
            radar_cols = [c for c in radar_cols if c in r.index]
            if radar_cols:
                try:
                    cl_e = analytics.get_class_stats(active_engagement_table, radar_cols)
                    def norm(col_n, val):
                        mx = cl_e.get(f'max_{col_n}', val) or 1
                        return float(val) / float(mx)
                    s_norm   = [norm(c, r[c]) for c in radar_cols]
                    avg_norm = [norm(c, cl_e.get(f'avg_{c}', 0)) for c in radar_cols]
                    short_labels = ['Study Hrs','Logins','Quiz Score','Attendance','Engagement','Final Grade'][:len(radar_cols)]
                    rc1, rc2 = st.columns([1, 1])
                    with rc1:
                        fig = radar_chart(short_labels, s_norm, avg_norm, "You vs Class Avg")
                        st.pyplot(fig)
                    with rc2:
                        st.markdown('<div class="section-header">Percentile Ranks</div>', unsafe_allow_html=True)
                        for col in radar_cols:
                            pct = analytics.get_percentile(float(r[col]), active_engagement_table, col)
                            nice = col.replace('_', ' ').title()
                            color = "#34d399" if pct >= 60 else ("#fbbf24" if pct >= 40 else "#f43f5e")
                            st.markdown(f"""<div style="margin:6px 0"><span style="color:#a1a1aa;font-size:13px">{nice}</span><span style="float:right;color:{color};font-weight:700;font-size:13px">{pct:.0f}th %ile</span><div style="clear:both;background:#09090b;border-radius:6px;height:8px;margin-top:4px;border:1px solid #27272a"><div style="width:{pct}%;background:{color};border-radius:6px;height:8px"></div></div></div>""", unsafe_allow_html=True)
                except Exception: pass

    with tab_compare:
        st.markdown('<div class="section-header">How You Stack Up Against the Class</div>', unsafe_allow_html=True)
        if found_e:
            r = se.iloc[0]
            try:
                key_cols = ['study_hours_weekly','video_watch_time_min','assignments_submitted','final_grade','engagement_score']
                key_cols = [c for c in key_cols if c in r.index]
                cl_e = analytics.get_class_stats(active_engagement_table, key_cols)
                fig, axes = plt.subplots(1, len(key_cols), figsize=(14, 4))
                if len(key_cols) == 1: axes = [axes]
                for ax_, col in zip(axes, key_cols):
                    you_v = float(r[col]); avg_v = float(cl_e.get(f'avg_{col}', 0))
                    ax_.bar(['You','Class\nAvg'], [you_v, avg_v], color=['#fbbf24','#38bdf8'], alpha=0.85, edgecolor='#09090b', linewidth=1.5)
                    ax_.set_title(col.replace('_',' ').title(), fontsize=9, color='#a1a1aa')
                    for bar_ in ax_.patches: ax_.text(bar_.get_x() + bar_.get_width()/2, bar_.get_height() + 0.01 * bar_.get_height(), f"{bar_.get_height():.1f}", ha='center', va='bottom', fontsize=8, color='#f4f4f5')
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as ex: st.error(f"Comparison error: {ex}")

        st.markdown('<div class="section-header"> Personalised Recommendations</div>', unsafe_allow_html=True)
        recs = []
        try:
            if found_e:
                r = se.iloc[0]
                if 'study_hours_weekly' in r.index:
                    cl_s = analytics.get_class_stats(active_engagement_table, ['study_hours_weekly'])
                    avg_s = cl_s['avg_study_hours_weekly']
                    if float(r['study_hours_weekly']) < float(avg_s): recs.append(("📖 Study More", f"You study {float(r['study_hours_weekly']):.1f} hrs/week vs class avg {float(avg_s):.1f}. Try adding 2–3 focused hours.", "warn"))
                if 'forum_posts' in r.index and float(r['forum_posts']) < 5: recs.append((" Be More Active", "You have fewer forum posts than average. Participating in discussions improves retention by up to 20%.", "info"))
                if 'attendance_rate' in r.index and float(r['attendance_rate']) < 0.75: recs.append((" Improve Attendance", f"Your attendance is {float(r['attendance_rate'])*100:.1f}%. Aim for above 80% to stay on track.", "danger"))
            if found_b:
                r_b = sb.iloc[0]
                if 'Course_Completion_Rate(%)' in r_b.index and float(r_b['Course_Completion_Rate(%)']) < 50: recs.append(("✅ Boost Completion", f"Only {float(r_b['Course_Completion_Rate(%)']):.1f}% course completed. Set weekly goals to stay consistent.", "danger"))
        except Exception: pass
        if not recs: st.markdown('<div class="custom-success">🌟 Excellent! You\'re performing well across all metrics. Keep it up!</div>', unsafe_allow_html=True)
        else:
            css_map = {"warn":"custom-warn","info":"custom-info","danger":"custom-danger"}
            for title_, msg_, typ_ in recs: st.markdown(f'<div class="{css_map[typ_]}"><b>{title_}</b><br>{msg_}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NOT LOGGED IN
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    # ═══════════════════════════════════════════════════════════════════
    # INTERACTIVE LANDING PAGE
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("""
    <style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(251, 191, 36, 0.1); }
        50% { box-shadow: 0 0 40px rgba(251, 191, 36, 0.3); }
    }
    .hero-container {
        text-align: center;
        padding: 40px 20px 30px;
        animation: fadeInUp 0.8s ease-out;
    }
    .hero-title {
        font-size: 52px;
        font-weight: 800;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 12px;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 18px;
        color: #a1a1aa;
        margin-bottom: 32px;
        font-weight: 400;
    }
    .hero-badge {
        display: inline-block;
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 50px;
        padding: 8px 20px;
        font-size: 13px;
        color: #fbbf24;
        margin: 0 6px 12px;
        animation: pulse-glow 3s ease-in-out infinite;
    }
    .stat-card {
        background: linear-gradient(135deg, #18181b 0%, #09090b 100%);
        border: 1px solid #27272a;
        border-radius: 16px;
        padding: 24px 16px;
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out backwards;
    }
    .stat-card:hover {
        border-color: #fbbf24;
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(251, 191, 36, 0.1);
    }
    .stat-number {
        font-size: 36px;
        font-weight: 800;
        color: #fbbf24;
        line-height: 1;
    }
    .stat-label {
        font-size: 12px;
        color: #a1a1aa;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .feature-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 28px 24px;
        transition: all 0.3s ease;
        animation: fadeInUp 0.7s ease-out backwards;
    }
    .feature-card:hover {
        border-color: #3f3f46;
        transform: translateY(-6px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    .feature-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 16px;
        font-weight: 700;
        color: #f4f4f5;
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 13px;
        color: #a1a1aa;
        line-height: 1.6;
    }
    .security-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #064e3b22;
        border: 1px solid #065f46;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        color: #34d399;
        margin: 4px;
    }
    .divider-line {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #27272a 50%, transparent 100%);
        margin: 40px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div style="font-size: 64px; margin-bottom: 8px; animation: float 3s ease-in-out infinite;">🎓</div>
        <div class="hero-title">EduTrak</div>
        <div class="hero-subtitle">Transforming Raw Student Data into Actionable Intelligence</div>
        <div>
            <span class="hero-badge">🔮 AI-Powered Predictions</span>
            <span class="hero-badge">📊 Real-Time Analytics</span>
            <span class="hero-badge">🛡️ Enterprise Security</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

    # Animated Stats
    st.markdown("<h2 style='text-align:center; color:#f4f4f5; font-size:22px; margin-bottom:24px;'>📈 Platform at a Glance</h2>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("""
        <div class="stat-card" style="animation-delay: 0.1s">
            <div class="stat-number">2,500+</div>
            <div class="stat-label">Students Tracked</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class="stat-card" style="animation-delay: 0.2s">
            <div class="stat-number">95%</div>
            <div class="stat-label">Model Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown("""
        <div class="stat-card" style="animation-delay: 0.3s">
            <div class="stat-number">150+</div>
            <div class="stat-label">Countries Covered</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown("""
        <div class="stat-card" style="animation-delay: 0.4s">
            <div class="stat-number">4.9★</div>
            <div class="stat-label">User Rating</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

    # Feature Cards
    st.markdown("<h2 style='text-align:center; color:#f4f4f5; font-size:22px; margin-bottom:24px;'>🚀 Core Capabilities</h2>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.1s">
            <div class="feature-icon">🔮</div>
            <div class="feature-title">AI Dropout Predictor</div>
            <div class="feature-desc">RandomForest model with 95% ROC-AUC predicts dropout risk in real-time from 16+ engagement features.</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.2s">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">At-Risk Identification</div>
            <div class="feature-desc">Auto-flag students with Low/Medium/High risk labels. One-click intervention logging for instructors.</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.3s">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Visual Analytics</div>
            <div class="feature-desc">Interactive heatmaps, scatter plots, radar charts & percentile rankings — dark-themed & responsive.</div>
        </div>
        """, unsafe_allow_html=True)

    f4, f5, f6 = st.columns(3)
    with f4:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.4s">
            <div class="feature-icon">📁</div>
            <div class="feature-title">Dynamic Datasets</div>
            <div class="feature-desc">Upload CSV datasets on-the-fly. Auto-validation, null-handling & SQLite integration with zero downtime.</div>
        </div>
        """, unsafe_allow_html=True)
    with f5:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.5s">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Role-Based Access</div>
            <div class="feature-desc">PBKDF2 password hashing, SQL injection guards via allow-list validation, Admin/Student segregation.</div>
        </div>
        """, unsafe_allow_html=True)
    with f6:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.6s">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">What-If Simulator</div>
            <div class="feature-desc">Adjust any slider to simulate student profiles. Instant risk recalculation with personalised recommendations.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

    # Security Section
    st.markdown("<h2 style='text-align:center; color:#f4f4f5; font-size:22px; margin-bottom:20px;'>🔐 Security & Compliance</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; margin-bottom:20px;">
        <span class="security-badge">🛡️ SQL Injection Guard</span>
        <span class="security-badge">🔐 PBKDF2-SHA256 Hashing</span>
        <span class="security-badge">👤 Role-Based Access</span>
        <span class="security-badge">📋 Dynamic Validation</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align:center; color:#71717a; font-size:13px; max-width:600px; margin:0 auto;">
        Every table/column name is validated against SQLite's <code>sqlite_master</code> before query execution. 
        Passwords use per-user salt with 100,000 iterations. Legacy plaintext rows auto-migrate to hashes on first login.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

    # CTA
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 30px;">
        <p style="color:#a1a1aa; font-size:16px; margin-bottom:16px;">👋 Ready to explore? Use the sidebar to log in or create an account.</p>
        <div style="font-size:13px; color:#52525b;">Default: <b>admin</b> / <b>admin</b> &nbsp;·&nbsp; <b>student</b> / <b>student</b></div>
    </div>
    """, unsafe_allow_html=True)

    login()

    c1, c2 = st.columns([2, 1])
    with c1:
        st.title("Welcome to EduTrak 🎓")
        st.subheader("Empowering Education through Data-Driven Insights")
        st.markdown("""
        ### About the Project
        EduTrak is a cutting-edge educational analytics portal that transforms raw student data
        into actionable intelligence. Whether you're an administrator or a student, EduTrak gives
        you the tools to achieve academic excellence.
        
        #### Key Features:
        - **Academic Excellence** — Study habits vs. final grades correlation
        - **Engagement & Risk** — At-risk student identification
        - **Personalized Progress** — Full student dashboard with charts & percentile ranks
        - **Dynamic Management** — Upload & preprocess datasets on the fly
        """)
    with c2:
        st.info("👋 **Getting Started**\n\nUse the sidebar to log in or create an account.")
# ═══════════════════════════════════════════════════════════════════════════════
# LOGGED IN
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.caption(f"Role: {st.session_state.role}")
    st.sidebar.markdown("---")
    
    is_admin = st.session_state.role == "Admin/Instructor"
    nav_opts = ["Dashboard", "Academic Excellence", "Risk & Engagement", "Student Lookup", "Interventions", "Datasets"] if is_admin else ["My Progress"]
    selection = st.sidebar.radio("Navigation", nav_opts)
    
    selected_countries      = []
    active_behavior_table   = 'behavior'
    active_engagement_table = 'engagement'
    
    if is_admin:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Data Source")
        datasets_df = analytics.get_available_datasets()
        b_opts = datasets_df[datasets_df['type'] == 'behavior']
        e_opts = datasets_df[datasets_df['type'] == 'engagement']
        sel_b  = st.sidebar.selectbox("Behavior Dataset", b_opts['name'].tolist())
        sel_e  = st.sidebar.selectbox("Engagement Dataset", e_opts['name'].tolist())
        active_behavior_table   = b_opts[b_opts['name']==sel_b]['table_name'].iloc[0]
        active_engagement_table = e_opts[e_opts['name']==sel_e]['table_name'].iloc[0]
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Global Filters")
        df_b = analytics.get_behavior_data(active_behavior_table)
        df_e = analytics.get_engagement_data(active_engagement_table)
        bc = set(df_b['Country'].unique()) if 'Country' in df_b.columns else set()
        ec = set(df_e['country'].unique()) if 'country' in df_e.columns else set()
        all_c = sorted(list(bc | ec))
        selected_countries = st.sidebar.multiselect("Countries", all_c, default=all_c)
        
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    # ═══════════════════════════════════════════════════════════════════════════
    # DASHBOARD (Institutional Overview)
    # ══════════════════════════════════════════════════════════════════════════
    if selection == "Dashboard":
        st.title("🏛️ Institutional Overview")
        df_b = analytics.get_behavior_data(active_behavior_table)
        df_e = analytics.get_engagement_data(active_engagement_table)
        if selected_countries:
            df_b = df_b[df_b['Country'].isin(selected_countries)] if 'Country' in df_b.columns else df_b
            df_e = df_e[df_e['country'].isin(selected_countries)] if 'country' in df_e.columns else df_e
            
        # Bento Grid Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Students (Behavior)",  f"{len(df_b):,}")
        m2.metric("Total Students (Engagement)", f"{len(df_e):,}")
        m3.metric("Avg Completion Rate", f"{df_b['Course_Completion_Rate(%)'].mean():.1f}%")
        m4.metric("Avg Final Grade", f"{df_e['final_grade'].mean():.1f}")
        
        st.markdown("---")
        
        # Charts in Cards
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.subheader("Platform Satisfaction")
                fig, ax = plt.subplots()
                sns.barplot(x='Platform_Used', y='Satisfaction_Score(1-5)', data=df_b, ax=ax, palette="mako")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
                top = df_b.groupby('Platform_Used')['Satisfaction_Score(1-5)'].mean().idxmax()
                st.markdown(f'<div class="custom-info">💡 Students are most satisfied on <b>{top}</b>.</div>', unsafe_allow_html=True)
            
        with c2:
            with st.container(border=True):
                st.subheader("Completion Rate by Education Level")
                fig, ax = plt.subplots()
                sns.boxplot(x='Education_Level', y='Course_Completion_Rate(%)', data=df_b, ax=ax, palette="rocket")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
                avg = df_b['Course_Completion_Rate(%)'].mean()
                st.markdown(f'<div class="custom-info">💡 Overall average completion: <b>{avg:.1f}%</b>.</div>', unsafe_allow_html=True)
            
        c3, c4 = st.columns(2)
        with c3:
            with st.container(border=True):
                st.subheader("Video Watch Time by Age Group")
                if 'age' in df_e.columns:
                    df_e['Age_Group'] = pd.cut(df_e['age'], bins=[10,20,30,40,50,60,100], labels=['10-20','21-30','31-40','41-50','51-60','60+'])
                    grouped_video = df_e.groupby('Age_Group', observed=True)['video_watch_time_min'].mean().reset_index()
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.plot(range(len(grouped_video)), grouped_video['video_watch_time_min'], marker='o', color='#fbbf24', linewidth=2.5, markersize=7, markerfacecolor='#09090b', markeredgewidth=2)
                    ax.fill_between(range(len(grouped_video)), grouped_video['video_watch_time_min'], alpha=0.15, color='#fbbf24')
                    for i, row in grouped_video.iterrows():
                        ax.annotate(f"{row['video_watch_time_min']:.0f}", xy=(i, row['video_watch_time_min']), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=8, color='#f4f4f5')
                    ax.set_xticks(range(len(grouped_video)))
                    ax.set_xticklabels(grouped_video['Age_Group'], fontsize=9)
                    ax.set_xlabel("Age Group"); ax.set_ylabel("Avg Watch Time (min)")
                    ax.grid(axis='y', alpha=0.2)
                    # y-axis was defaulting to start at 0, so the fill_between (which
                    # shades everything under the line) turned into one solid muddy
                    # block since all values sit tightly around ~300. Starting the
                    # axis near the data's own range keeps the fill as a thin, tight
                    # band under the line instead.
                    y_min, y_max = grouped_video['video_watch_time_min'].min(), grouped_video['video_watch_time_min'].max()
                    pad = max((y_max - y_min) * 0.6, 5)
                    ax.set_ylim(max(0, y_min - pad), y_max + pad)
                    plt.tight_layout()
                    st.pyplot(fig)
                    peak_age = grouped_video.loc[grouped_video['video_watch_time_min'].idxmax(), 'Age_Group']
                    peak_val = grouped_video['video_watch_time_min'].max()
                    low_age  = grouped_video.loc[grouped_video['video_watch_time_min'].idxmin(), 'Age_Group']
                    low_val  = grouped_video['video_watch_time_min'].min()
                    st.markdown(f'''<div class="custom-info">💡 <b>{peak_age}</b> age group watches the most — avg <b>{peak_val:.0f} min</b>. <b>{low_age}</b> group watches least at <b>{low_val:.0f} min</b>.</div>''', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="custom-warn">⚠️ Age column not found.</div>', unsafe_allow_html=True)
            
        with c4:
            with st.container(border=True):
                st.subheader("Learning Mode Distribution")
                if 'Learning_Mode' in df_b.columns:
                    counts = df_b['Learning_Mode'].value_counts()
                    fig, ax = plt.subplots(figsize=(6, 4))
                    colors = ['#fbbf24','#f59e0b','#d97706','#b45309','#92400e']
                    wedges, texts, autotexts = ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors[:len(counts)], startangle=140, pctdistance=0.75, radius=0.85, wedgeprops=dict(edgecolor='#09090b', linewidth=2.5, width=0.65))
                    for t in texts: t.set_color('#f4f4f5'); t.set_fontsize(10); t.set_fontweight('bold')
                    for at in autotexts: at.set_color('#09090b'); at.set_fontsize(9); at.set_fontweight('600')
                    ax.set_facecolor('#18181b'); fig.patch.set_facecolor('#18181b')
                    plt.tight_layout()
                    st.pyplot(fig)
                    dominant = counts.index[0]
                    dominant_pct = counts.iloc[0] / counts.sum() * 100
                    st.markdown(f'''<div class="custom-info">💡 <b>{dominant}</b> is the most popular learning mode at <b>{dominant_pct:.1f}%</b>.</div>''', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="custom-warn">⚠️ Learning_Mode column not found.</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # ACADEMIC EXCELLENCE
    # ═══════════════════════════════════════════════════════════════════════════
    elif selection == "Academic Excellence":
        st.title("🏆 Academic Excellence")
        df_e = analytics.get_engagement_data(active_engagement_table)
        if selected_countries:
            df_e = df_e[df_e['country'].isin(selected_countries)] if 'country' in df_e.columns else df_e
            
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.subheader("Correlation Matrix")
                corr_cols = [c for c in ['study_hours_weekly','login_frequency_weekly','avg_quiz_score','attendance_rate','engagement_score','final_grade'] if c in df_e.columns]
                fig, ax = plt.subplots(figsize=(6,5))
                sns.heatmap(df_e[corr_cols].corr(), annot=True, fmt=".2f", cmap="magma", ax=ax, linewidths=0.5)
                plt.tight_layout()
                st.pyplot(fig)
                top_f = df_e[corr_cols].corr()['final_grade'].drop('final_grade').idxmax()
                st.markdown(f'<div class="custom-info">💡 <b>{top_f}</b> has the strongest correlation with final grades.</div>', unsafe_allow_html=True)
        with c2:
            with st.container(border=True):
                st.subheader("Grades by Device Type")
                fig, ax = plt.subplots()
                order = df_e.groupby('device_type')['final_grade'].mean().sort_values(ascending=False).index
                sns.barplot(x='device_type', y='final_grade', data=df_e, ax=ax, order=order, palette="plasma")
                ax.set_xlabel("Device"); ax.set_ylabel("Avg Grade")
                plt.tight_layout()
                st.pyplot(fig)
                top_d = df_e.groupby('device_type')['final_grade'].mean().idxmax()
                st.markdown(f'<div class="custom-info">💡 <b>{top_d}</b> users tend to achieve the best grades.</div>', unsafe_allow_html=True)
            
        c3, c4 = st.columns(2)
        with c3:
            with st.container(border=True):
                st.subheader("Quiz Score vs Final Grade")
                fig, ax = plt.subplots(figsize=(6,4))
                ax.scatter(df_e['avg_quiz_score'], df_e['final_grade'], alpha=0.25, s=8, color='#fbbf24', label='Students')
                m, b_ = np.polyfit(df_e['avg_quiz_score'].fillna(0), df_e['final_grade'].fillna(0), 1)
                x_ = np.linspace(df_e['avg_quiz_score'].min(), df_e['avg_quiz_score'].max(), 100)
                ax.plot(x_, m*x_+b_, color='#34d399', linewidth=2.5, label=f'Trend (slope={m:.2f})')
                ax.set_xlabel("Avg Quiz Score"); ax.set_ylabel("Final Grade")
                ax.legend(facecolor='#18181b', edgecolor='#27272a', labelcolor='#f4f4f5', fontsize=8)
                ax.grid(alpha=0.2)
                plt.tight_layout()
                st.pyplot(fig)
                corr_q = df_e['avg_quiz_score'].corr(df_e['final_grade'])
                high_q = df_e[df_e['avg_quiz_score'] > df_e['avg_quiz_score'].quantile(0.75)]['final_grade'].mean()
                low_q  = df_e[df_e['avg_quiz_score'] < df_e['avg_quiz_score'].quantile(0.25)]['final_grade'].mean()
                st.markdown(f'''<div class="custom-info">💡 <b>Correlation: {corr_q:.2f}</b> — Top 25% quiz scorers average <b>{high_q:.1f}</b> vs bottom 25% at <b>{low_q:.1f}</b>.</div>''', unsafe_allow_html=True)
        with c4:
            with st.container(border=True):
                st.subheader("Attendance vs Final Grade")
                fig, ax = plt.subplots(figsize=(6,4))
                scatter = ax.scatter(df_e['attendance_rate']*100, df_e['final_grade'], alpha=0.25, s=8, c=df_e['final_grade'], cmap='viridis')
                plt.colorbar(scatter, ax=ax, label='Grade')
                m2, b2 = np.polyfit(df_e['attendance_rate'].fillna(0)*100, df_e['final_grade'].fillna(0), 1)
                x2 = np.linspace(0, 100, 100)
                ax.plot(x2, m2*x2+b2, color='#f43f5e', linewidth=2.5, label='Trend')
                ax.axvline(80, color='#fbbf24', linestyle='--', linewidth=1.5, alpha=0.7, label='80% threshold')
                ax.set_xlabel("Attendance Rate (%)"); ax.set_ylabel("Final Grade")
                ax.legend(facecolor='#18181b', edgecolor='#27272a', labelcolor='#f4f4f5', fontsize=8)
                ax.grid(alpha=0.2)
                plt.tight_layout()
                st.pyplot(fig)
                corr_a = df_e['attendance_rate'].corr(df_e['final_grade'])
                above80 = df_e[df_e['attendance_rate'] >= 0.8]['final_grade'].mean()
                below80 = df_e[df_e['attendance_rate'] < 0.8]['final_grade'].mean()
                st.markdown(f'''<div class="custom-info">💡 <b>Correlation: {corr_a:.2f}</b> — Students with ≥80% attendance score <b>{above80:.1f}</b> avg vs <b>{below80:.1f}</b>.</div>''', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # RISK & ENGAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    elif selection == "Risk & Engagement":
        st.title("🚩 Student Engagement & Risk")
        df_e = analytics.get_engagement_data(active_engagement_table)
        if selected_countries:
            df_e = df_e[df_e['country'].isin(selected_countries)] if 'country' in df_e.columns else df_e

        tab_overview, tab_risklist, tab_predict = st.tabs(["📊 Overview", "📋 Risk List", "🤖 AI Risk Predictor"])

        with tab_overview:
            dropout_rate = df_e['dropout'].mean() * 100
            high_risk = df_e[df_e['engagement_score'] < df_e['engagement_score'].quantile(0.25)]
            r1, r2, r3 = st.columns(3)
            r1.metric("Overall Dropout Rate", f"{dropout_rate:.1f}%", delta_color="inverse")
            r2.metric("Avg Engagement Score", f"{df_e['engagement_score'].mean():.2f}")
            r3.metric("At-Risk Students", f"{len(high_risk):,}")

            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.subheader("Study Hours vs Final Grade")
                    fig, ax = plt.subplots(figsize=(6,4))
                    sc = ax.scatter(df_e['study_hours_weekly'], df_e['final_grade'], c=df_e['dropout'], cmap='RdYlGn_r', alpha=0.35, s=8)
                    cbar = plt.colorbar(sc, ax=ax); cbar.set_label('Dropout (1=Yes)', color='#a1a1aa'); plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#a1a1aa')
                    ax.set_xlabel("Study Hours/Week"); ax.set_ylabel("Final Grade"); ax.grid(alpha=0.2)
                    plt.tight_layout()
                    st.pyplot(fig)
                    avg_g = df_e[df_e['study_hours_weekly'] > df_e['study_hours_weekly'].mean()]['final_grade'].mean()
                    low_g = df_e[df_e['study_hours_weekly'] <= df_e['study_hours_weekly'].mean()]['final_grade'].mean()
                    st.markdown(f'<div class="custom-info"> Above-average studiers score <b>{avg_g:.1f}</b> vs <b>{low_g:.1f}</b> for below-average.</div>', unsafe_allow_html=True)
            with c2:
                with st.container(border=True):
                    st.subheader("Dropout Risk by Internet Speed")
                    bins, labels_ = [0,30,100,1000], ['Slow','Medium','Fast']
                    df_e['Speed_Cat'] = pd.cut(df_e['internet_speed_mbps'], bins=bins, labels=labels_)
                    dp = df_e.groupby('Speed_Cat', observed=True)['dropout'].mean().reset_index()
                    fig, ax = plt.subplots(figsize=(6,4))
                    bar_colors = ['#f43f5e','#fbbf24','#38bdf8']
                    bars = ax.bar(dp['Speed_Cat'], dp['dropout']*100, color=bar_colors[:len(dp)], edgecolor='#09090b', linewidth=1.5, width=0.5)
                    for bar_ in bars: ax.text(bar_.get_x() + bar_.get_width()/2, bar_.get_height()+0.3, f"{bar_.get_height():.1f}%", ha='center', va='bottom', color='#f4f4f5', fontsize=10, fontweight='bold')
                    ax.set_ylabel("Dropout Probability (%)"); ax.set_xlabel("Internet Speed"); ax.grid(axis='y', alpha=0.2)
                    plt.tight_layout()
                    st.pyplot(fig)
                    slow_d = dp[dp['Speed_Cat']=='Slow']['dropout'].values
                    fast_d = dp[dp['Speed_Cat']=='Fast']['dropout'].values
                    if len(slow_d) and len(fast_d):
                        diff = (slow_d[0] - fast_d[0]) * 100
                        st.markdown(f'<div class="custom-danger">⚠️ Slow internet students have <b>{diff:.1f}%</b> higher dropout rate than fast users.</div>', unsafe_allow_html=True)

        with tab_risklist:
            with st.container(border=True):
                st.subheader("📋 Class Risk List")
                st.caption("Runs the trained model across every student in the active engagement dataset at once, so you can filter and export by risk level instead of checking one ID at a time.")

                id_col = 'student_id' if 'student_id' in df_e.columns else ('Student_ID' if 'Student_ID' in df_e.columns else None)
                scored = analytics.predict_dropout_risk_batch(df_e) if id_col else None

                if scored is None:
                    st.markdown('<div class="custom-warn">⚠️ Can\'t score this dataset — either the model isn\'t trained yet (<code>python train_dropout_model.py</code>) or the active engagement dataset is missing columns the model needs (age, gender, avg_session_duration_min, forum_posts, quiz_attempts, avg_quiz_score, attendance_rate, device_type — a custom upload may not include all of these).</div>', unsafe_allow_html=True)
                else:
                    risk_choice = st.radio("Filter by Risk Level", ["All", "Low Risk", "Medium Risk", "High Risk"], horizontal=True)
                    view = scored if risk_choice == "All" else scored[scored['risk_label'] == risk_choice]

                    rc1, rc2, rc3 = st.columns(3)
                    rc1.metric("Students Shown", f"{len(view):,}")
                    rc2.metric("High Risk (class-wide)", f"{(scored['risk_label']=='High Risk').sum():,}")
                    rc3.metric("Avg Risk Probability", f"{view['risk_probability'].mean()*100:.1f}%" if len(view) else "—")

                    display_cols = [c for c in [id_col, 'country', 'engagement_score', 'attendance_rate', 'final_grade', 'risk_probability', 'risk_label'] if c in view.columns]
                    st.dataframe(
                        view[display_cols].sort_values('risk_probability', ascending=False).reset_index(drop=True),
                        use_container_width=True, height=380
                    )
                    csv_download_button(view[display_cols], "⬇️ Export Risk List CSV", f"risk_list_{risk_choice.replace(' ','_').lower()}.csv", key="export_risklist")

                    st.markdown('<div class="section-header">Quick Flag from This List</div>', unsafe_allow_html=True)
                    with st.form(key="quick_flag_form"):
                        qc1, qc2 = st.columns([1, 1])
                        with qc1:
                            q_sid = st.text_input("Student ID to flag", placeholder="e.g. 42")
                        with qc2:
                            q_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=2)
                        q_note = st.text_input("Note (optional)")
                        q_submit = st.form_submit_button("🚩 Log Outreach Flag", use_container_width=True)
                        if q_submit:
                            if not q_sid:
                                st.error("Student ID is required.")
                            else:
                                analytics.create_intervention(q_sid, st.session_state.username, q_note, q_priority)
                                st.success(f"✅ Flagged Student {q_sid} for outreach.")

        with tab_predict:
            with st.container(border=True):
                st.subheader("🔮 AI Risk Predictor")
                st.caption("Adjust the sliders below to simulate any student profile and get a real-time dropout risk prediction.")

                metrics = analytics.get_dropout_model_metrics()
                if metrics is None:
                    st.markdown('<div class="custom-warn">⚠️ Model not trained yet. Run <code>python train_dropout_model.py</code> once from the project folder, then reload this page.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="custom-info">🤖 Model validated at <b>{metrics["roc_auc"]*100:.1f}%</b> ROC-AUC on held-out students (5-fold CV: {metrics["cv_roc_auc_mean"]*100:.1f}%).</div>', unsafe_allow_html=True)

                    # ── Student Profile Sliders ──
                    st.markdown('<div class="section-header">Student Profile</div>', unsafe_allow_html=True)

                    country_opts = sorted(df_e['country'].unique().tolist()) if 'country' in df_e.columns and len(df_e) else ["USA"]

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        age = st.number_input("Age", 15, 60, 22, key="pred_age")
                        gender = st.selectbox("Gender", ["Male", "Female"], key="pred_gender")
                        device_type = st.selectbox("Device Type", ["Laptop", "Tablet", "Mobile"], key="pred_device")
                        country = st.selectbox("Country", country_opts, key="pred_country")
                    with col2:
                        internet_speed_mbps = st.slider("Internet Speed (Mbps)", 1.0, 200.0, 50.0, key="pred_internet")
                        study_hours_weekly = st.slider("Study Hours / Week", 0.0, 40.0, 10.0, key="pred_study")
                        login_frequency_weekly = st.slider("Logins / Week", 0, 30, 7, key="pred_logins")
                        avg_session_duration_min = st.slider("Avg Session Duration (min)", 0.0, 120.0, 35.0, key="pred_session")
                    with col3:
                        attendance_rate = st.slider("Attendance Rate", 0.0, 1.0, 0.75, key="pred_attendance")
                        avg_quiz_score = st.slider("Avg Quiz Score", 0.0, 100.0, 60.0, key="pred_quiz")
                        final_grade = st.slider("Final Grade (so far)", 0.0, 100.0, 60.0, key="pred_grade")
                        engagement_score = st.slider("Engagement Score", 0.0, 15.0, 6.0, key="pred_engagement")

                    c4, c5, c6 = st.columns(3)
                    with c4:
                        video_watch_time_min = st.slider("Video Watch Time (min)", 0.0, 600.0, 250.0, key="pred_video")
                    with c5:
                        assignments_submitted = st.slider("Assignments Submitted", 0, 20, 5, key="pred_assign")
                        forum_posts = st.slider("Forum Posts", 0, 30, 8, key="pred_forum")
                    with c6:
                        quiz_attempts = st.slider("Quiz Attempts", 0, 15, 5, key="pred_qattempts")

                    # ── Predict Button ──
                    if st.button("🔮 Predict Risk", use_container_width=True, key="predict_btn"):
                        student_input = dict(
                            age=age, internet_speed_mbps=internet_speed_mbps, study_hours_weekly=study_hours_weekly,
                            login_frequency_weekly=login_frequency_weekly, avg_session_duration_min=avg_session_duration_min,
                            video_watch_time_min=video_watch_time_min, assignments_submitted=assignments_submitted,
                            forum_posts=forum_posts, quiz_attempts=quiz_attempts, avg_quiz_score=avg_quiz_score,
                            attendance_rate=attendance_rate, engagement_score=engagement_score, final_grade=final_grade,
                            gender=gender, device_type=device_type, country=country,
                        )
                        proba, label = analytics.predict_dropout_risk(student_input)
                        gauge_color = {"Low Risk": "#34d399", "Medium Risk": "#fbbf24", "High Risk": "#f43f5e"}

                        # ── GAUGE + FEATURE IMPORTANCE ──
                        rc1, rc2 = st.columns([1, 1.4])
                        with rc1:
                            pct = proba * 100
                            color = gauge_color[label]
                            st.markdown(f"""
                            <div style="text-align:center; padding:20px; background:#18181b; border:1px solid #27272a; border-radius:12px; margin-bottom:16px">
                                <div style="font-size:12px; color:#a1a1aa; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px">Predicted Dropout Probability</div>
                                <div style="font-size:48px; font-weight:800; color:{color}; line-height:1">{pct:.1f}%</div>
                                <div style="margin-top:12px; background:#09090b; border-radius:8px; height:16px; border:1px solid #27272a; overflow:hidden">
                                    <div style="width:{pct:.1f}%; background:{color}; height:16px; border-radius:8px; box-shadow:0 0 20px {color}44; transition:width 0.6s ease"></div>
                                </div>
                                <div style="margin-top:8px; font-size:13px; color:{color}; font-weight:700">{label}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            if label == "High Risk":
                                st.markdown('<div class="custom-danger">⚠️ <b>Immediate attention required.</b> This student profile shows strong dropout signals.</div>', unsafe_allow_html=True)
                            elif label == "Medium Risk":
                                st.markdown('<div class="custom-warn">⚡ <b>Monitor closely.</b> Some risk factors are present — early intervention recommended.</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="custom-success">✅ <b>Low risk.</b> This profile aligns with students who typically stay enrolled.</div>', unsafe_allow_html=True)

                        with rc2:
                            imp = analytics.get_dropout_feature_importance(8)
                            fig, ax = plt.subplots(figsize=(6,4))
                            ax.barh(imp.index[::-1], imp.values[::-1], color=CHART_PALETTE["primary"], edgecolor='#09090b')
                            ax.set_xlabel("Model Feature Importance")
                            ax.grid(axis='x', alpha=0.2)
                            plt.tight_layout()
                            st.pyplot(fig)
                            st.caption("Global feature importance — attendance_rate dominates in this dataset (≈80%).")

                        # ── YOU VS CLASS AVERAGE (DYNAMIC TABLE) ──
                        st.markdown('<div class="section-header">Profile vs Class Average</div>', unsafe_allow_html=True)
                        try:
                            compare_cols = ['study_hours_weekly','login_frequency_weekly','avg_session_duration_min',
                                            'attendance_rate','avg_quiz_score','engagement_score','final_grade']
                            cl_stats = analytics.get_class_stats(active_engagement_table, compare_cols)

                            comp_data = []
                            for col in compare_cols:
                                you_val = float(student_input[col])
                                avg_val = float(cl_stats.get(f'avg_{col}', 0))
                                comp_data.append({
                                    'Metric': col.replace('_', ' ').title(),
                                    'Your Profile': round(you_val, 2),
                                    'Class Avg': round(avg_val, 2),
                                    'Status': 'Above Avg' if you_val >= avg_val else 'Below Avg',
                                })

                            comp_df = pd.DataFrame(comp_data)
                            st.dataframe(
                                comp_df.style.map(lambda x: 'color: #34d399' if x == 'Above Avg' else 'color: #f43f5e', subset=['Status']),
                                use_container_width=True, hide_index=True, height=320
                            )
                        except Exception as e:
                            st.caption(f"Could not load class averages: {e}")

                        # ── AI RECOMMENDATIONS (DYNAMIC) ──
                        st.markdown('<div class="section-header">Personalised Recommendations</div>', unsafe_allow_html=True)
                        recs = []
                        try:
                            if attendance_rate < 0.8:
                                recs.append(("📅 Boost Attendance", f"Attendance is {attendance_rate*100:.0f}%. Raising above 80% is the single biggest lever to reduce dropout risk.", "danger"))
                            if study_hours_weekly < cl_stats.get('avg_study_hours_weekly', 0):
                                recs.append(("📖 Increase Study Hours", f"{study_hours_weekly:.1f} hrs/week vs class avg {cl_stats['avg_study_hours_weekly']:.1f}. Try adding 2–3 focused sessions.", "warn"))
                            if avg_quiz_score < cl_stats.get('avg_avg_quiz_score', 0):
                                recs.append(("🎯 Improve Quiz Performance", f"Avg quiz score {avg_quiz_score:.1f} vs class avg {cl_stats['avg_avg_quiz_score']:.1f}. Review past quizzes before new ones.", "warn"))
                            if forum_posts < 5:
                                recs.append(("💬 Join Discussions", f"{forum_posts} forum posts. Active participation improves retention by 15–20%.", "info"))
                            if engagement_score < cl_stats.get('avg_engagement_score', 0):
                                recs.append(("⚡ Raise Engagement", f"Score {engagement_score:.2f} vs class avg {cl_stats['avg_engagement_score']:.2f}. More logins & video time help.", "warn"))
                            if assignments_submitted < 10:
                                recs.append(("📋 Submit More Assignments", f"Only {assignments_submitted} submitted. Consistent submission is a strong retention signal.", "info"))
                        except Exception:
                            pass

                        if not recs:
                            st.markdown('<div class="custom-success">🌟 Excellent profile! Performing at or above class average on all key metrics.</div>', unsafe_allow_html=True)
                        else:
                            css_map = {"warn":"custom-warn","info":"custom-info","danger":"custom-danger"}
                            for title_, msg_, typ_ in recs:
                                st.markdown(f'<div class="{css_map[typ_]}"><b>{title_}</b><br>{msg_}</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # DATASETS
    # ═══════════════════════════════════════════════════════════════════════════
    elif selection == "Datasets":
        st.title("📂 Dataset Management")
        tab1, tab2 = st.tabs(["⬆️ Upload New Dataset", "📋 Existing Datasets"])
        with tab1:
            c_left, c_right = st.columns([1.1, 1], gap="large")
            with c_left:
                with st.container(border=True):
                    st.subheader("Dataset Configuration")
                    ds_type = st.radio("Select Dataset Type", ["Behavior", "Engagement"], horizontal=True)
                    ds_name = st.text_input("Dataset Name", placeholder="e.g. Semester 1 Batch 2025")
                    f_up = st.file_uploader("Upload CSV File", type="csv")
                    req_b = ['Student_ID','Platform_Used','Satisfaction_Score(1-5)','Education_Level','Course_Completion_Rate(%)','Daily_Learning_Hours','Country']
                    req_e = ['student_id','country','study_hours_weekly','login_frequency_weekly','video_watch_time_min','assignments_submitted','final_grade','engagement_score','internet_speed_mbps','dropout','device_type']
                    req = req_b if ds_type == "Behavior" else req_e
                
                    if f_up and ds_name:
                        if st.button("⬆️ Process & Upload Dataset", use_container_width=True):
                            df_ = pd.read_csv(f_up)
                            miss = [c for c in req if c not in df_.columns]
                            if miss:
                                st.markdown(f'<div class="custom-danger">❌ <b>Missing Columns:</b> {", ".join(miss)}</div>', unsafe_allow_html=True)
                            else:
                                with st.spinner("Validating and processing dataset…"):
                                    ok, msg = analytics.save_new_dataset(df_, ds_name, ds_type.lower())
                                if ok:
                                    st.markdown(f'<div class="custom-success">✅ <b>"{ds_name}"</b> uploaded successfully! {len(df_):,} rows processed.</div>', unsafe_allow_html=True)
                                    st.rerun()
                                else:
                                    st.markdown(f'<div class="custom-danger">❌ Error: {msg}</div>', unsafe_allow_html=True)
                    elif not ds_name and f_up:
                        st.markdown('<div class="custom-warn">⚠️ Please enter a dataset name before uploading.</div>', unsafe_allow_html=True)
                
            with c_right:
                with st.container(border=True):
                    st.subheader("Required Columns")
                    tags_html = " ".join([f'<span class="badge badge-amber">{c}</span>' for c in req])
                    st.markdown(tags_html, unsafe_allow_html=True)
                
        with tab2:
            existing = analytics.get_available_datasets()
            if existing.empty:
                st.markdown('<div class="empty-state"><span class="empty-icon">📭</span><span class="empty-text">No datasets uploaded yet — use the form above to add one.</span></div>', unsafe_allow_html=True)
            else:
                b_df = existing[existing["type"]=="behavior"]
                e_df = existing[existing["type"]=="engagement"]
                s1, s2, s3 = st.columns(3)
                s1.metric("Total Datasets", f"{len(existing)}")
                s2.metric("Behavior", f"{len(b_df)}")
                s3.metric("Engagement", f"{len(e_df)}")
                
                if not b_df.empty:
                    st.markdown('<div class="section-header">📘 Behavior Datasets</div>', unsafe_allow_html=True)
                    for _, row in b_df.iterrows():
                        st.markdown(f'''<div class="dashboard-card" style="padding:16px 20px; display:flex; justify-content:space-between; align-items:center">
                            <div><b style="color:#f4f4f5">📘 {row["name"]}</b><br><small style="color:#a1a1aa">Table: {row.get("table_name","—")} · Added: {row.get("upload_date","—")}</small></div>
                            <span class="badge badge-amber">BEHAVIOR</span>
                        </div>''', unsafe_allow_html=True)
                if not e_df.empty:
                    st.markdown('<div class="section-header">📗 Engagement Datasets</div>', unsafe_allow_html=True)
                    for _, row in e_df.iterrows():
                        st.markdown(f'''<div class="dashboard-card" style="padding:16px 20px; display:flex; justify-content:space-between; align-items:center">
                            <div><b style="color:#f4f4f5">📗 {row["name"]}</b><br><small style="color:#a1a1aa">Table: {row.get("table_name","—")} · Added: {row.get("upload_date","—")}</small></div>
                            <span class="badge badge-emerald">ENGAGEMENT</span>
                        </div>''', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # MY PROGRESS
    # ═══════════════════════════════════════════════════════════════════════════
    elif selection == "My Progress":
        st.title("👤 My Progress Dashboard")
        st.markdown("Enter your Student ID to get your complete, personalised analytics.")
        sid = st.text_input("🔍 Student ID", placeholder="e.g. 42")
        if sid:
            render_student_profile(sid, active_behavior_table, active_engagement_table, admin_view=False)
        else:
            st.markdown('<div class="custom-info">👆 Enter your Student ID above to load your full dashboard.</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # STUDENT LOOKUP (Admin — same dashboard as My Progress, for any student ID)
    # ═══════════════════════════════════════════════════════════════════════════
    elif selection == "Student Lookup":
        st.title("🔍 Student Lookup")
        st.markdown("Look up any student by ID to view their full analytics, export a report, or flag them for outreach.")
        sid = st.text_input("🔍 Student ID", placeholder="e.g. 42", key="lookup_sid")
        if sid:
            render_student_profile(sid, active_behavior_table, active_engagement_table, admin_view=True)
        else:
            st.markdown('<div class="custom-info">👆 Enter a Student ID above to load their dashboard.</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # INTERVENTIONS (Admin — outreach flag log)
    # ═══════════════════════════════════════════════════════════════════════════
    elif selection == "Interventions":
        st.title("🚩 Interventions & Outreach Log")
        st.markdown("Track students flagged for outreach — from Risk List, Student Lookup, or logged directly here.")

        with st.expander("➕ Log a New Flag"):
            with st.form(key="new_intervention_form"):
                ic1, ic2 = st.columns([1, 1])
                with ic1:
                    i_sid = st.text_input("Student ID")
                with ic2:
                    i_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
                i_note = st.text_area("Note", placeholder="Reason for flagging / suggested action…")
                i_submit = st.form_submit_button("🚩 Log Flag", use_container_width=True)
                if i_submit:
                    if not i_sid:
                        st.error("Student ID is required.")
                    else:
                        analytics.create_intervention(i_sid, st.session_state.username, i_note, i_priority)
                        st.success(f"✅ Logged outreach flag for Student {i_sid}.")
                        st.rerun()

        st.markdown('<div class="section-header">Outreach Log</div>', unsafe_allow_html=True)
        status_filter = st.radio("Status", ["Open", "Resolved", "All"], horizontal=True)
        log_df = analytics.get_interventions(status_filter)

        if log_df.empty:
            st.markdown('<div class="empty-state"><span class="empty-icon">📭</span><span class="empty-text">No interventions logged yet.</span></div>', unsafe_allow_html=True)
        else:
            csv_download_button(log_df, "⬇️ Export Log CSV", "interventions_log.csv", key="export_interventions")
            priority_cls = {"High": "badge-rose", "Medium": "badge-amber", "Low": "badge-sky"}
            status_cls = {"Open": "badge-amber", "Resolved": "badge-emerald"}
            for _, row in log_df.iterrows():
                c_info, c_action = st.columns([5, 1])
                with c_info:
                    st.markdown(f'''<div class="dashboard-card" style="padding:16px 20px">
                        <div><b style="color:#f4f4f5">Student #{row["student_id"]}</b>
                        <span class="badge {priority_cls.get(row["priority"],"badge-sky")}">{row["priority"]}</span>
                        <span class="badge {status_cls.get(row["status"],"badge-sky")}">{row["status"]}</span></div>
                        <small style="color:#a1a1aa">Flagged by {row["flagged_by"]} on {row["created_at"]}</small>
                        <p style="margin-top:8px">{row["note"] or "<i>No note added.</i>"}</p>
                    </div>''', unsafe_allow_html=True)
                with c_action:
                    if row["status"] == "Open":
                        if st.button("✅ Resolve", key=f"resolve_{row['id']}", use_container_width=True):
                            analytics.update_intervention_status(row["id"], "Resolved")
                            st.rerun()
                    else:
                        if st.button("↩️ Reopen", key=f"reopen_{row['id']}", use_container_width=True):
                            analytics.update_intervention_status(row["id"], "Open")
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
🎓 EduTrak 2026 &nbsp;·&nbsp; Made by Atharv &nbsp;·&nbsp; BBDU
</div>
""", unsafe_allow_html=True)