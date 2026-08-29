import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Personel Ödeme ve Mutabakat Paneli")

# Mevcut örnek veri seti (Kendi veri kaynağınızla değiştirebilirsiniz)
data = {
    "Personel": [
        "EMRECAN KEÇE", "BERKAY SAKİN", "ALATTİN CEBECİ", "BURCU DÜREN",
        "AHMET BERKAN ÖKSÜZ", "CELAL ŞENOL", "MEHMET KAYMAZ", "SUAT ARI", "SERGEN GÖRÜROĞLU"
    ],
    "Nakit Ft. Top": [0.0, 1149.0, 0.0, 0.0, 0.0, 1800.0, 1150.0, 0.0, 0.0],
    "Nakit Ödeme Tutarı Topl.": [157.10, 852.12, 0.0, 496.19, 995.74, 981.95, 2094.10, 248.57, 0.0],
    "Banka/ATM": [0.0, 0.0, 0.0, 500.0, 1000.0, 2900.0, 0.0, 0.0, 0.0],
    "Ödenen": [157.00, 2000.00, 0.0, 496.19, 0.0, 2781.95, 3244.00, 250.00, 0.0]
}

df = pd.DataFrame(data)

# HESAP kolonunu otomatik topluyoruz (veya isterseniz bunu da düzenlenebilir yapabilirsiniz)
df["HESAP"] = df["Nakit Ft. Top"] + df["Nakit Ödeme Tutarı Topl."] + df["Banka/ATM"]

st.markdown("### 📝 Personel İşlem Tablosu (Düzenlenebilir)")
st.info("Tablodaki herhangi bir hücreye çift tıklayarak değerleri değiştirebilir, anında güncellenmesini sağlayabilirsiniz.")

# st.data_editor ile tablomuzu interaktif ve düzenlenebilir hale getiriyoruz
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Personel": st.column_config.TextColumn("Personel", disabled=False),
        "Nakit Ft. Top": st.column_config.NumberColumn("Nakit Ft. Top", format="%.2f TL"),
        "Nakit Ödeme Tutarı Topl.": st.column_config.NumberColumn("Nakit Ödeme Tutarı Topl.", format="%.2f TL"),
        "Banka/ATM": st.column_config.NumberColumn("Banka/ATM", format="%.2f TL"),
        "HESAP": st.column_config.NumberColumn("HESAP", format="%.2f TL", disabled=True), # HESAP otomatik hesaplandığı için kilitli kalabilir
        "Ödenen": st.column_config.NumberColumn("Ödenen", format="%.2f TL"),
    },
    hide_index=False,
    key="personel_editor"
)

# Düzenlenen tablodaki verilere göre HESAP ve Eksik/Fazla sütununu dinamik olarak yeniden hesapla
edited_df["HESAP"] = edited_df["Nakit Ft. Top"] + edited_df["Nakit Ödeme Tutarı Topl."] + edited_df["Banka/ATM"]

def hesapla_durum(row):
    fark = row["Ödenen"] - row["HESAP"]
    if abs(fark) < 0.01:
        return "Tamam"
    elif fark < 0:
        return f"Eksik: {fark:.2f} TL"
    else:
        return f"Fazla: +{fark:.2f} TL"

edited_df["Eksik/Fazla"] = edited_df.apply(hesapla_durum, axis=1)

st.markdown("### 📊 Güncel Sonuçlar ve Durum")
st.dataframe(
    edited_df[["Personel", "Nakit Ft. Top", "Nakit Ödeme Tutarı Topl.", "Banka/ATM", "HESAP", "Ödenen", "Eksik/Fazla"]], 
    use_container_width=True
)
