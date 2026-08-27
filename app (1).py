import streamlit as st
import pandas as pd
import io
import urllib.parse
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Sayfa yapılandırması
st.set_page_config(
    page_title="Günlük Personel Hesap ve Kasa Takibi",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gelişmiş Canlı Mavi ve Turuncu Tema CSS Kodları
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #102a43 0%, #243b55 50%, #1f4068 100%);
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #1a365d;
        border-right: 2px solid #ff7b00;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #ffffff !important;
    }
    .person-card {
        background: linear-gradient(145deg, #1e3a8a, #172554);
        border: 2px solid #ff7b00;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(255, 123, 0, 0.25);
        margin-bottom: 8px;
    }
    .card-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-top: 6px;
    }
    .profile-img {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ff7b00;
        background-color: #1a365d;
        flex-shrink: 0;
    }
    .person-info {
        text-align: left;
    }
    .person-name {
        font-size: 0.90rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 2px;
        letter-spacing: 0.3px;
    }
    .person-net-tutar {
        font-size: 1.1rem;
        font-weight: bold;
        color: #00ff88;
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
    .streamlit-expanderHeader {
        background-color: #1e3a8a !important;
        color: #ff7b00 !important;
        border: 1px solid #ff7b00 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
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
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Kenar Çubuğu
with st.sidebar:
    st.image("https://img.icons8.com/color/96/money-bag.png", width=60)
    st.markdown("### F4 / HESAP")
    st.markdown("**Görükle Acente**")
    st.markdown("---")
    
    st.markdown("👤 **Aktif Kullanıcı**")
    st.info("CELAL ŞENOL (Şube Şefi)")
    
    st.markdown("---")
    st.markdown("📂 **Rapor / Liste Yükle**")
    uploaded_file = st.file_uploader("HESAP Dosyasını Yükle (Excel veya CSV)", type=["xlsx", "xls", "csv"])
    
    st.markdown("---")
    st.button("💰 HESAP", use_container_width=True, type="primary")

# Ana Başlık
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
                col_clean = col.lower().replace('i', 'i').replace('ı', 'i')
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

    # --- KUSURSUZ BAŞ HARF AVATAR ÇÖZÜCÜ ---
    def get_profile_image_url(person_name):
        # Kişinin adından otomatik olarak şık, kurumsal renkli baş harf rozeti üretir (Hiçbir kırık resim hatası vermez)
        return f"https://ui-avatars.com/api/?name={urllib.parse.quote(person_name)}&background=1e3a8a&color=ff7b00&bold=true&size=128"

    cols_per_row = 4
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
                    
                    is_completed = st.session_state.get(completed_key, False)
                    status_html = '<div style="color: #00ff88; font-size: 0.75rem; font-weight: bold; margin-bottom: 2px;">✔ İşlem Tamam</div>' if is_completed else '<div style="color: transparent; font-size: 0.75rem; margin-bottom: 2px;">&nbsp;</div>'

                    avatar_url = get_profile_image_url(person_name)

                    st.markdown(f"""
                    <div class="person-card">
                        {status_html}
                        <div class="card-content">
                            <img src="{avatar_url}" class="profile-img">
                            <div class="person-info">
                                <div class="person-name">{person_name}</div>
                                <div class="person-net-tutar">{hesap_tutar:,.2f} TL</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"⚙️ {person_name} - İşlem", expanded=False):
                        st.write(f"**Nakit Ft. Top:** {nakit_ft:,.2f} TL")
                        st.write(f"**Nakit Ödeme Tutarı Topl.:** {nakit_odeme:,.2f} TL")
                        
                        banka_atm = st.number_input("Banka/ATM Tutarı", min_value=0.0, value=0.0, step=10.0, key=banka_key)
                        hesap_tutar = nakit_ft + nakit_odeme - banka_atm
                        st.metric(label="HESAP (Net)", value=f"{hesap_tutar:,.2f} TL")
                        
                        def mark_completed(k=completed_key):
                            st.session_state[k] = True

                        if odenen_key not in st.session_state:
                            st.session_state[odenen_key] = hesap_tutar

                        odenen_tutar = st.number_input(
                            "Ödenen (Alınan/Verilen)", 
                            min_value=0.0, 
                            value=float(st.session_state[odenen_key]), 
                            step=10.0, 
                            key=odenen_key,
                            on_change=mark_completed
                        )
                        
                        if st.session_state.get(odenen_key) != hesap_tutar:
                            st.session_state[completed_key] = True

                        fark = odenen_tutar - hesap_tutar
                        if fark > 0:
                            st.markdown(f"<span style='color: #00ff66; font-weight: bold;'>✅ Fazla ({abs(fark):,.2f} TL)</span>", unsafe_allow_html=True)
                        elif fark < 0:
                            st.markdown(f"<span style='color: #ff3333; font-weight: bold;'>✅ Eksik ({abs(fark):,.2f} TL)</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("<span style='color: #00ff66; font-weight: bold;'>✅ Tamam (0.00 TL)</span>", unsafe_allow_html=True)

    # --- GENEL KASA & PARA SAYMA ALANI ---
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
        k_col1, k_col2 = st.columns(2)
        with k_col1:
            net_kasa_giris = st.number_input("📥 Şube Net Kasa Değeri", min_value=0.0, value=float(st.session_state["genel_net_kasa"]), step=10.0, key="genel_net_kasa")
        with k_col2:
            kops_kasa_giris = st.number_input("📥 KOPS KASA", min_value=0.0, value=float(st.session_state.get("genel_kops_kasa", 0.0)), step=10.0, key="genel_kops_kasa")
        st.markdown('</div>', unsafe_allow_html=True)

    sube_net_val = float(st.session_state.get('genel_net_kasa', 0.0))
    kops_val = float(st.session_state.get('genel_kops_kasa', 0.0))
    kasa_fark = sube_net_val - kops_val

    # --- KASA ÖZETİ VE TABLO ---
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

    # --- PDF ÇIKTISI ---
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
