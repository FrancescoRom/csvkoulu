import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


df = pd.read_csv("2019nopeustestit.csv", sep=",")

# sarakkeiden uudelleennimeäminen helpommin käsiteltäväksi
df.rename(columns={
    "Aika": "Aika",
    "Alue": "Alue",
    "Kaupunki": "Kaupunki",
    "Latausnopeus (Kbps)": "DL_kbps",
    "Lähetysnopeus (Kbps)": "UL_kbps",
    "Viive (ms)": "Viive_ms",
    "jitter": "Jitter_ms"
}, inplace=True)

# muutos mbps, helpompi lukea
df["DL_Mbps"] = pd.to_numeric(df["DL_kbps"], errors="coerce") / 1000
df["UL_Mbps"] = pd.to_numeric(df["UL_kbps"], errors="coerce") / 1000
df["Viive_ms"] = pd.to_numeric(df["Viive_ms"], errors="coerce")
df["Jitter_ms"] = pd.to_numeric(df["Jitter_ms"], errors="coerce")

# yritetään parsia päivämäärä, ei kaadeta sovellusta jos ei onnistu
df["Aika"] = pd.to_datetime(df["Aika"], errors="coerce")


st.title("Ooklan mittaamat nettinopeudet 2019")

st.write("**Ensimmäiset rivit**")
st.dataframe(df.head())

st.write("---")

st.write("Datan kuvailua")
st.dataframe(df.select_dtypes(include="number").describe().T)

st.write("---")

# PERUSMITTARIT
st.write("**Kokonaiskuva (mediaanit):**")
dl_med = round(df["DL_Mbps"].median(), 2)
ul_med = round(df["UL_Mbps"].median(), 2)
lat_med = round(df["Viive_ms"].median(), 2)
st.write("Median DL (Mbps):", dl_med, " | Median UL (Mbps):", ul_med, " | Median viive (ms):", lat_med)

# SUODATUS
st.write("---")
st.write("### Suodatus")

# valitse alue
alueet = ["(Kaikki)"] + sorted(df["Alue"].dropna().unique().tolist())
valittu_alue = st.selectbox("Valitse alue:", alueet)

df_filt = df.copy()
if valittu_alue != "(Kaikki)":
    df_filt = df_filt[df_filt["Alue"] == valittu_alue]

# valitse kaupunki (suodatetun alueen sisällä)
kaupungit = ["(Kaikki)"] + sorted(df_filt["Kaupunki"].dropna().unique().tolist())
valittu_kaupunki = st.selectbox("Valitse kaupunki", kaupungit)

if valittu_kaupunki != "(Kaikki)":
    df_filt = df_filt[df_filt["Kaupunki"] == valittu_kaupunki]

st.write("Rivejä suodatettuna:", len(df_filt))

# GRAAFIT
st.write("---")
st.write("### Graafit")

# histogrammi
st.write("**Histogrammi: Latausnopeus (Mbps)**")
fig1 = plt.figure()
plt.hist(df_filt["DL_Mbps"].dropna(), bins=30, color="orange")
plt.xlabel("DL (Mbps)")
plt.ylabel("Lukumäärä")
st.pyplot(fig1)

# top 10 kaupungit mediaani DLn mukaan, suodatuksen jälkeen
st.write("**Top-10 kaupungit mediaami DL (Mbps)**")
if "Kaupunki" in df_filt.columns and df_filt["Kaupunki"].notna().any():
    kaupunki_med = (
        df_filt.groupby("Kaupunki")["DL_Mbps"]
        .median()
        .sort_values(ascending=False)
        .head(10)
    )
    fig2 = plt.figure()
    plt.bar(kaupunki_med.index, kaupunki_med.values, color="green")
    plt.xticks(rotation=90, fontsize=8)
    plt.ylabel("Mediaani DL (Mbps)")
    st.pyplot(fig2)

# aikasarja, kuukausittainen mediaani DL
st.write("**Aikasarja: kuukausittainen mediaani DL (Mbps)**")
if pd.api.types.is_datetime64_any_dtype(df_filt["Aika"]):
    ts = (
        df_filt.dropna(subset=["Aika", "DL_Mbps"])
        .set_index("Aika")["DL_Mbps"]
        .resample("ME")
        .median()
    )
    if not ts.empty:
        fig3 = plt.figure()
        plt.plot(ts.index, ts.values, label="Median DL/kk", color="blue")
        plt.scatter(ts.index, ts.values, color="black")
        plt.xticks(rotation=90, fontsize=6)
        plt.xlabel("Kuukausi")
        plt.ylabel("DL (Mbps)")
        st.pyplot(fig3)
    else:
        st.write("Ei aikasarjaa muodostettavaksi (puuttuvia arvoja?).")