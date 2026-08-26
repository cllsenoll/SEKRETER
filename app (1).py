import streamlit as st
import pandas as pd
import io
import urllib.parse
import os
import matplotlib
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
    /* Ana Ekran Arka Planı (Canlı Mavi Gradyan) */
    .stApp {
        background: linear-gradient(135deg, #102a43 0%, #243b55 50%, #1f4068 100%);
        color: #ffffff;
    }
    
    /* Sol Kenar Çubuğu (Sidebar) Arka Planı */
    [data-testid="stSidebar"] {
        background-color: #1a365d;
        border-right: 2px solid #ff7b00;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #ffffff !important;
    }

    /* SADECE Excel Yükleme Kutusu (Dropzone) Turuncu Renk Tonunda */
    [data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(135deg, #ff7b00 0%, #d97706 100%) !important;
        border: 2px dashed #ffffff !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #ffffff !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #ffffff !important;
        color: #d97706 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }

    /* Personel Kartları Tasarımı */
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

    /* Genel Kasa Paneli Tasarımı */
    .kasa-panel {
        background: linear-gradient(145deg, #1e3a8a, #0f172a);
        border: 2px solid #ff7b00;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 6px 20px rgba(255, 123, 0, 0.25);
        margin-top: 15px;
        margin-bottom: 25px;
    }

    /* Expander ve Kutuların Görünümü */
    .streamlit-expanderHeader {
        background-color: #1e3a8a !important;
        color: #ff7b00 !important;
        border: 1px solid #ff7b00 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    /* Input ve Widget Etiketlerini Beyaz Yapma */
    .stNumberInput label, .stMetric label, .stTextInput label {
        color: #ffffff !important;
    }

    /* Başlıklar */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    /* Turuncu Vurgulu Butonlar */
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

    /* Metrik Değeri */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Kenar Çubuğu (Sidebar)
with st.sidebar:
    st.image("https://img.icons8.com/color/96/money-bag.png", width=60)
    st.markdown("### F4 / HESAP")
    st.markdown("**Görükle Acente**")
    st.markdown("---")
    
    st.markdown("👤 **Aktif Kullanıcı**")
    st.info("CELAL ŞENOL (Şube Şefi)")
    
    st.markdown("---")
    st.markdown("⚙️ **GitHub Ayarları**")
    github_user = st.text_input("GitHub Kullanıcı Adınız", value="KULLANICI_ADINIZ", help="GitHub deponuzun bulunduğu kullanıcı adını buraya yazın.")
    
    st.markdown("---")
    st.markdown("📂 **Rapor / Liste Yükle**")
    uploaded_file = st.file_uploader("HESAP Excel Dosyasını Yükle", type=["xlsx", "xls", "csv"])
    
    st.markdown("---")
    st.button("💰 HESAP", use_container_width=True, type="primary")

# Ana Başlık
st.markdown("# 💰 Günlük Personel Hesap ve Kasa Takibi")
st.markdown("#### Personel Durum Kartları")
st.markdown("---")

# Varsayılan Örnek Veri
@st.cache_data
def load_sample_data():
    data = {
        "Personel": [
            "HATİCE KÜBRA IŞIK", "EMRECAN KEÇE", "BERKAY SAKİN", "ALATTİN CEBECİ",
            "BURCU DÜREN", "AHMET BERKAN ÖKSÜZ", "CELAL ŞENOL", "MEHMET KAYMAZ"
        ],
        "Nakit Ft. Tutarı Top": [4500.00, 4000.00, 2000.00, 0.00, 1200.00, 200.00, 0.00, 250.00],
        "Nakit Ödeme Tutarı Topl.": [1443.23, 1535.38, 877.45, 0.00, 378.54, 39.81, 0.00, 29.97]
    }
    return pd.DataFrame(data)

# Dosya yükleme kontrolü
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("Excel dosyası başarıyla yüklendi!")
    except Exception as e:
        st.sidebar.error(f"Dosya okuma hatası: {e}")
        df = load_sample_data()
else:
    df = load_sample_data()
    st.info("💡 Bilgi: Kendi 'HESAP' Excel dosyanızı yüklemediğiniz sürece örnek veriler gösterilmektedir.")

# Gerekli sütun kontrolü
required_cols = ["Personel", "Nakit Ft. Tutarı Top", "Nakit Ödeme Tutarı Topl."]
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Yüklenen Excel dosyasında eksik sütunlar var: {missing_cols}")
    st.stop()

def get_profile_image_url(person_name, g_user):
    clean_name = person_name.strip()
    encoded_name = urllib.parse.quote(f"{clean_name}.png")
    return f"https://raw.githubusercontent.com/{g_user}/SEKRETER/main/{encoded_name}"

DEFAULT_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# 4'lü Kolon yapısıyla kartları listeleme
cols_per_row = 4
for i in range(0, len(df), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        idx = i + j
        if idx < len(df):
            row = df.iloc[idx]
            person_name = row["Personel"]
            nakit_ft = float(row["Nakit Ft. Tutarı Top"])
            nakit_odeme = float(row["Nakit Ödeme Tutarı Topl."])
            
            banka_key = f"banka_{idx}"
            odenen_key = f"odenen_{idx}"
            completed_key = f"completed_{idx}"
            
            with cols[j]:
                temp_banka = st.session_state.get(banka_key, 0.0)
                hesap_tutar = nakit_ft + nakit_odeme - temp_banka
                
                is_completed = st.session_state.get(completed_key, False)
                if is_completed:
                    status_html = '<div style="color: #00ff88; font-size: 0.75rem; font-weight: bold; margin-bottom: 2px;">✔ İşlem Tamam</div>'
                else:
                    status_html = '<div style="color: transparent; font-size: 0.75rem; margin-bottom: 2px;">&nbsp;</div>'

                avatar_url = get_profile_image_url(person_name, github_user)

                st.markdown(f"""
                <div class="person-card">
                    {status_html}
                    <div class="card-content">
                        <img src="{avatar_url}" onerror="this.onerror=null; this.src='{DEFAULT_AVATAR}';" class="profile-img">
                        <div class="person-info">
                            <div class="person-name">{person_name}</div>
                            <div class="person-net-tutar">{hesap_tutar:,.2f} TL</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"⚙️ {person_name} - İşlem", expanded=False):
                    st.write(f"**Nakit Ft. Top:** {nakit_ft:,.2f} TL")
                    st.write(f"**Nakit Ödeme Top:** {nakit_odeme:,.2f} TL")
                    
                    banka_atm = st.number_input("Banka / ATM Tutarı", min_value=0.0, value=0.0, step=10.0, key=banka_key)
                    
                    hesap_tutar = nakit_ft + nakit_odeme - banka_atm
                    st.metric(label="HESAP (Net)", value=f"{hesap_tutar:,.2f} TL")
                    
                    def mark_completed(k=completed_key):
                        st.session_state[k] = True

                    if odenen_key not in st.session_state:
                        st.session_state[odenen_key] = hesap_tutar

                    odenen_tutar = st.number_input(
                        "Ödenen (Alınan/Verilen)", 
                        min_value=0.0, 
                        value=st.session_state[odenen_key], 
                        step=10.0, 
                        key=odenen_key,
                        on_change=mark_completed
                    )
                    
                    if st.session_state.get(odenen_key) != hesap_tutar:
                        st.session_state[completed_key] = True

                    fark = odenen_tutar - hesap_tutar
                    
                    if fark > 0:
                        st.markdown(f"<span style='color: #00ff66; font-weight: bold; font-size: 1.05rem;'>💵 Eksik/Fazla (Fazla/Üstü): {abs(fark):,.2f} TL</span>", unsafe_allow_html=True)
                    elif fark < 0:
                        st.markdown(f"<span style='color: #ff3333; font-weight: bold; font-size: 1.05rem;'>⚠️ Eksik/Fazla (Eksik): {abs(fark):,.2f} TL</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #00ff66; font-weight: bold; font-size: 1.05rem;'>✅ Eksik/Fazla: 0.00 TL (Tamam)</span>", unsafe_allow_html=True)

# --- GENEL KASA & PARA SAYMA ALANI ---
st.markdown("---")
st.markdown("### 💵 Genel Şube Kasası / Para Sayma Paneli")
st.markdown("Tüm şubenin toplam nakit kasasını saymak için banknot adetlerini giriniz.")

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(f"📊 Toplam Sayılan Banknot: **{toplam_sayilan_kasa:,.2f} TL**")
    
    if "genel_net_kasa" not in st.session_state:
        st.session_state["genel_net_kasa"] = float(toplam_sayilan_kasa)
    else:
        st.session_state["genel_net_kasa"] = float(toplam_sayilan_kasa)

    # İki kutucuk eşit boyutta ve daha küçük görünüm için yan yana kolonlar
    st.markdown("<br>", unsafe_allow_html=True)
    k_col1, k_col2 = st.columns(2)
    
    with k_col1:
        net_kasa_giris = st.number_input(
            "📥 Şube Net Kasa Değeri", 
            min_value=0.0, 
            value=st.session_state["genel_net_kasa"], 
            step=10.0, 
            key="genel_net_kasa"
        )
        
    with k_col2:
        kops_kasa_giris = st.number_input(
            "📥 KOPS KASA", 
            min_value=0.0, 
            value=st.session_state.get("genel_kops_kasa", 0.0), 
            step=10.0, 
            key="genel_kops_kasa"
        )

    st.markdown('</div>', unsafe_allow_html=True)

sube_net_val = st.session_state.get('genel_net_kasa', 0.0)
kops_val = st.session_state.get('genel_kops_kasa', 0.0)
kasa_fark = sube_net_val - kops_val

st.markdown("---")
st.markdown("### 📊 Genel Hesap Özeti Tablosu")

summary_data = []
for idx, row in df.iterrows():
    person_name = row["Personel"]
    nakit_ft = float(row["Nakit Ft. Tutarı Top"])
    nakit_odeme = float(row["Nakit Ödeme Tutarı Topl."])
    
    banka_val = st.session_state.get(f"banka_{idx}", 0.0)
    hesap = nakit_ft + nakit_odeme - banka_val
    odenen_val = st.session_state.get(f"odenen_{idx}", hesap)
    fark_val = odenen_val - hesap
    
    if fark_val > 0:
        durum_metni = f"Fazla: +{fark_val:,.2f} TL"
    elif fark_val < 0:
        durum_metni = f"Eksik: {fark_val:,.2f} TL"
    else:
        durum_metni = "Tamam (0.00 TL)"
    
    summary_data.append({
        "Personel": person_name,
        "Nakit Ft. Top": f"{nakit_ft:,.2f} TL",
        "Nakit Ödeme Top": f"{nakit_odeme:,.2f} TL",
        "Banka / ATM": f"{banka_val:,.2f} TL",
        "HESAP": f"{hesap:,.2f} TL",
        "Ödenen": f"{odenen_val:,.2f} TL",
        "Eksik/Fazla": durum_metni
    })

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True)

col_ozet1, col_ozet2 = st.columns(2)
with col_ozet1:
    st.markdown(f"### 🏦 Şube Net Kasa: **{sube_net_val:,.2f} TL**")
with col_ozet2:
    st.markdown(f"### 💳 KOPS KASA: **{kops_val:,.2f} TL**")

if kasa_fark < 0:
    st.markdown(f"<div style='background-color: rgba(255, 51, 51, 0.2); border: 2px solid #ff3333; padding: 12px; border-radius: 8px; text-align: center; font-size: 1.1rem; font-weight: bold; color: #ff6b6b; margin-top: 10px;'>⚠️ Kasa Durumu: AÇIK ({abs(kasa_fark):,.2f} TL Eksik)</div>", unsafe_allow_html=True)
elif kasa_fark > 0:
    st.markdown(f"<div style='background-color: rgba(0, 255, 136, 0.2); border: 2px solid #00ff88; padding: 12px; border-radius: 8px; text-align: center; font-size: 1.1rem; font-weight: bold; color: #00ff88; margin-top: 10px;'>💵 Kasa Durumu: FAZLA ({kasa_fark:,.2f} TL Fazla)</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div style='background-color: rgba(0, 255, 136, 0.2); border: 2px solid #00ff88; padding: 12px; border-radius: 8px; text-align: center; font-size: 1.1rem; font-weight: bold; color: #00ff88; margin-top: 10px;'>✅ Kasa Durumu: TAMAM (Fark Yok)</div>", unsafe_allow_html=True)

# Matplotlib içindeki yerleşik DejaVu fontlarını kullanarak Türkçe karakter hatasını kesin olarak çözen PDF fonksiyonu
def generate_pdf(data_frame, sube_kasa_tutari, kops_kasa_tutari, durum_mesaji):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    # Matplotlib veri dizininden DejaVuSans ttf dosyalarını güvenle alıyoruz
    mpl_data_path = matplotlib.get_data_path()
    font_path = os.path.join(mpl_data_path, 'fonts', 'ttf', 'DejaVuSans.ttf')
    font_bold_path = os.path.join(mpl_data_path, 'fonts', 'ttf', 'DejaVuSans-Bold.ttf')
    
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))
        font_name = 'DejaVuSans'
        font_bold = 'DejaVuSans-Bold'
    except Exception:
        font_name = 'Helvetica'
        font_bold = 'Helvetica-Bold'
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10,
        textColor=colors.HexColor('#d97706'),
        alignment=1,
        spaceAfter=15
    )
    
    elements.append(Paragraph("Günlük Personel Hesap ve Kasa Takip Raporu", title_style))
    elements.append(Paragraph(f"Şube Net Kasa: {sube_kasa_tutari:,.2f} TL  |  KOPS KASA: {kops_kasa_tutari:,.2f} TL  |  Durum: {durum_mesaji}", subtitle_style))
    elements.append(Spacer(1, 10))
    
    table_data = [list(data_frame.columns)] + data_frame.values.tolist()
    
    t = Table(table_data, colWidths=[150, 95, 95, 85, 85, 85, 115])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

if kasa_fark < 0:
    durum_str = f"AÇIK ({abs(kasa_fark):,.2f} TL)"
elif kasa_fark > 0:
    durum_str = f"FAZLA ({kasa_fark:,.2f} TL)"
else:
    durum_str = "TAMAM"

pdf_bytes = generate_pdf(summary_df, sube_net_val, kops_val, durum_str)

st.download_button(
    label="📥 Hesap Özetini ve Kasayı PDF Olarak İndir",
    data=pdf_bytes,
    file_name='gunluk_hesap_ozeti.pdf',
    mime='application/pdf',
)
