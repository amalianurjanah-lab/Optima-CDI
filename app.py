import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import base64, os, warnings
warnings.filterwarnings('ignore')

# ─── LOGO ───────────────────────────────────────────────────────────────────
def get_logo_b64():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_OPTIMA.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64  = get_logo_b64()
LOGO_HTML = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:56px;object-fit:contain;" />' if LOGO_B64 else "🏥"

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OPTIMA-CDI | Audit Klaim RS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS — LIGHT + STEEL BLUE PALETTE ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Background: putih bersih dengan nuansa steel-blue muda ── */
.main { background: #eef3f8; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(150deg, #f0f5fb 0%, #e8f0f9 40%, #dde8f4 100%);
}
[data-testid="stHeader"] { background: transparent; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #75909C;
    border-right: 2px solid #5a7a87;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 { color: #a8c4d8 !important; }
[data-testid="stSidebar"] label { color: #c5d9e8 !important; font-weight: 500; }
[data-testid="stSidebar"] .stRadio label { color: #b8d0e2 !important; }
[data-testid="stSidebar"] hr { border-color: #2e4a6a; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.07);
    border: 2px dashed #4a7a9b;
    border-radius: 10px;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] { background: rgba(255,255,255,0.08); }
[data-testid="stSidebar"] button[data-baseweb="tab"] { color: #a8c4d8 !important; }
[data-testid="stSidebar"] button[data-baseweb="tab"][aria-selected="true"] { color: #5fb3e4 !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { color: #b8d0e2 !important; }

/* ── Metric cards ── */
.metric-card {
    background: #ffffff;
    border: 1.5px solid #c8dcea;
    border-radius: 16px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 18px rgba(44,82,120,0.09);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    border-radius: 16px 16px 0 0;
}
.metric-card.blue::before   { background: linear-gradient(90deg, #2e7bb5, #5fb3e4); }
.metric-card.red::before    { background: linear-gradient(90deg, #c0392b, #e74c3c); }
.metric-card.green::before  { background: linear-gradient(90deg, #1a7a4a, #27ae60); }
.metric-card.orange::before { background: linear-gradient(90deg, #c87722, #e8a030); }
.metric-card.purple::before { background: linear-gradient(90deg, #3d5a80, #6b8fb5); }
.metric-card.steel::before  { background: linear-gradient(90deg, #3a5f7f, #7a9ab5); }

.metric-label { font-size: 0.72rem; color: #5a7a95; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.metric-value { font-size: 1.7rem; font-weight: 800; color: #1c2e45; line-height: 1; }
.metric-sub   { font-size: 0.75rem; color: #7a9ab5; margin-top: 4px; }
.metric-delta { font-size: 0.78rem; font-weight: 600; margin-top: 6px; }
.delta-neg { color: #c0392b; }
.delta-pos { color: #1a7a4a; }

/* ── Section headers ── */
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin: 8px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid #c8dcea;
}
.section-header h2 { font-size: 1rem; font-weight: 700; color: #1c3a5a; margin: 0; }
.section-icon { font-size: 1.1rem; }

/* ── Narasi box ── */
.narasi-box {
    background: linear-gradient(135deg, #eaf3fb 0%, #deedf8 100%);
    border: 1.5px solid #a8c8de;
    border-left: 5px solid #2e7bb5;
    border-radius: 12px;
    padding: 16px 18px; margin: 6px 0;
}
.narasi-box p { color: #1c2e45; font-size: 0.86rem; line-height: 1.75; margin: 0; }
.narasi-box strong { color: #1e5f8a; }

/* ── Alert boxes ── */
.alert-warning {
    background: linear-gradient(135deg, #fffbea 0%, #fef4cc 100%);
    border: 1.5px solid #e0c050;
    border-left: 5px solid #c8960a;
    border-radius: 10px; padding: 14px 16px; margin: 6px 0;
}
.alert-danger {
    background: linear-gradient(135deg, #fdf0ee 0%, #fce0dc 100%);
    border: 1.5px solid #e0a8a0;
    border-left: 5px solid #c0392b;
    border-radius: 10px; padding: 14px 16px; margin: 6px 0;
}
.alert-success {
    background: linear-gradient(135deg, #eafaf3 0%, #d4f4e4 100%);
    border: 1.5px solid #7ec8a0;
    border-left: 5px solid #1a7a4a;
    border-radius: 10px; padding: 14px 16px; margin: 6px 0;
}
.alert-box-text { color: #1c2e45; font-size: 0.83rem; line-height: 1.65; margin: 0; }
.alert-title    { font-weight: 700; font-size: 0.9rem; margin-bottom: 5px; }

/* ── Brand bar ── */
.brand-bar {
    background: linear-gradient(90deg, #1c2e45 0%, #2a4060 60%, #1e3a58 100%);
    border-radius: 16px;
    padding: 16px 26px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px;
    box-shadow: 0 4px 24px rgba(28,46,69,0.18);
}
.brand-name { font-size: 1.5rem; font-weight: 800; color: #e8f2fa; letter-spacing: -0.02em; }
.brand-name span { color: #5fb3e4; }
.brand-sub { font-size: 0.78rem; color: #7aaac8; margin-top: 2px; }

/* ── Welcome screen ── */
.welcome-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 60px 20px 40px 20px; text-align: center;
}
.welcome-title {
    font-size: 1.55rem; font-weight: 800; color: #1c2e45;
    line-height: 1.35; margin: 24px 0 10px 0;
}
.welcome-title span { color: #1c2e45; }
.welcome-sub {
    font-size: 0.95rem; color: #5a7a95; margin-top: 8px;
    background: #eaf3fb; border: 1.5px solid #a8c8de;
    border-radius: 10px; padding: 12px 22px; display: inline-block;
}

/* ── Table ── */
[data-testid="stDataFrame"] {
    border-radius: 12px; border: 1.5px solid #c8dcea;
    box-shadow: 0 2px 12px rgba(44,82,120,0.07);
}

/* ── Buttons ── */
.stDownloadButton button {
    background: linear-gradient(90deg, #2e7bb5, #1c5a8a) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #dde8f4; }
::-webkit-scrollbar-thumb { background: #7aaac8; border-radius: 3px; }

/* ── Tab ── */
button[data-baseweb="tab"] { font-size: 0.85rem !important; font-weight: 600 !important; color: #5a7a95 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #2e7bb5 !important; }
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADER ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file):
    try:
        raw      = pd.read_excel(uploaded_file, header=0, nrows=1)
        info_row = str(raw.columns[0])
        df       = pd.read_excel(uploaded_file, header=2)
    except Exception as e:
        st.error(f"Gagal memuat file: {e}")
        return None, ""

    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['No.'])
    df = df[df['No.'].astype(str).str.strip().str.match(r'^\d+$')]

    for col in ['Total Tarif INA-CBGs','Tarif RS Diajukan','Selisih (Gap)','Gap %','LOS','Nilai Top-Up']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df['Tgl. Masuk']  = pd.to_datetime(df['Tgl. Masuk'],  errors='coerce')
    df['Tgl. Pulang'] = pd.to_datetime(df['Tgl. Pulang'], errors='coerce')

    df['Tipe Ketidaktepatan'] = df.apply(lambda r: (
        'Uppercoding' if (r.get('Gap %', 0) or 0) < 0 else
        'Undercoding' if (r.get('Gap %', 0) or 0) > 0 else 'Sesuai'
    ) if pd.notna(r.get('Gap %')) else 'Sesuai', axis=1)

    df['Ada Error'] = df['Status Klaim'] == 'Berpotensi Error'

    def mitigasi(row):
        err  = str(row.get('Indikasi Error Coding', ''))
        tipe = str(row.get('Tipe Ketidaktepatan', ''))
        if 'CC/MCC' in err or 'Komplikasi' in err: return 'Review & tambahkan kode CC/MCC dari rekam medis'
        elif 'PDx vs SDx' in err:                  return 'Tukar urutan PDx–SDx sesuai kondisi utama penerimaan'
        elif 'Top-up' in err:                       return 'Lengkapi formulir top-up & kode prosedur pendukung'
        elif 'prosedur' in err:                     return 'Verifikasi kode prosedur dengan panduan ICD-9-CM/INA-CBGs'
        elif 'Overcoding' in err or 'Uppercoding' in tipe: return 'Turunkan grup tarif: periksa severity level koding'
        elif 'Undercoding' in err or 'Undercoding' in tipe: return 'Naikkan grup tarif: tambahkan diagnosis penyerta relevan'
        else: return '—'

    df['Rekomendasi Mitigasi'] = df.apply(mitigasi, axis=1)

    gap_abs = df['Selisih (Gap)'].abs()
    df['Risiko Finansial'] = pd.cut(
        gap_abs, bins=[0,1_000_000,5_000_000,20_000_000,float('inf')],
        labels=['Rendah','Sedang','Tinggi','Kritis'], right=True
    ).astype(str)
    df.loc[df['Selisih (Gap)'].isna(), 'Risiko Finansial'] = 'N/A'

    info_row = info_row.replace(' DUMMY','').replace(' Dummy','').replace('DUMMY ','').replace('dummy','')
    return df, info_row


# ─── CHART THEME ─────────────────────────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor='rgba(255,255,255,0)',
    plot_bgcolor='rgba(255,255,255,0.75)',
    font=dict(family='Inter', color='#1c3a5a', size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    colorway=['#2e7bb5','#c0392b','#1a7a4a','#c87722','#3d5a80','#e8a030','#5fb3e4','#7ec8a0']
)
GRID = dict(gridcolor='#c8dcea', zerolinecolor='#c8dcea')

def fmt_rp(val):
    if pd.isna(val): return "—"
    if abs(val) >= 1_000_000_000: return f"Rp {val/1e9:.2f} M"
    if abs(val) >= 1_000_000:     return f"Rp {val/1e6:.1f} Jt"
    return f"Rp {val:,.0f}"


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(f'<div style="text-align:center;padding:14px 0 4px 0;">'
                    f'<img src="data:image/png;base64,{LOGO_B64}" style="height:72px;object-fit:contain;" />'
                    f'</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#5fb3e4;font-size:1.1rem;font-weight:800;margin:4px 0 2px 0;'>OPTIMA-CDI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#7aaac8;font-size:0.73rem;margin:0 0 10px 0;'>Audit Klaim Cerdas & Mitigasi Otomatis</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<p style='color:#a8c4d8;font-size:0.78rem;font-weight:600;margin-bottom:6px;'>📂 Upload File Rekap Klaim</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx"], label_visibility="collapsed",
                                     help="Upload file rekap klaim RS manapun — format INA-CBGs standar")

    # Hanya tampilkan filter & navigasi jika file sudah diupload
    if uploaded_file is not None:
        df_main, info_row = load_data(uploaded_file)
        if df_main is None:
            st.stop()

        st.divider()
        st.markdown("<p style='color:#a8c4d8;font-size:0.78rem;font-weight:600;'>⚙️ Filter Data</p>", unsafe_allow_html=True)
        status_filter  = st.multiselect("Status Klaim", options=df_main['Status Klaim'].dropna().unique().tolist(), default=df_main['Status Klaim'].dropna().unique().tolist())
        jenis_filter   = st.multiselect("Jenis (RI/RJ)",  options=df_main['Jenis'].dropna().unique().tolist(),        default=df_main['Jenis'].dropna().unique().tolist())
        koder_filter   = st.multiselect("Koder",           options=sorted(df_main['Koder'].dropna().unique().tolist()),default=sorted(df_main['Koder'].dropna().unique().tolist()))
        bangsal_filter = st.multiselect("Bangsal / Unit",  options=sorted(df_main['Bangsal'].dropna().unique().tolist()),default=sorted(df_main['Bangsal'].dropna().unique().tolist()))

        st.divider()
        st.markdown("<p style='color:#a8c4d8;font-size:0.78rem;font-weight:600;'>📑 Navigasi Halaman</p>", unsafe_allow_html=True)
        page = st.radio("", [
            "📊 Ringkasan Eksekutif",
            "🔍 Analisis Error Coding",
            "💰 Analisis Finansial",
            "📋 Log Transaksi Klaim",
            "🛡️ Mitigasi & Rekomendasi"
        ], label_visibility="collapsed")
    else:
        df_main    = None
        info_row   = ""
        page       = None

    st.divider()
    st.markdown("<p style='color:#4a6a85;font-size:0.7rem;text-align:center;'>OPTIMA-CDI v2.0 · 2026<br>Audit INA-CBGs Berbasis Data</p>", unsafe_allow_html=True)


# ─── WELCOME SCREEN (jika belum upload) ──────────────────────────────────────
if uploaded_file is None or df_main is None:
    st.markdown(f"""
    <div class="welcome-wrap" style="color: #002D62; font-weight: bold;">
        { '<img src="data:image/png;base64,' + LOGO_B64 + '" style="height:160px;object-fit:contain;" />' if LOGO_B64 else '🏥' }
        <div class="welcome-title" style="color: #002D62; font-weight: bold;">
            <strong>Dashboard Analitik</strong><br>
            <span>Dampak Ketidaktepatan terhadap Coding</span> <br>
            Efisiensi Biaya INA-CBGs
        </div>
        <div class="welcome-sub" style="color: #002D62; font-weight: bold;">
            💡 Silakan unggah file Excel rekap klaim melalui sidebar untuk melihat visualisasi.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── APPLY FILTERS ───────────────────────────────────────────────────────────
df = df_main.copy()
if status_filter:  df = df[df['Status Klaim'].isin(status_filter)]
if jenis_filter:   df = df[df['Jenis'].isin(jenis_filter)]
if koder_filter:   df = df[df['Koder'].isin(koder_filter)]
if bangsal_filter: df = df[df['Bangsal'].isin(bangsal_filter)]


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — RINGKASAN EKSEKUTIF
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Ringkasan Eksekutif":

    parts     = info_row.split('·') if '·' in info_row else [info_row]
    rs_name   = parts[0].strip() if len(parts) > 0 else "Rumah Sakit"
    rs_kode   = parts[1].strip() if len(parts) > 1 else ""
    rs_alamat = parts[2].strip() if len(parts) > 2 else ""
    rs_period = parts[3].strip() if len(parts) > 3 else ""

    logo_part = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:52px;object-fit:contain;" />' if LOGO_B64 else "🏥"
    st.markdown(f"""
    <div class="brand-bar">
        <div style="display:flex;align-items:center;gap:14px;">
            {logo_part}
            <div>
                <div class="brand-name"><span>OPTIMA</span>-CDI</div>
                <div class="brand-sub">{rs_name} &nbsp;|&nbsp; {rs_kode} &nbsp;|&nbsp; {rs_alamat}</div>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="color:#5fb3e4;font-size:0.82rem;font-weight:700;">Periode Audit</div>
            <div style="color:#a8c4d8;font-size:0.80rem;">{rs_period}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    total      = len(df)
    error_df   = df[df['Status Klaim'] == 'Berpotensi Error']
    n_error    = len(error_df)
    n_ok       = len(df[df['Status Klaim'] == 'Sesuai'])
    pct_error  = n_error / total * 100 if total else 0
    total_cbgs = df['Total Tarif INA-CBGs'].sum()
    total_rs   = df['Tarif RS Diajukan'].sum()
    total_gap  = df['Selisih (Gap)'].sum()
    pct_gap    = total_gap / total_cbgs * 100 if total_cbgs else 0
    n_upper    = len(error_df[error_df['Tipe Ketidaktepatan']=='Uppercoding'])
    n_under    = len(error_df[error_df['Tipe Ketidaktepatan']=='Undercoding'])

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,color,label,val,sub,delta in [
        (c1,"blue",  "📋 Total Berkas",      f"{total}",         f"{n_ok} sesuai · {n_error} error",   f"<span class='delta-neg'>⚠ {pct_error:.1f}% berpotensi error</span>"),
        (c2,"red",   "🚨 Berpotensi Error",   f"{n_error}",       "dari total klaim diaudit",            f"<span class='delta-neg'>↓ {n_upper} uppercoding · {n_under} undercoding</span>"),
        (c3,"steel", "🏦 Total INA-CBGs",     fmt_rp(total_cbgs), "standar tarif BPJS",                 ""),
        (c4,"orange","📤 Tarif RS Diajukan",  fmt_rp(total_rs),   "total klaim RS ke BPJS",             ""),
        (c5,"purple","💸 Total Gap",           fmt_rp(total_gap),  "selisih INA-CBGs vs RS",             f"<span class='delta-neg'>{pct_gap:.1f}% dari total tarif</span>"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card {color}"><div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-sub">{sub}</div><div class="metric-delta">{delta}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    top_error   = df['Indikasi Error Coding'].value_counts().idxmax() if df['Indikasi Error Coding'].notna().any() else "—"
    top_bangsal = error_df['Bangsal'].value_counts().idxmax() if not error_df.empty else "—"
    pct_upper   = n_upper/n_error*100 if n_error else 0

    st.markdown(f"""
    <div class="narasi-box">
    <p>📌 <strong>Ringkasan Temuan Audit:</strong> Dari <strong>{total} berkas klaim</strong> yang diaudit,
    sebanyak <strong>{n_error} berkas ({pct_error:.1f}%)</strong> teridentifikasi <em>berpotensi error coding</em>.
    Sebanyak <strong>{n_upper} kasus ({pct_upper:.0f}%)</strong> merupakan uppercoding — RS mengajukan tarif lebih rendah
    dari yang seharusnya. Indikasi error terbanyak: <strong>"{top_error}"</strong>,
    bangsal paling terdampak: <strong>{top_bangsal}</strong>.
    Total gap mencapai <strong>{fmt_rp(total_gap)}</strong> ({abs(pct_gap):.1f}% dari total tarif standar).</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header"><span class="section-icon">📊</span><h2>Distribusi Status Klaim</h2></div>', unsafe_allow_html=True)
        sc = df['Status Klaim'].value_counts().reset_index(); sc.columns=['Status','Jumlah']
        fig = px.pie(sc, names='Status', values='Jumlah', hole=0.55,
                     color='Status', color_discrete_map={'Sesuai':'#1a7a4a','Berpotensi Error':'#c0392b'})
        fig.update_traces(textposition='outside', textinfo='percent+label', textfont=dict(color='#1c3a5a',size=12))
        fig.update_layout(**CHART_THEME, height=280, showlegend=False,
                          annotations=[dict(text=f"<b>{total}</b><br>Berkas",x=0.5,y=0.5,font_size=14,font_color='#1c2e45',showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header"><span class="section-icon">🏥</span><h2>Error per Bangsal / Unit</h2></div>', unsafe_allow_html=True)
        be = error_df['Bangsal'].value_counts().reset_index(); be.columns=['Bangsal','Jumlah Error']
        fig2 = px.bar(be, x='Jumlah Error', y='Bangsal', orientation='h',
                      color='Jumlah Error', color_continuous_scale=['#7aaac8','#2e7bb5','#1c3a5a'])
        fig2.update_layout(**CHART_THEME, height=280,
                           yaxis=dict(title='',autorange='reversed',**GRID),
                           xaxis=dict(title='Jumlah Error',**GRID), coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown('<div class="section-header"><span class="section-icon">👤</span><h2>Error per Koder</h2></div>', unsafe_allow_html=True)
        kd = df.groupby('Koder').agg(Total=('No.','count'),Error=('Ada Error','sum')).reset_index()
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name='Sesuai', x=kd['Koder'],y=kd['Total']-kd['Error'],marker_color='#1a7a4a',opacity=0.85))
        fig3.add_trace(go.Bar(name='Error',  x=kd['Koder'],y=kd['Error'],             marker_color='#c0392b',opacity=0.85))
        fig3.update_layout(**CHART_THEME, height=280, barmode='stack',
                           xaxis=dict(title='',**GRID), yaxis=dict(title='Jumlah',**GRID),
                           legend=dict(bgcolor='rgba(255,255,255,0.6)',font_color='#1c3a5a'))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-header"><span class="section-icon">⚖️</span><h2>Risiko Finansial per Berkas</h2></div>', unsafe_allow_html=True)
        rc = df['Risiko Finansial'].value_counts().reset_index(); rc.columns=['Risiko','Jumlah']
        cmap = {'Rendah':'#1a7a4a','Sedang':'#c87722','Tinggi':'#c0392b','Kritis':'#7b0d0d','N/A':'#7aaac8'}
        fig4 = px.bar(rc, x='Risiko', y='Jumlah', color='Risiko', color_discrete_map=cmap)
        fig4.update_layout(**CHART_THEME, height=280, showlegend=False,
                           xaxis=dict(title='Tingkat Risiko',**GRID), yaxis=dict(title='Jumlah Berkas',**GRID))
        st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ANALISIS ERROR CODING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Analisis Error Coding":
    st.markdown("## 🔍 Analisis Ketidaktepatan Coding")
    st.markdown("<p style='color:#5a7a95;font-size:0.85rem;'>Identifikasi pola error: uppercoding, undercoding, dan indikasi spesifik kesalahan koder.</p>", unsafe_allow_html=True)

    error_df = df[df['Status Klaim']=='Berpotensi Error'].copy()
    n_error = len(error_df); total = len(df)
    if n_error == 0:
        st.info("Tidak ada berkas berpotensi error dengan filter saat ini.")
        st.stop()

    n_upper = len(error_df[error_df['Tipe Ketidaktepatan']=='Uppercoding'])
    n_under = len(error_df[error_df['Tipe Ketidaktepatan']=='Undercoding'])

    k1,k2,k3,k4 = st.columns(4)
    for col,color,label,val,sub in [
        (k1,"red",   "🔴 Total Error",   f"{n_error}",      f"{n_error/total*100:.1f}% dari semua berkas"),
        (k2,"orange","🔺 Uppercoding",   f"{n_upper}",      f"{n_upper/n_error*100:.0f}% dari kasus error"),
        (k3,"blue",  "🔻 Undercoding",   f"{n_under}",      f"{n_under/n_error*100:.0f}% dari kasus error"),
        (k4,"green", "✅ Berkas Sesuai", f"{total-n_error}", f"{(total-n_error)/total*100:.1f}% aman"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card {color}"><div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    top2 = error_df['Indikasi Error Coding'].value_counts().head(2)
    st.markdown(f"""
    <div class="narasi-box"><p>🔎 <strong>Interpretasi:</strong>
    Dari {n_error} berkas error, <strong>{n_upper} ({n_upper/n_error*100:.0f}%)</strong> adalah <em>uppercoding</em>.
    Dua indikasi teratas: <strong>"{top2.index[0]}" ({top2.iloc[0]} kasus)</strong>
    dan <strong>"{top2.index[1] if len(top2)>1 else '—'}"</strong>.
    Error ini umumnya timbul karena koder tidak membaca rekam medis secara menyeluruh.</p></div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_e, col_f = st.columns([1.1, 0.9])
    with col_e:
        st.markdown('<div class="section-header"><span class="section-icon">📌</span><h2>Jenis Indikasi Error Coding</h2></div>', unsafe_allow_html=True)
        et = error_df['Indikasi Error Coding'].value_counts().reset_index(); et.columns=['Indikasi','Jumlah']
        fig = px.bar(et, x='Jumlah', y='Indikasi', orientation='h', color='Jumlah',
                     color_continuous_scale=['#7aaac8','#2e7bb5','#1c3a5a'])
        fig.update_layout(**CHART_THEME, height=340,
                          yaxis=dict(title='',autorange='reversed',**GRID),
                          xaxis=dict(title='Jumlah Kasus',**GRID), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_f:
        st.markdown('<div class="section-header"><span class="section-icon">🔄</span><h2>Upper vs Undercoding per Koder</h2></div>', unsafe_allow_html=True)
        tk = error_df.groupby(['Koder','Tipe Ketidaktepatan']).size().reset_index(name='n')
        fig2 = px.bar(tk, x='Koder', y='n', color='Tipe Ketidaktepatan', barmode='group',
                      color_discrete_map={'Uppercoding':'#c0392b','Undercoding':'#2e7bb5'})
        fig2.update_layout(**CHART_THEME, height=340,
                           xaxis=dict(title='',**GRID), yaxis=dict(title='Jumlah',**GRID),
                           legend=dict(bgcolor='rgba(255,255,255,0.6)',font_color='#1c3a5a'))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header"><span class="section-icon">📅</span><h2>Tren Error Coding per Tanggal Masuk</h2></div>', unsafe_allow_html=True)
    tren = df.groupby([df['Tgl. Masuk'].dt.date,'Status Klaim']).size().reset_index(name='n')
    tren.columns=['Tanggal','Status','Jumlah']
    fig3 = px.line(tren, x='Tanggal', y='Jumlah', color='Status', markers=True,
                   color_discrete_map={'Sesuai':'#1a7a4a','Berpotensi Error':'#c0392b'})
    fig3.update_layout(**CHART_THEME, height=220,
                       xaxis=dict(title='',**GRID), yaxis=dict(title='Jumlah Berkas',**GRID),
                       legend=dict(bgcolor='rgba(255,255,255,0.6)',font_color='#1c3a5a'))
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ANALISIS FINANSIAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Analisis Finansial":
    st.markdown("## 💰 Analisis Finansial Klaim")
    st.markdown("<p style='color:#5a7a95;font-size:0.85rem;'>Perbandingan Tarif INA-CBGs vs Tarif RS — potensi kerugian dan distribusi gap.</p>", unsafe_allow_html=True)

    total_cbgs = df['Total Tarif INA-CBGs'].sum()
    total_rs   = df['Tarif RS Diajukan'].sum()
    total_gap  = df['Selisih (Gap)'].sum()
    error_df   = df[df['Status Klaim']=='Berpotensi Error']
    error_gap  = error_df['Selisih (Gap)'].sum()

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(f'<div class="metric-card steel"><div class="metric-label">💊 Total INA-CBGs</div><div class="metric-value">{fmt_rp(total_cbgs)}</div><div class="metric-sub">tarif standar BPJS</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="metric-card orange"><div class="metric-label">📤 Total Klaim RS</div><div class="metric-value">{fmt_rp(total_rs)}</div><div class="metric-sub">diajukan ke BPJS</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="metric-card red"><div class="metric-label">💸 Total Gap</div><div class="metric-value">{fmt_rp(total_gap)}</div><div class="metric-sub">{total_gap/total_cbgs*100:.1f}% dari INA-CBGs</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="metric-card purple"><div class="metric-label">⚠️ Gap Berkas Error</div><div class="metric-value">{fmt_rp(error_gap)}</div><div class="metric-sub">khusus berpotensi error</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="narasi-box"><p>💡 <strong>Narasi Finansial:</strong>
    Total tarif INA-CBGs yang seharusnya diterima RS adalah <strong>{fmt_rp(total_cbgs)}</strong>,
    namun RS hanya mengajukan <strong>{fmt_rp(total_rs)}</strong>.
    Gap sebesar <strong>{fmt_rp(abs(total_gap))}</strong> terjadi karena koder tidak mengkode diagnosa/prosedur secara lengkap.
    Berkas error menyumbang <strong>{fmt_rp(abs(error_gap))}</strong> ({error_gap/total_gap*100:.0f}% dari total gap).</p></div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_g, col_h = st.columns(2)
    with col_g:
        st.markdown('<div class="section-header"><span class="section-icon">📊</span><h2>INA-CBGs vs Klaim RS per Bangsal</h2></div>', unsafe_allow_html=True)
        bf = df.groupby('Bangsal').agg(INA_CBGs=('Total Tarif INA-CBGs','sum'),Klaim_RS=('Tarif RS Diajukan','sum')).reset_index().sort_values('INA_CBGs',ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='INA-CBGs',y=bf['Bangsal'],x=bf['INA_CBGs'],orientation='h',marker_color='#2e7bb5',opacity=0.85))
        fig.add_trace(go.Bar(name='Klaim RS', y=bf['Bangsal'],x=bf['Klaim_RS'], orientation='h',marker_color='#c87722',opacity=0.85))
        fig.update_layout(**CHART_THEME, height=340, barmode='group',
                          yaxis=dict(title='',**GRID), xaxis=dict(title='Nominal (Rp)',**GRID),
                          legend=dict(bgcolor='rgba(255,255,255,0.6)',font_color='#1c3a5a'))
        st.plotly_chart(fig, use_container_width=True)

    with col_h:
        st.markdown('<div class="section-header"><span class="section-icon">📉</span><h2>Distribusi Gap (%) per Berkas</h2></div>', unsafe_allow_html=True)
        fig2 = px.histogram(df.dropna(subset=['Gap %']),x='Gap %',nbins=25,color_discrete_sequence=['#2e7bb5'])
        fig2.add_vline(x=df['Gap %'].mean(),line_dash='dash',line_color='#c87722',
                       annotation_text=f"Rata-rata: {df['Gap %'].mean():.1f}%",annotation_font_color='#c87722')
        fig2.update_layout(**CHART_THEME, height=340,
                           xaxis=dict(title='Gap (%)',**GRID), yaxis=dict(title='Jumlah Berkas',**GRID))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header"><span class="section-icon">🔝</span><h2>Top 10 Berkas Gap Terbesar</h2></div>', unsafe_allow_html=True)
    top10 = df.nsmallest(10,'Selisih (Gap)')[['No.','Nama Pasien','Kode INACBG','Deskripsi INACBG',
                                               'Total Tarif INA-CBGs','Tarif RS Diajukan','Selisih (Gap)','Gap %',
                                               'Bangsal','Koder','Status Klaim']].copy()
    for c in ['Total Tarif INA-CBGs','Tarif RS Diajukan','Selisih (Gap)']:
        top10[c] = top10[c].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "—")
    st.dataframe(top10, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — LOG TRANSAKSI KLAIM
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Log Transaksi Klaim":
    st.markdown("## 📋 Log Riwayat Transaksi Audit Klaim")
    st.markdown("<p style='color:#5a7a95;font-size:0.85rem;'>Rincian tiap berkas: <strong>Biaya RS</strong>, <strong>Tarif INA-CBGs</strong>, gap, indikasi error, dan status.</p>", unsafe_allow_html=True)

    search = st.text_input("🔎 Cari nama pasien / kode klaim / bangsal...", placeholder="Ketik untuk mencari...")
    display_df = df.copy()
    if search:
        mask = (display_df['Nama Pasien'].str.contains(search,case=False,na=False) |
                display_df['No. Klaim / SEP'].str.contains(search,case=False,na=False) |
                display_df['Bangsal'].str.contains(search,case=False,na=False) |
                display_df['Kode INACBG'].str.contains(search,case=False,na=False))
        display_df = display_df[mask]

    st.markdown(f"<p style='color:#5a7a95;font-size:0.8rem;'>Menampilkan <strong style='color:#1c2e45'>{len(display_df)}</strong> dari {len(df)} berkas</p>", unsafe_allow_html=True)

    cols_show = ['No.','Tgl. Masuk','Tgl. Pulang','LOS','Nama Pasien','Kode INACBG','Deskripsi INACBG',
                 'Bangsal','Koder','Jenis','Total Tarif INA-CBGs','Tarif RS Diajukan','Selisih (Gap)','Gap %',
                 'Indikasi Error Coding','Status Klaim','Tipe Ketidaktepatan','Risiko Finansial','Rekomendasi Mitigasi']
    cols_show = [c for c in cols_show if c in display_df.columns]
    log_df    = display_df[cols_show].copy()
    log_df['Total Tarif INA-CBGs'] = log_df['Total Tarif INA-CBGs'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "—")
    log_df['Tarif RS Diajukan']    = log_df['Tarif RS Diajukan'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "—")
    log_df['Selisih (Gap)']        = log_df['Selisih (Gap)'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "—")

    st.dataframe(log_df, use_container_width=True, hide_index=True, height=520)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        display_df[cols_show].to_excel(writer, index=False, sheet_name='Log Klaim')
    buf.seek(0)
    st.download_button("⬇️ Unduh Log sebagai Excel", data=buf,
                       file_name="log_audit_klaim_optima_cdi.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — MITIGASI & REKOMENDASI
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛡️ Mitigasi & Rekomendasi":
    st.markdown("## 🛡️ Mitigasi Otomatis & Rekomendasi Tindak Lanjut")
    st.markdown("<p style='color:#5a7a95;font-size:0.85rem;'>Sistem deteksi + mitigasi otomatis untuk setiap jenis error coding — berlaku untuk semua RS di Indonesia.</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-warning">
    <div class="alert-title" style="color:#c8960a;">⚠️ Tentang OPTIMA-CDI & Konteks Mitigasi</div>
    <p class="alert-box-text">OPTIMA-CDI dirancang untuk <strong>digunakan di semua RS Indonesia</strong> dengan format
    rekap klaim INA-CBGs standar. Ketika ditemukan ketidaktepatan coding, sistem secara otomatis:
    (1) mengklasifikasikan jenis error, (2) mengukur dampak finansial per berkas, dan
    (3) memberikan rekomendasi mitigasi spesifik yang bisa langsung ditindaklanjuti tim CDI/koder/manajemen.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header"><span class="section-icon">📐</span><h2>Matriks Mitigasi per Jenis Error</h2></div>', unsafe_allow_html=True)
    matrix = [
        ("🔴 Uppercoding – Overcoding Grup Tarif","RS mengkode ke grup tarif lebih tinggi dari kondisi klinis sebenarnya.",
         "Turunkan grup severity; review rekam medis; verifikasi dengan panduan grouper INA-CBGs.",
         "Finansial Sedang–Tinggi: risiko klaim ditolak BPJS & dikenai denda.","alert-danger","#c0392b"),
        ("🟠 CC/MCC Tidak Dikodekan","Komplikasi/komorbiditas ada di rekam medis tapi tidak dikodekan.",
         "Koder wajib membaca seluruh resume medis & laporan lab. Tambahkan kode ICD-10 CC/MCC.",
         "Finansial Tinggi: kehilangan pendapatan signifikan.","alert-warning","#c8960a"),
        ("🟠 Komplikasi Tidak Dikodekan","Komplikasi pasca tindakan tidak dicantumkan dalam kode sekunder.",
         "Review laporan operasi & catatan perawat. Tambahkan kode komplikasi relevan.",
         "Finansial Sedang: kehilangan pendapatan per episode.","alert-warning","#c8960a"),
        ("🟡 PDx vs SDx Terbalik","Diagnosis utama dan sekunder tertukar, grup INA-CBGs tidak mencerminkan kondisi utama.",
         "Tetapkan PDx berdasarkan kondisi utama penerimaan. Konsultasikan dengan DPJP jika perlu.",
         "Finansial Rendah–Sedang.","alert-warning","#c8960a"),
        ("🟡 Top-Up Tidak Dilengkapi","Kode top-up tidak dicantumkan padahal alkes/prosedur sudah digunakan.",
         "Lengkapi formulir top-up sebelum submission. Verifikasi dengan farmasi & logistik RS.",
         "Finansial Sedang: top-up bisa menambah tarif signifikan.","alert-warning","#c8960a"),
        ("🔵 Undercoding Severity","Tingkat keparahan dikode lebih rendah dari kondisi klinis pasien.",
         "Naikkan grup severity sesuai bukti klinis. Tambahkan diagnosis penyerta yang relevan.",
         "Finansial Tinggi: RS kehilangan pendapatan karena tarif terlalu rendah.","narasi-box","#2e7bb5"),
        ("🔵 Kode Prosedur Tidak Sesuai","Prosedur tidak sesuai dengan kode ICD-9-CM yang diklaim.",
         "Verifikasi kode prosedur dengan laporan operasi. Gunakan panduan ICD-9-CM terbaru.",
         "Finansial Sedang: potensi klaim ditolak atau tarif tidak optimal.","narasi-box","#2e7bb5"),
    ]
    for title,desc,mit,dampak,cls,tc in matrix:
        st.markdown(f"""
        <div class="{cls}" style="margin-bottom:10px;">
            <div class="alert-title" style="color:{tc};">{title}</div>
            <p class="alert-box-text"><strong>Masalah:</strong> {desc}<br>
            <strong>Mitigasi:</strong> {mit}<br>
            <strong>Dampak Finansial:</strong> {dampak}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-icon">📋</span><h2>Daftar Berkas Error + Rekomendasi Mitigasi Otomatis</h2></div>', unsafe_allow_html=True)

    error_df = df[df['Status Klaim']=='Berpotensi Error'].copy()
    mit_cols = ['No.','Nama Pasien','Kode INACBG','Total Tarif INA-CBGs','Tarif RS Diajukan',
                'Selisih (Gap)','Gap %','Tipe Ketidaktepatan','Indikasi Error Coding','Risiko Finansial','Rekomendasi Mitigasi']
    mit_cols = [c for c in mit_cols if c in error_df.columns]
    mit_df   = error_df[mit_cols].copy()
    for c in ['Total Tarif INA-CBGs','Tarif RS Diajukan','Selisih (Gap)']:
        if c in mit_df.columns:
            mit_df[c] = mit_df[c].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "—")
    st.dataframe(mit_df, use_container_width=True, hide_index=True, height=400)

    buf2 = BytesIO()
    with pd.ExcelWriter(buf2, engine='openpyxl') as writer:
        error_df[mit_cols].to_excel(writer, index=False, sheet_name='Mitigasi Error')
    buf2.seek(0)
    st.download_button("⬇️ Unduh Laporan Mitigasi (.xlsx)", data=buf2,
                       file_name="laporan_mitigasi_optima_cdi.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-icon">🤖</span><h2>Analisis Otomatis — Siap Presentasi</h2></div>', unsafe_allow_html=True)

    total=len(df); n_error=len(error_df)
    total_cbgs=df['Total Tarif INA-CBGs'].sum(); total_rs=df['Tarif RS Diajukan'].sum()
    total_gap=df['Selisih (Gap)'].sum()
    top_err=error_df['Indikasi Error Coding'].value_counts()
    top_bangsal=error_df['Bangsal'].value_counts(); top_koder=error_df['Koder'].value_counts()

    st.markdown(f"""
    <div class="alert-success">
    <div class="alert-title" style="color:#1a7a4a;">✅ Ringkasan Analisis Otomatis OPTIMA-CDI</div>
    <p class="alert-box-text">
    <strong>1. Volume & Tingkat Error:</strong><br>
    Dari <strong>{total} berkas</strong>, sebanyak <strong>{n_error} ({n_error/total*100:.1f}%)</strong>
    berpotensi error — hampir <strong>1 dari {total//n_error if n_error else '?'} berkas</strong> memerlukan tindak lanjut.<br><br>
    <strong>2. Dampak Finansial:</strong><br>
    Total tarif INA-CBGs <strong>{fmt_rp(total_cbgs)}</strong>, RS mengajukan <strong>{fmt_rp(total_rs)}</strong>.
    Gap <strong>{fmt_rp(abs(total_gap))}</strong> ({abs(total_gap/total_cbgs*100):.1f}%) adalah potensi pendapatan tidak tertagih optimal.<br><br>
    <strong>3. Akar Masalah:</strong><br>
    Error terbanyak: <strong>"{top_err.index[0]}" ({top_err.iloc[0]} kasus)</strong>.
    Bangsal terdampak: <strong>{top_bangsal.index[0]}</strong>. Koder error terbanyak: <strong>{top_koder.index[0]}</strong>.<br><br>
    <strong>4. Rekomendasi Strategis:</strong><br>
    (a) Concurrent review di bangsal berisiko tinggi sebelum submit ke BPJS.<br>
    (b) Refreshment pelatihan INA-CBGs untuk koder dengan error tertinggi.<br>
    (c) Integrasikan OPTIMA-CDI sebagai pre-submission quality gate.<br>
    (d) Upload file rekap klaim RS manapun — sistem otomatis mendeteksi & merekomendasikan mitigasi.
    </p></div>
    """, unsafe_allow_html=True)
