import streamlit as st
import pandas as pd

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

    /* Personel Kartları Tasarımı */
    .person-card {
        background: linear-gradient(145deg, #1e3a8a, #172554);
        border: 2px solid #ff7b00;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(255, 123, 0, 0.25);
        margin-bottom: 8px;
    }
    .person-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ffffff;
        margin-top: 8px;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
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
    .stNumberInput label, .stMetric label {
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
    st.info("💡 Bilgi: Kendi 'HESAP' Excel dosyanızı yüklemediğiniz sürece örnek veriler gösterilmektedir. Excel dosyanızda **'Personel'**, **'Nakit Ft. Tutarı Top'** ve **'Nakit Ödeme Tutarı Topl.'** sütunları yer almalıdır.")

# Gerekli sütun kontrolü
required_cols = ["Personel", "Nakit Ft. Tutarı Top", "Nakit Ödeme Tutarı Topl."]
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Yüklenen Excel dosyasında eksik sütunlar var: {missing_cols}")
    st.stop()

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
            
            with cols[j]:
                st.markdown(f"""
                <div class="person-card">
                    <div style="color: #ff7b00; font-size: 0.8rem; font-weight: bold; margin-bottom: 3px;">✔ İşlem Tamam</div>
                    <div class="person-name">{person_name}</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"⚙️ {person_name} - İşlem", expanded=False):
                    st.write(f"**Nakit Ft. Top:** {nakit_ft:,.2f} TL")
                    st.write(f"**Nakit Ödeme Top:** {nakit_odeme:,.2f} TL")
                    
                    # 1. Banka/ATM Manüel Giriş (Etiket beyaz)
                    banka_atm = st.number_input("Banka / ATM Tutarı", min_value=0.0, value=0.0, step=10.0, key=banka_key)
                    
                    # Hesaplama: Nakit Ft. Tutarı Top + Nakit Ödeme Tutarı Topl. - BANKA/ATM
                    hesap_tutar = nakit_ft + nakit_odeme - banka_atm
                    
                    # HESAP (Net) gösterimi (Etiket beyaz)
                    st.metric(label="HESAP (Net)", value=f"{hesap_tutar:,.2f} TL")
                    
                    # 2. Ödenen Manüel Giriş (Etiket beyaz)
                    odenen_tutar = st.number_input("Ödenen (Alınan/Verilen)", min_value=0.0, value=hesap_tutar, step=10.0, key=odenen_key)
                    
                    # Mantık: Ödenen - HESAP (Net)
                    # Ödenen > HESAP ise -> Fazla (Para üstü)
                    # HESAP > Ödenen ise -> Eksik (Tahsil edilmeli)
                    fark = odenen_tutar - hesap_tutar
                    
                    if fark > 0:
                        st.markdown(f"<span style='color: #00ff66; font-weight: bold; font-size: 1.1rem;'>💵 Eksik/Fazla (Fazla/Üstü): {abs(fark):,.2f} TL</span>", unsafe_allow_html=True)
                    elif fark < 0:
                        st.markdown(f"<span style='color: #ff3333; font-weight: bold; font-size: 1.1rem;'>⚠️ Eksik/Fazla (Eksik): {abs(fark):,.2f} TL</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #00ff66; font-weight: bold; font-size: 1.1rem;'>✅ Eksik/Fazla: 0.00 TL (Tamam)</span>", unsafe_allow_html=True)

# Alt Özet Tablosu ve İndirme Butonu
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
        "Nakit Ft. Top": nakit_ft,
        "Nakit Ödeme Top": nakit_odeme,
        "Banka / ATM": banka_val,
        "HESAP": hesap,
        "Ödenen": odenen_val,
        "Eksik/Fazla": durum_metni
    })

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df.style.format({
    "Nakit Ft. Top": "{:,.2f} TL",
    "Nakit Ödeme Top": "{:,.2f} TL",
    "Banka / ATM": "{:,.2f} TL",
    "HESAP": "{:,.2f} TL",
    "Ödenen": "{:,.2f} TL"
}), use_container_width=True)

csv = summary_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Hesap Özetini CSV Olarak İndir",
    data=csv,
    file_name='gunluk_hesap_ozeti.csv',
    mime='text/csv',
)
