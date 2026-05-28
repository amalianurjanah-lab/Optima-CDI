import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA WARNA
# ==========================================
st.set_page_config(
    page_title="OPTIMA-CDI - Advanced Claims Audit Analytics",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [data-testid="stSidebar"] {
            font-family: 'Inter', sans-serif;
            background-color: #FBF9FB !important;
        }
        .metric-card {
            background-color: #FFFFFF;
            padding: 22px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.03);
            border: 1px solid #F3E8FF;
        }
        .metric-title {
            color: #6B7280;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 6px;
        }
        .metric-value {
            color: #1F2937;
            font-size: 24px;
            font-weight: 700;
        }
        .header-container {
            background: linear-gradient(135deg, #7C3AED 0%, #EC4899 100%);
            padding: 25px 30px;
            border-radius: 20px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 10px 20px rgba(124, 58, 237, 0.12);
        }
        .chart-box {
            background-color: white; 
            padding: 22px; 
            border-radius: 16px; 
            border: 1px solid #F3E8FF;
            box-shadow: 0 2px 8px rgba(0,0,0,0.01);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR UTAMA
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding-bottom: 15px; border-bottom: 2px solid #F3E8FF; margin-bottom: 20px;">
            <span style="font-size: 22px; font-weight: 700; background: linear-gradient(90deg, #7C3AED, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">OPTIMA-CDI</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📁 Unggah Data Rekap")
    uploaded_file = st.file_uploader("Pilih file anda (.xlsx)", type=["xlsx"])

# Header Utama
st.markdown("""
    <div class="header-container">
        <h1 style="margin: 0; font-size: 26px; font-weight: 700;">OPTIMA-CDI — Advanced Cost Impact Analytics</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 13.5px;">Dashboard Analitik Dampak Ketidaktepatan Coding terhadap Efisiensi Biaya INA-CBGs</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. CORE PROCESSING ENGINE
# ==========================================
if uploaded_file is not None:
    try:
        # Load dengan skiprows=2 karena baris data riil dimulai di baris ke-3
        df = pd.read_excel(uploaded_file, sheet_name=0, skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        
        # Mapping presisi agar tabel log terisi penuh
        mapping_presisi = {
            'No.': 'no_urut',
            'Tgl. Pulang': 'tanggal_pulang',
            'No. RM': 'no_rm',
            'Nama Pasien': 'nama_pasien',
            'Kode INACBG': 'kode_inacbg',
            'Selisih (Gap)': 'selisih',
            'Total Tarif INA-CBGs': 'tarif_inacbg',
            'Tarif RS Diajukan': 'tarif_rs',
            'Indikasi Error Coding': 'error_coding',
            'Bangsal': 'poli_bangsal'
        }
        df = df.rename(columns=mapping_presisi)
        
        # Fungsi pembersihan angka finansial agar nilai minus (-) tidak hilang
        def clean_money_value(val):
            if pd.isna(val):
                return 0.0
            if isinstance(val, (int, float)):
                return float(val)
            
            val_str = str(val).strip()
            # Bersihkan titik pemisah ribuan jika ada
            val_str = val_str.replace('.', '')
            # Tangani format tanda kurung akuntansi (1000) menjadi -1000
            if val_str.startswith('(') and val_str.endswith(')'):
                val_str = '-' + val_str[1:-1]
            try:
                return float(val_str)
            except ValueError:
                return 0.0

        for num_col in ['selisih', 'tarif_inacbg', 'tarif_rs']:
            if num_col in df.columns:
                df[num_col] = df[num_col].apply(clean_money_value)
        
        # Penanganan teks kosong
        df['error_coding'] = df['error_coding'].apply(lambda x: 'Koding Tepat / Sesuai' if pd.isna(x) or str(x).strip() in ['', 'nan'] else str(x).strip())
        df['poli_bangsal'] = df['poli_bangsal'].apply(lambda x: 'Lain-Lain' if pd.isna(x) or str(x).strip() in ['', 'nan'] else str(x).strip())
        
        df['tanggal_pulang'] = pd.to_datetime(df['tanggal_pulang'], errors='coerce')
        df = df.dropna(subset=['tanggal_pulang'])
        df = df.sort_values(by='tanggal_pulang').reset_index(drop=True)
        
        # FILTER KEBOCORAN (Hanya hitung nilai jika selisih < 0)
        df['nilai_leakage'] = df['selisih'].apply(lambda x: abs(x) if x < 0 else 0)

        # --------------------------------------
        # A. METRIK KPI UTAMA
        # --------------------------------------
        total_audit = len(df)
        total_inacbg = float(df['tarif_inacbg'].sum())
        total_rs = float(df['tarif_rs'].sum())
        net_gap = float(df['selisih'].sum())
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">📋 Total Kasus Diaudit</div><div class="metric-value">{total_audit:,} Berkas</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">💰 Total Klaim INA-CBGs</div><div class="metric-value" style="color: #22C55E;">Rp {total_inacbg:,.0f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">🏥 Total Tarif Diajukan RS</div><div class="metric-value" style="color: #6B7280;">Rp {total_rs:,.0f}</div></div>', unsafe_allow_html=True)
        with c4:
            warna_gap = "#EF4444" if net_gap < 0 else "#22C55E"
            label_gap = "Defisit / Leakage" if net_gap < 0 else "Surplus Finansial"
            st.markdown(f'<div class="metric-card"><div class="metric-title">⚠️ Total Selisih Tarif ({label_gap})</div><div class="metric-value" style="color: {warna_gap};">Rp {net_gap:,.0f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --------------------------------------
        # B. GRAFIK BARIS PERTAMA
        # --------------------------------------
        ch1, ch2 = st.columns([3, 2])
        
        with ch1:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.subheader("🔍 Distribusi Finansial Berdasarkan Jenis Error Coding")
            
            error_summary = df.groupby('error_coding')['nilai_leakage'].agg(['count', 'sum']).reset_index()
            error_summary.columns = ['Jenis Error', 'Jumlah Kasus', 'Total Dampak Kerugian (Rp)']
            error_summary = error_summary[error_summary['Total Dampak Kerugian (Rp)'] > 0]
            error_summary = error_summary.sort_values(by='Total Dampak Kerugian (Rp)', ascending=True)
            
            fig_error = px.bar(
                error_summary, 
                x='Total Dampak Kerugian (Rp)', 
                y='Jenis Error', 
                orientation='h',
                color='Total Dampak Kerugian (Rp)',
                color_continuous_scale=['#EC4899', '#7C3AED'],
                hover_data=['Jumlah Kasus']
            )
            fig_error.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, coloraxis_showscale=False)
            st.plotly_chart(fig_error, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with ch2:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.subheader("🏢 Distribusi Dampak Error per Poli / Bangsal")
            
            # Perbaikan filter Pie Chart agar datanya sinkron kembali ke proporsi semula
            poli_summary = df.groupby('poli_bangsal')['nilai_leakage'].sum().reset_index()
            poli_summary.columns = ['Poli / Bangsal', 'Total Kebocoran Biaya']
            poli_summary = poli_summary[poli_summary['Total Kebocoran Biaya'] > 0]
            
            fig_poli = px.pie(
                poli_summary, 
                values='Total Kebocoran Biaya', 
                names='Poli / Bangsal', 
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_poli.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, showlegend=True)
            st.plotly_chart(fig_poli, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --------------------------------------
        # C. TREN TANGGAL
        # --------------------------------------
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.subheader("📅 Tren Dampak Finansial Error Bulanan (Periode Mei 2026)")
        
        df['hari_pulang'] = df['tanggal_pulang'].dt.strftime('%d %b %Y')
        trend_summary = df.groupby(['hari_pulang', 'tanggal_pulang'])['nilai_leakage'].sum().reset_index()
        trend_summary = trend_summary.sort_values(by='tanggal_pulang')
        
        fig_trend = px.line(
            trend_summary, 
            x='hari_pulang', 
            y='nilai_leakage',
            labels={'hari_pulang': 'Tanggal Kepulangan Pasien', 'nilai_leakage': 'Akumulasi Kerugian Biaya (Rp)'},
            markers=True
        )
        fig_trend.update_traces(line_color='#7C3AED', line_width=3, marker=dict(size=8, color='#EC4899'))
        fig_trend.update_layout(margin=dict(t=15, b=15, l=10, r=10), height=260)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --------------------------------------
        # D. TABEL LOG UTAMA (TERISI 100%)
        # --------------------------------------
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.subheader("📋 Log Riwayat Transaksi Audit Klaim Utama")
        
        df_log = df.copy()
        df_log['tanggal_pulang'] = df_log['tanggal_pulang'].dt.strftime('%Y-%m-%d')
        
        display_cols = {
            'no_urut': 'No', 
            'tanggal_pulang': 'Tanggal Pulang', 
            'no_rm': 'No RM',
            'nama_pasien': 'Nama Pasien', 
            'kode_inacbg': 'Kode INA-CBG',
            'error_coding': 'Indikasi Kesalahan Koding', 
            'poli_bangsal': 'Poli / Bangsal', 
            'selisih': 'Selisih Gap (Rp)'
        }
        
        avail_cols = [c for c in display_cols.keys() if c in df_log.columns]
        df_display_final = df_log[avail_cols].rename(columns=display_cols)
        
        st.dataframe(df_display_final, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Gagal memproses struktur internal kolom berkas excel: {e}")