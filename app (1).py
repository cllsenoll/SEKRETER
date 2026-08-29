import streamlit as st
import pandas as pd
import io
import urllib.parse
import os
import base64
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(
    page_title="Günlük Personel Hesap ve Kasa Takibi",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b132b 0%, #1c2541 50%, #0b132b 100%);
    color: #ffffff;
}
[data-testid="stSidebar"] {
    background-color: #1a365d;
    border-right: 2px solid #ff7b00;
}
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
    color: #ffffff !important;
}
.custom-card {
    background: #131b2e;
    border: 1px solid #2a3b5c;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
}
.card-top {
    display: flex;
    align-items: center;
    gap: 16px;
}
.profile-img {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #ffb703;
    background-color: #0b132b;
    flex-shrink: 0;
}
.person-name {
    font-size: 1.1rem;
    font-weight: bold;
    color: #ffffff;
    letter-spacing: 0.5px;
}
.person-title {
    font-size: 0.85rem;
    color: #ffb703;
    margin-top: 2px;
    font-weight: 500;
}
.metrics-bar {
    display: flex;
    gap: 8px;
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    overflow-x: auto;
}
.metric-pill {
    background: #1a2642;
    border: 1px solid #2a3b5c;
    border-radius: 8px;
    padding: 6px 10px;
    text-align: center;
    flex: 1;
    min-width: 75px;
}
.pill-label {
    font-size: 0.65rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: bold;
}
.pill-value {
    font-size: 0.85rem;
    font-weight: bold;
    color: #00ff88;
    margin-top: 2px;
}
.kasa-panel {
    background: linear-gradient(145deg, #1e3a8a, #0f172a);
    border: 2px solid #ff7b00;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 6px 20px rgba(255, 123, 0, 0.25);
    margin-top: 15px;
    margin-bottom: 25px;
}
.stNumberInput label, .stMetric label, .stTextInput label {
    color: #ffffff !important;
}
h1, h2, h3, h4 {
    color: #ffffff !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.stButton>button {
    background: linear-gradient(90deg, #ff7b00 0%, #ff9e00 100%);
    color: white;
    border-radius: 8px;
    font-weight: bold;
    border: none;
    box-shadow: 0 4px 10px rgba(255, 123, 0, 0.3);
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ff9e00 0%, #ffb703 100%);
    color: white;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/money-bag.png", width=60)
    st.markdown("### F4 / HESAP")
    st.markdown("**Görükle Acente**")
    st.markdown("---")
    st.markdown("👤 **Aktif Kullanıcı**")
    st.info("CELAL ŞENOL (Şube Şefi)")
    st.markdown("---")
    uploaded_file = st.file_uploader("HESAP Dosyasını Yükle (Excel veya CSV)", type=["xlsx", "xls", "csv"])
    st.markdown("---")
    st.button("💰 HESAP", use_container_width=True, type="primary")

st.markdown("# 💰 Günlük Personel Hesap ve Kasa Takibi")
st.markdown("#### Personel Durum Kartları")
st.markdown("---")

df = None
excel_kops_degeri = None

if uploaded_file is not None:
    try:
        file_name_lower = uploaded_file.name.lower()
        file_bytes = uploaded_file.getvalue()
        
        if file_name_lower.endswith('.csv'):
            for sep in [';', ',', '\t']:
                for enc in ['cp1254', 'utf-8', 'latin1']:
                    try:
                        temp_df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc)
                        if len(temp_df.columns) > 1:
                            df = temp_df
                            break
                    except:
                        continue
                if df is not None:
                    break
            if df is None:
                df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine='python', encoding='cp1254')
        else:
            df = pd.read_excel(uploaded_file)
        
        if df is not None:
            df.columns = df.columns.astype(str).str.strip()
            rename_map = {}
            for col in df.columns:
                col_clean = col.lower().replace('İ', 'i').replace('ı', 'i').replace('I', 'i')
                if "personel" in col_clean and ("adi" in col_clean or "ad" in col_clean or col_clean == "personel"):
                    rename_map[col] = "Personel"
                elif "nakit" in col_clean and "ft" in col_clean and ("tutar" in col_clean or "top" in col_clean):
                    rename_map[col] = "Nakit Ft. Tutarı Top"
                elif "nakit" in col_clean and "odeme" in col_clean:
                    rename_map[col] = "Nakit Ödeme Tutarı Topl."
            
            if rename_map:
                df = df.rename(columns=rename_map)

            if "Personel" in df.columns:
                df = df[df["Personel"].notna()]
                df = df[~df["Personel"].astype(str).str.lower().str.contains("toplam")]

            for col in df.columns:
                if "kops" in col.lower():
                    val_candidates = pd.to_numeric(df[col], errors='coerce').dropna()
                    if not val_candidates.empty:
                        excel_kops_degeri = float(val_candidates.iloc[0])

            st.sidebar.success("Dosya başarıyla yüklendi ve işlendi!")
    except Exception as e:
        st.sidebar.error(f"Kritik Dosya Okuma Hatası: {e}")
        df = None

if df is None:
    st.info("📂 Lütfen işlem yapmak için sol menüden **HESAP** adlı dosyanızı (Excel veya CSV) yükleyin.")
else:
    required_cols = ["Personel", "Nakit Ft. Tutarı Top", "Nakit Ödeme Tutarı Topl."]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Yüklenen dosyada aradığımız sütunlar bulunamadı!\n**Eksik Sütunlar:** {missing_cols}")
        st.stop()

    if len(df) == 0:
        st.error("❌ Yüklenen dosya tamamen boş.")
        st.stop()

    def clean_turkish_number(val):
        if pd.isna(val):
            return 0.0
        val_str = str(val).strip()
        if val_str == '' or val_str.lower() == 'nan':
            return 0.0
        val_str = val_str.replace('TL', '').replace('₺', '').strip()
        try:
            if ',' in val_str and '.' in val_str:
                if val_str.rfind(',') > val_str.rfind('.'):
                    val_str = val_str.replace('.', '').replace(',', '.')
                else:
                    val_str = val_str.replace(',', '')
            elif ',' in val_str:
                val_str = val_str.replace(',', '.')
            return float(val_str)
        except:
            return 0.0

    df["Nakit Ft. Tutarı Top"] = df["Nakit Ft. Tutarı Top"].apply(clean_turkish_number)
    df["Nakit Ödeme Tutarı Topl."] = df["Nakit Ödeme Tutarı Topl."].apply(clean_turkish_number)

    @st.cache_data(ttl=300)
    def get_base64_avatar(person_name):
        clean_name = person_name.strip()
        tr_chars = {"İ": "i", "I": "i", "ı": "i", "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g", "Ç": "c", "ç": "c", "Ö": "o", "ö": "o", "Ü": "u", "ü": "u"}
        for k, v in tr_chars.items():
            clean_name = clean_name.replace(k, v)
        
        formatted_name = clean_name.lower().replace(" ", "_")
        github_user = "cllsenoll"
        github_repo = "SEKRETER"
        branch_name = "main"
        
        folders = ["", "fotograflar/", "img/", "images/", "resimler/", "foto/"]
        extensions = ["png", "jpg", "jpeg", "JPG", "PNG"]
        
        import urllib.request
        for folder in folders:
            for ext in extensions:
                url = f"https://raw.githubusercontent.com/{github_user}/{github_repo}/{branch_name}/{folder}{formatted_name}.{ext}"
                try:
                    req = urllib.request.urlopen(url, timeout=2)
                    img_bytes = req.read()
                    encoded = base64.b64encode(img_bytes).decode()
                    mime_type = "image/png" if ext.lower() == "png" else "image/jpeg"
                    return f"data:{mime_type};base64,{encoded}"
                except:
                    continue
                
        return f"https://ui-avatars.com/api/?name={urllib.parse.quote(person_name)}&background=1e3a8a&color=ffb703&bold=true&size=128"

    cols_per_row = 2 
    for i in range(0, len(df), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(df):
                row = df.iloc[idx]
                person_name = str(row["Personel"])
                nakit_ft = float(row["Nakit Ft. Tutarı Top"])
                nakit_odeme = float(row["Nakit Ödeme Tutarı Topl."])
                
                banka_key = f"banka_{idx}"
                odenen_key = f"odenen_{idx}"
                completed_key = f"completed_{idx}"
                
                with cols[j]:
                    temp_banka = st.session_state.get(banka_key, 0.0)
                    hesap_tutar = nakit_ft + nakit_odeme - temp_banka
                    
                    if odenen_key not in st.session_state:
                        st.session_state[odenen_key] = hesap_tutar
                    
                    odenen_val = float(st.session_state.get(odenen_key, hesap_tutar))
                    is_completed = st.session_state.get(completed_key, False)
                    avatar_src = get_base64_avatar(person_name)
                    status_text = '<span style="color: #00ff88; font-size: 0.75rem; font-weight: bold; float: right;">✔ İşlem Tamam</span>' if is_completed else ''

                    card_html = f"""<div class="custom-card"><div class="card-top"><img src="{avatar_src}" class="profile-img"><div style="flex-grow: 1;">{status_text}<div class="person-name">{person_name}</div><div class="person-title">Saha Kuryesi</div></div></div><div class="metrics-bar"><div class="metric-pill"><div class="pill-label">Nakit Ft.</div><div class="pill-value" style="color: #60a5fa;">{nakit_ft:,.2f}</div></div><div class="metric-pill"><div class="pill-label">Nakit Ödeme</div><div class="pill-value" style="color: #60a5fa;">{nakit_odeme:,.2f}</div></div><div class="metric-pill"><div class="pill-label">Banka/ATM</div><div class="pill-value" style="color: #fbbf24;">{temp_banka:,.2f}</div></div><div class="metric-pill"><div class="pill-label">HESAP (Net)</div><div class="pill-value" style="color: #38bdf8;">{hesap_tutar:,.2f}</div></div><div class="metric-pill"><div class="pill-label">Ödenen</div><div class="pill-value" style="color: #00ff88;">{odenen_val:,.2f}</div></div></div></div>"""
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    with st.expander(f"⚙️ {person_name} - İşlem Detayları", expanded=False):
                        banka_atm = st.number_input("Banka/ATM Tutarı", min_value=0.0, value=float(temp_banka), step=10.0, key=banka_key)
                        
                        def mark_completed(k=completed_key):
                            st.session_state[k] = True

                        odenen_tutar = st.number_input(
                            "Ödenen (Alınan/Verilen)", 
                            min_value=0.0, 
                            value=float(st.session_state[odenen_key]), 
                            step=10.0, 
                            key=odenen_key,
                            on_change=mark_completed
                        )
                        
                        hesap_tutar_guncel = nakit_ft + nakit_odeme - banka_atm
                        if st.session_state.get(odenen_key) != hesap_tutar_guncel:
                            st.session_state[completed_key] = True

                        fark = odenen_tutar - hesap_tutar_guncel
                        if fark > 0:
                            st.markdown(f"<span style='color: #00ff66; font-weight: bold;'>✅ Fazla ({abs(fark):,.2f} TL)</span>", unsafe_allow_html=True)
                        elif fark < 0:
                            st.markdown(f"<span style='color: #ff3333; font-weight: bold;'>✅ Eksik ({abs(fark):,.2f} TL)</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("<span style='color: #00ff66; font-weight: bold;'>✅ Tamam (0.00 TL)</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💵 Genel Şube Kasası / Para Sayma Paneli")

    with st.container():
        st.markdown('<div class="kasa-panel">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            b200 = st.number_input("200 TL Adet", min_value=0, value=st.session_state.get("genel_b200", 0), step=1, key="genel_b200")
            b20 = st.number_input("20 TL Adet", min_value=0, value=st.session_state.get("genel_b20", 0), step=1, key="genel_b20")
        with col2:
            b100 = st.number_input("100 TL Adet", min_value=0, value=st.session_state.get("genel_b100", 0), step=1, key="genel_b100")
            b10 = st.number_input("10 TL Adet", min_value=0, value=st.session_state.get("genel_b10", 0), step=1, key="genel_b10")
        with col3:
            b50 = st.number_input("50 TL Adet", min_value=0, value=st.session_state.get("genel_b50", 0), step=1, key="genel_b50")
            b5 = st.number_input("5 TL Adet", min_value=0, value=st.session_state.get("genel_b5", 0), step=1, key="genel_b5")

        toplam_sayilan_kasa = (b200 * 200) + (b100 * 100) + (b50 * 50) + (b20 * 20) + (b10 * 10) + (b5 * 5)
        st.session_state["genel_net_kasa"] = float(toplam_sayilan_kasa)

        if excel_kops_degeri is not None and "genel_kops_kasa" not in st.session_state:
            st.session_state["genel_kops_kasa"] = excel_kops_degeri

        st.markdown("<br>", unsafe_allow_html=True)
        k_col1, k_col2, k_col3, k_col4 = st.columns(4)
        with k_col1:
            net_kasa_giris = st.number_input("📥 Şube Net Kasa Değeri", min_value=0.0, value=float(st.session_state["genel_net_kasa"]), step=10.0, key="genel_net_kasa")
        with k_col2:
            kops_kasa_giris = st.number_input("📥 KOPS KASA", min_value=0.0, value=float(st.session_state.get("genel_kops_kasa", 0.0)), step=10.0, key="genel_kops_kasa")
        with k_col3:
            atm_yatirilacak_giris = st.number_input("📥 ATM Yatırılacak", min_value=0.0, value=float(st.session_state.get("genel_atm_yatirilacak", 0.0)), step=10.0, key="genel_atm_yatirilacak")
        with k_col4:
            devredecek_hesap = max(0.0, kops_kasa_giris - atm_yatirilacak_giris)
            st.session_state["genel_devredecek"] = devredecek_hesap
            st.metric(label="📥 Devredecek", value=f"{devredecek_hesap:,.2f} TL")
        st.markdown('</div>', unsafe_allow_html=True)

    sube_net_val = float(st.session_state.get('genel_net_kasa', 0.0))
    kops_val = float(st.session_state.get('genel_kops_kasa', 0.0))
    kasa_fark = sube_net_val - kops_val

    st.markdown("---")
    st.markdown("### 📊 Genel Hesap Özeti ve Kasa Durumu")
    
    if kasa_fark < 0:
        st.markdown(f"<div style='background-color: rgba(255, 51, 51, 0.2); border: 2px solid #ff3333; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; color: #ff6b6b;'>⚠️ Kasa Durumu: AÇIK ({abs(kasa_fark):,.2f} TL Eksik)</div>", unsafe_allow_html=True)
    elif kasa_fark > 0:
        st.markdown(f"<div style='background-color: rgba(0, 255, 136, 0.2); border: 2px solid #00ff88; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; color: #00ff88;'>💵 Kasa Durumu: FAZLA ({kasa_fark:,.2f} TL Fazla)</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color: rgba(0, 255, 136, 0.2); border: 2px solid #00ff88; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; color: #00ff88;'>✅ Kasa Durumu: TAMAM (Fark Yok)</div>", unsafe_allow_html=True)

    summary_data = []
    for idx, row in df.iterrows():
        person_name = str(row["Personel"])
        nakit_ft = float(row["Nakit Ft. Tutarı Top"])
        nakit_odeme = float(row["Nakit Ödeme Tutarı Topl."])
        banka_val = st.session_state.get(f"banka_{idx}", 0.0)
        hesap = nakit_ft + nakit_odeme - banka_val
        odenen_val = st.session_state.get(f"odenen_{idx}", hesap)
        fark_val = odenen_val - hesap
        
        durum_metni = f"Fazla: +{fark_val:,.2f} TL" if fark_val > 0 else (f"Eksik: {fark_val:,.2f} TL" if fark_val < 0 else "Tamam")
        summary_data.append({
            "Personel": person_name,
            "Nakit Ft. Top": f"{nakit_ft:,.2f} TL",
            "Nakit Ödeme Tutarı Topl.": f"{nakit_odeme:,.2f} TL",
            "Banka/ATM": f"{banka_val:,.2f} TL",
            "HESAP": f"{hesap:,.2f} TL",
            "Ödenen": f"{odenen_val:,.2f} TL",
            "Eksik/Fazla": durum_metni
        })

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

    @st.cache_data
    def get_dejavu_font():
        font_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        font_bold_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf"
        local_font, local_bold = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
        try:
            if not os.path.exists(local_font): urllib.request.urlretrieve(font_url, local_font)
            if not os.path.exists(local_bold): urllib.request.urlretrieve(font_bold_url, local_bold)
            return local_font, local_bold
        except:
            return None, None

    def generate_pdf(data_frame, sube_kasa_tutari, kops_kasa_tutari, durum_mesaji):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        
        f_path, f_bold_path = get_dejavu_font()
        font_name, font_bold = ('DejaVuSans', 'DejaVuSans-Bold') if f_path and f_bold_path else ('Helvetica', 'Helvetica-Bold')
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName=font_bold, fontSize=18, textColor=colors.HexColor('#1e3a8a'), alignment=1, spaceAfter=6)
        subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName=font_bold, fontSize=10, textColor=colors.HexColor('#d97706'), alignment=1, spaceAfter=15)
        
        elements.append(Paragraph("Günlük Personel Hesap ve Kasa Takip Raporu", title_style))
        elements.append(Paragraph(f"Şube Net Kasa: {sube_kasa_tutari:,.2f} TL  |  KOPS KASA: {kops_kasa_tutari:,.2f} TL  |  Durum: {durum_mesaji}", subtitle_style))
        elements.append(Spacer(1, 10))
        
        table_raw_data = [list(data_frame.columns)] + data_frame.values.tolist()
        cell_style_header = ParagraphStyle('HeaderStyle', fontName=font_bold, fontSize=10, textColor=colors.whitesmoke, alignment=1)
        cell_style_body = ParagraphStyle('BodyStyle', fontName=font_name, fontSize=9, textColor=colors.HexColor('#1e293b'), alignment=1)
        
        formatted_table_data = [[Paragraph(str(val), cell_style_header if r == 0 else cell_style_body) for val in row] for r, row in enumerate(table_raw_data)]
        t = Table(formatted_table_data, colWidths=[150, 95, 95, 85, 85, 85, 115])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    durum_str = f"AÇIK ({abs(kasa_fark):,.2f} TL)" if kasa_fark < 0 else (f"FAZLA ({kasa_fark:,.2f} TL)" if kasa_fark > 0 else "TAMAM")
    pdf_bytes = generate_pdf(summary_df, sube_net_val, kops_val, durum_str)

    st.download_button(
        label="📥 Hesap Özetini ve Kasayı PDF Olarak İndir",
        data=pdf_bytes,
        file_name='gunluk_hesap_ozeti.pdf',
        mime='application/pdf',
    )
